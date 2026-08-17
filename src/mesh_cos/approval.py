from __future__ import annotations

from dataclasses import dataclass
from .models import AuthorityLevel, new_id, utcnow

@dataclass(slots=True)
class Approval:
    approval_id: str
    task_id: str
    requested_by: str
    approval_owner: str
    authority_level: AuthorityLevel
    action: str
    status: str = "PENDING"
    requested_at: str = ""
    decided_at: str | None = None
    decision_reason: str | None = None


def request_approval(task_id: str, requested_by: str, approval_owner: str, authority_level: AuthorityLevel, action: str) -> Approval:
    return Approval(new_id("approval"), task_id, requested_by, approval_owner, authority_level, action, requested_at=utcnow())


def decide(approval: Approval, *, actor: str, approved: bool, reason: str) -> Approval:
    if actor != approval.approval_owner:
        raise PermissionError("Only the configured approval owner may decide")
    if approval.status != "PENDING":
        raise ValueError("Approval already decided")
    approval.status = "APPROVED" if approved else "REJECTED"
    approval.decided_at = utcnow()
    approval.decision_reason = reason
    return approval
