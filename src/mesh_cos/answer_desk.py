from __future__ import annotations

from dataclasses import dataclass

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import new_id
from .security import authorize_source


@dataclass(frozen=True, slots=True)
class AnswerDisposition:
    disposition: str
    reason: str


def decide(
    *,
    known_fact: bool,
    source_accessible: bool,
    established_policy: bool,
    reversible: bool,
    requires_judgment: bool,
    ceo_authority: bool,
    requester_permissions: set[str],
    source_class: str = "approved",
) -> AnswerDisposition:
    if not authorize_source(requester_permissions, source_class):
        return AnswerDisposition("BLOCKED_BY_ACCESS", "Requester lacks source permission")
    if ceo_authority:
        return AnswerDisposition("ESCALATED", "CEO authority required")
    if known_fact and source_accessible:
        return AnswerDisposition("ANSWERED", "Known authorized fact")
    if established_policy and reversible:
        return AnswerDisposition("ANSWERED", "Established delegated policy")
    if requires_judgment:
        return AnswerDisposition("RECOMMENDATION_PROVIDED", "Bounded judgment required")
    return AnswerDisposition("BLOCKED_BY_EVIDENCE", "Insufficient authoritative evidence")


class AnswerDeskService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def handle(self, *, request_id: str, **kwargs) -> AnswerDisposition:
        result = decide(**kwargs)
        self.ledger.save_record(
            "answer_desk",
            request_id,
            {"request_id": request_id, "disposition": result.disposition, "reason": result.reason},
        )
        self.ledger.record_event(
            AuditEvent(
                "answer_desk_disposition",
                "answer-desk",
                request_id,
                new_id("corr"),
                2,
                result.disposition,
            ).to_dict()
        )
        return result
