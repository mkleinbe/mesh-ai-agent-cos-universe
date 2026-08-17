from __future__ import annotations

from dataclasses import asdict, dataclass

from .audit import AuditEvent
from .ledger import TaskLedger
from .lifecycle import transition
from .models import AuthorityLevel, TaskStatus, new_id, utcnow


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

    def to_dict(self) -> dict:
        data = asdict(self)
        data["version"] = "mesh.cos.approval.v1"
        data["authority_level"] = int(self.authority_level)
        return data


def request_approval(task_id: str, requested_by: str, approval_owner: str, authority_level: AuthorityLevel, action: str) -> Approval:
    if authority_level < AuthorityLevel.L4:
        raise ValueError("Approval records are reserved for L4/L5 actions")
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


class ApprovalService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def request(self, task_id: str, requested_by: str, approval_owner: str, authority_level: AuthorityLevel, action: str) -> Approval:
        task = self._require_task(task_id)
        approval = request_approval(task_id, requested_by, approval_owner, authority_level, action)
        self.ledger.save_record("approval", approval.approval_id, approval.to_dict())
        task.approval_status = "PENDING"
        task.approval_owner = approval_owner
        if task.status in {TaskStatus.IN_PROGRESS, TaskStatus.READY_FOR_DECISION}:
            transition(task, TaskStatus.AWAITING_APPROVAL)
        self.ledger.save_task(task)
        self._audit(task, "approval_requested", approval.approval_id, approval.approval_id)
        return approval

    def decide(self, approval_id: str, *, actor: str, approved: bool, reason: str) -> Approval:
        raw = self.ledger.get_record("approval", approval_id)
        if raw is None:
            raise KeyError(approval_id)
        raw = dict(raw)
        raw.pop("version", None)
        raw["authority_level"] = AuthorityLevel(raw["authority_level"])
        approval = decide(Approval(**raw), actor=actor, approved=approved, reason=reason)
        self.ledger.save_record("approval", approval_id, approval.to_dict())
        task = self._require_task(approval.task_id)
        task.approval_status = approval.status
        if task.status == TaskStatus.AWAITING_APPROVAL:
            transition(task, TaskStatus.READY_FOR_ACTION if approved else TaskStatus.IN_PROGRESS)
        self.ledger.save_task(task)
        self._audit(task, "approval_decided", approval.status, approval.approval_id)
        return approval

    def _require_task(self, task_id: str):
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        return task

    def _audit(self, task, event_type: str, result: str, approval_reference: str) -> None:
        event = AuditEvent(event_type, "approval-service", task.task_id, task.correlation_id, int(task.authority_level), result, approval_reference=approval_reference)
        self.ledger.record_event(event.to_dict())
