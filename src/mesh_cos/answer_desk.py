from __future__ import annotations

from dataclasses import dataclass

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import new_id, utcnow
from .security import authorize_source


@dataclass(frozen=True, slots=True)
class AnswerDisposition:
    disposition: str
    reason: str
    routed_to: str | None = None


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
    functional_owner: str | None = None,
    approval_required: bool = False,
) -> AnswerDisposition:
    if not authorize_source(requester_permissions, source_class):
        return AnswerDisposition("BLOCKED_BY_ACCESS", "Requester lacks source permission")
    if ceo_authority:
        return AnswerDisposition("ESCALATED", "CEO authority required")
    if approval_required:
        return AnswerDisposition("APPROVAL_REQUIRED", "Qualified human approval required")
    if known_fact and source_accessible:
        return AnswerDisposition("ANSWERED", "Known authorized fact")
    if established_policy and reversible:
        return AnswerDisposition("ANSWERED", "Established delegated policy")
    if functional_owner:
        return AnswerDisposition("ROUTED", "Functional owner has domain authority", functional_owner)
    if requires_judgment:
        return AnswerDisposition("RECOMMENDATION_PROVIDED", "Bounded judgment required")
    return AnswerDisposition("BLOCKED_BY_EVIDENCE", "Insufficient authoritative evidence")


class AnswerDeskService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def handle(self, *, request_id: str, **kwargs) -> AnswerDisposition:
        received_at = utcnow()
        result = decide(**kwargs)
        self.ledger.save_record(
            "answer_desk",
            request_id,
            {
                "request_id": request_id,
                "disposition": result.disposition,
                "reason": result.reason,
                "routed_to": result.routed_to,
                "received_at": received_at,
                "resolved_at": utcnow(),
                "incorrect": False,
                "corrected": False,
                "access_control_failure": result.disposition == "BLOCKED_BY_ACCESS",
            },
        )
        self.ledger.record_event(
            AuditEvent("answer_desk_disposition", "answer-desk", request_id, new_id("corr"), 2, result.disposition).to_dict()
        )
        return result

    def record_correction(self, request_id: str, *, actor: str, reason: str) -> dict:
        record = self.ledger.get_record("answer_desk", request_id)
        if record is None:
            raise KeyError(request_id)
        record["incorrect"] = True
        record["corrected"] = True
        record["correction_reason"] = reason
        record["corrected_by"] = actor
        record["corrected_at"] = utcnow()
        self.ledger.save_record("answer_desk", request_id, record)
        self.ledger.record_event(AuditEvent("answer_desk_corrected", actor, request_id, new_id("corr"), 2, reason).to_dict())
        return record
