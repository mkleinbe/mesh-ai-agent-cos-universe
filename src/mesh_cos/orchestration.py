from __future__ import annotations

from collections.abc import Callable

from .audit import AuditEvent
from .ledger import TaskLedger
from .lifecycle import transition
from .models import AuthorityLevel, TaskRecord, TaskStatus, new_id


class ChiefOfStaffService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def intake(self, objective: str, expected_outcome: str, requested_by: str, executive_sponsor: str,
               accountable_agent: str, decision_owner: str, authority_level: AuthorityLevel,
               acceptance_test: str) -> TaskRecord:
        task = TaskRecord(
            task_id=new_id("task"), objective=objective, expected_outcome=expected_outcome,
            requested_by=requested_by, executive_sponsor=executive_sponsor,
            accountable_agent=accountable_agent, decision_owner=decision_owner,
            authority_level=authority_level, acceptance_test=acceptance_test,
        )
        self.ledger.save_task(task)
        self._audit(task, "task_intake", "created")
        return task

    def advance(self, task_id: str, target: TaskStatus) -> TaskRecord:
        task = self._require(task_id)
        before = task.status.value
        transition(task, target)
        self.ledger.save_task(task)
        self._audit(task, "task_transition", f"{before}->{target.value}")
        return task

    def complete(self, task_id: str, *, outcome: str, evidence: list[str]) -> TaskRecord:
        task = self._require(task_id)
        task.outcome = outcome
        task.outcome_evidence = list(evidence)
        transition(task, TaskStatus.COMPLETED)
        self.ledger.save_task(task)
        self._audit(task, "task_complete", "completed")
        return task

    def verify(self, task_id: str, acceptance: Callable[[TaskRecord], tuple[bool, str]]) -> TaskRecord:
        task = self._require(task_id)
        passed, reason = acceptance(task)
        record = {
            "task_id": task.task_id,
            "acceptance_test": task.acceptance_test,
            "passed": bool(passed),
            "reason": reason,
            "evidence": list(task.outcome_evidence),
        }
        self.ledger.save_record("verification", task.task_id, record)
        transition(task, TaskStatus.VERIFIED if passed else TaskStatus.REWORK)
        self.ledger.save_task(task)
        self._audit(task, "task_verify", "passed" if passed else "failed")
        return task

    def _require(self, task_id: str) -> TaskRecord:
        task = self.ledger.get_task(task_id)
        if not task:
            raise KeyError(task_id)
        return task

    def _audit(self, task: TaskRecord, event_type: str, result: str) -> None:
        event = AuditEvent(event_type, "cos", task.task_id, task.correlation_id, int(task.authority_level), result)
        self.ledger.record_event(event.to_dict())
