from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .ledger import TaskLedger
from .models import new_id, utcnow
from .registry import AgentRegistry
from .security import authorize_source


@dataclass(frozen=True, slots=True)
class SourceResult:
    found: bool
    value: str | None = None
    source_ref: str | None = None
    source_class: str = "approved"
    owner: str | None = None


@dataclass(frozen=True, slots=True)
class AnswerDeskResponse:
    disposition: str
    answer: str | None = None
    source_ref: str | None = None
    owner: str | None = None
    reason: str = ""


class Retriever(Protocol):
    def __call__(self, question: str) -> SourceResult: ...


class AnswerDeskService:
    def __init__(self, *, registry: AgentRegistry, retriever: Retriever, ledger: TaskLedger) -> None:
        self.registry = registry
        self.registry.get("answer-desk")
        self.retriever = retriever
        self.ledger = ledger

    def _metric(self, disposition: str, *, requester: str) -> None:
        self.ledger.record_metric(
            {
                "metric_id": new_id("metric"),
                "metric_name": "answer_desk_disposition",
                "task_id": None,
                "agent_id": "answer-desk",
                "timestamp": utcnow(),
                "value": 1.0,
                "requester": requester,
                "disposition": disposition,
            }
        )

    def handle(
        self,
        question: str,
        *,
        requester: str,
        requester_permissions: set[str],
        established_policy: bool = False,
        reversible: bool = True,
        requires_judgment: bool = False,
        ceo_authority: bool = False,
    ) -> AnswerDeskResponse:
        result = self.retriever(question)
        if not authorize_source(requester_permissions, result.source_class):
            response = AnswerDeskResponse("BLOCKED_BY_ACCESS", reason="Requester lacks source permission")
        elif ceo_authority:
            response = AnswerDeskResponse("ESCALATED", owner="cos", reason="CEO authority required")
        elif result.found and not requires_judgment:
            response = AnswerDeskResponse("ANSWERED", answer=result.value, source_ref=result.source_ref, owner=result.owner, reason="Authorized evidence")
        elif established_policy and reversible and result.found:
            response = AnswerDeskResponse("ANSWERED", answer=result.value, source_ref=result.source_ref, owner=result.owner, reason="Established policy")
        elif result.found and requires_judgment:
            response = AnswerDeskResponse("RECOMMENDATION_PROVIDED", answer=result.value, source_ref=result.source_ref, owner=result.owner, reason="Bounded judgment")
        elif result.owner:
            self.registry.get(result.owner)
            response = AnswerDeskResponse("ROUTED", owner=result.owner, reason="Functional owner required")
        else:
            response = AnswerDeskResponse("BLOCKED_BY_EVIDENCE", reason="Insufficient authoritative evidence")
        self._metric(response.disposition, requester=requester)
        return response
