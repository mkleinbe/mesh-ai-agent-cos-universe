from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict

from .approval import decide as decide_approval_record
from .approval import request_approval
from .audit import AuditEvent
from .delegation_service import DelegationService
from .ledger import TaskLedger
from .lifecycle import transition
from .models import AuthorityLevel, Delegation, TaskRecord, TaskStatus, new_id, utcnow
from .registry import AgentRegistry
from .verification import VerificationResult


class CoSService:
    """Application service that drives a task from intake to verified closure."""

    def __init__(self, *, ledger: TaskLedger, registry: AgentRegistry) -> None:
        self.ledger = ledger
        self.registry = registry
        self.delegations = DelegationService(ledger=ledger, registry=registry)

    def _require(self, task_id: str) -> TaskRecord:
        task = self.ledger.get_task(task_id)
        if task is None:
            raise KeyError(task_id)
        return task

    def _audit(self, task: TaskRecord, event_type: str, *, before: dict | None = None, result: str = "ok", approval_reference: str | None = None, evidence: list[str] | None = None) -> None:
        event = AuditEvent(
            event_type=event_type,
            actor_agent="cos",
            task_id=task.task_id,
            correlation_id=task.correlation_id,
            authority_level=int(task.authority_level),
            result=result,
            before_state=before,
            after_state=task.to_dict(),
            approval_reference=approval_reference,
            evidence_references=evidence,
        )
        if self.ledger.record_event(event.to_dict()):
            task.audit_events.append(event.event_id)
            self.ledger.save_task(task)

    def intake(
        self,
        *,
        objective: str,
        expected_outcome: str,
        requested_by: str,
        executive_sponsor: str,
        accountable_agent: str,
        decision_owner: str,
        acceptance_test: str,
        authority_level: AuthorityLevel = AuthorityLevel.L0,
        priority: str = "P2",
        idempotency_key: str | None = None,
        **fields,
    ) -> TaskRecord:
        if idempotency_key:
            existing_id = self.ledger.task_for_intake_key(idempotency_key)
            if existing_id:
                return self._require(existing_id)
        self.registry.get(accountable_agent)
        task = TaskRecord(
            task_id=new_id("task"),
            objective=objective,
            expected_outcome=expected_outcome,
            requested_by=requested_by,
            executive_sponsor=executive_sponsor,
            accountable_agent=accountable_agent,
            decision_owner=decision_owner,
            acceptance_test=acceptance_test,
            authority_level=authority_level,
            priority=priority,
            **fields,
        )
        if idempotency_key and not self.ledger.register_intake_key(idempotency_key, task.task_id):
            existing_id = self.ledger.task_for_intake_key(idempotency_key)
            if existing_id:
                return self._require(existing_id)
        self.ledger.save_task(task)
        self._audit(task, "task_intake")
        return task

    def _advance(self, task_id: str, target: TaskStatus, event_type: str | None = None) -> TaskRecord:
        task = self._require(task_id)
        before = task.to_dict()
        transition(task, target)
        self.ledger.save_task(task)
        self._audit(task, event_type or f"task_{target.value.lower()}", before=before)
        return task

    def plan(self, task_id: str) -> TaskRecord:
        task = self._require(task_id)
        if task.status == TaskStatus.INTAKE:
            self._advance(task_id, TaskStatus.TRIAGED)
        task = self._require(task_id)
        if task.status == TaskStatus.TRIAGED:
            return self._advance(task_id, TaskStatus.PLANNED)
        return task

    def assign(self, task_id: str) -> TaskRecord:
        task = self._require(task_id)
        if task.status == TaskStatus.PLANNED:
            return self._advance(task_id, TaskStatus.ASSIGNED)
        return task

    def delegate(self, task_id: str, delegation: Delegation, *, depth: int = 1, ancestry: list[str] | None = None) -> Delegation:
        task = self._require(task_id)
        created = self.delegations.create(task, delegation, depth=depth, ancestry=ancestry or [delegation.delegating_agent])
        if task.status == TaskStatus.PLANNED:
            self._advance(task_id, TaskStatus.ASSIGNED, "delegation_assigned")
        task = self._require(task_id)
        self._audit(task, "delegation_created", evidence=[created.delegation_id])
        return created

    def start(self, task_id: str) -> TaskRecord:
        return self._advance(task_id, TaskStatus.IN_PROGRESS)

    def block(self, task_id: str, blocker: str) -> TaskRecord:
        task = self._require(task_id)
        task.blockers.append(blocker)
        self.ledger.save_task(task)
        return self._advance(task_id, TaskStatus.BLOCKED)

    def await_input(self, task_id: str) -> TaskRecord:
        return self._advance(task_id, TaskStatus.AWAITING_INPUT)

    def qa(self, task_id: str) -> TaskRecord:
        return self._advance(task_id, TaskStatus.QA)

    def ready_for_decision(self, task_id: str) -> TaskRecord:
        return self._advance(task_id, TaskStatus.READY_FOR_DECISION)

    def ready_for_action(self, task_id: str) -> TaskRecord:
        return self._advance(task_id, TaskStatus.READY_FOR_ACTION)

    def request_human_approval(self, task_id: str, *, requested_by: str, approval_owner: str, authority_level: AuthorityLevel, action: str):
        task = self._require(task_id)
        approval = request_approval(task_id, requested_by, approval_owner, authority_level, action)
        payload = asdict(approval)
        payload["version"] = "mesh.cos.approval.v1"
        payload["authority_level"] = int(approval.authority_level)
        self.ledger.save_approval(payload)
        task.approval_status = "PENDING"
        task.approval_owner = approval_owner
        self.ledger.save_task(task)
        if task.status in {TaskStatus.IN_PROGRESS, TaskStatus.READY_FOR_DECISION}:
            self._advance(task_id, TaskStatus.AWAITING_APPROVAL, "approval_requested")
        else:
            self._audit(task, "approval_requested", evidence=[approval.approval_id])
        return approval

    def decide_human_approval(self, approval_id: str, *, actor: str, approved: bool, reason: str):
        payload = self.ledger.get_approval(approval_id)
        if payload is None:
            raise KeyError(approval_id)
        from .approval import Approval
        raw = dict(payload)
        raw.pop("version", None)
        raw["authority_level"] = AuthorityLevel(raw["authority_level"])
        approval = Approval(**raw)
        decide_approval_record(approval, actor=actor, approved=approved, reason=reason)
        saved = asdict(approval)
        saved["version"] = "mesh.cos.approval.v1"
        saved["authority_level"] = int(approval.authority_level)
        self.ledger.save_approval(saved)
        task = self._require(approval.task_id)
        task.approval_status = approval.status
        self.ledger.save_task(task)
        self._audit(task, "approval_decided", approval_reference=approval.approval_id, result=approval.status)
        if approved and task.status == TaskStatus.AWAITING_APPROVAL:
            self._advance(task.task_id, TaskStatus.READY_FOR_ACTION)
        elif not approved and task.status == TaskStatus.AWAITING_APPROVAL:
            self._advance(task.task_id, TaskStatus.IN_PROGRESS)
        return approval

    def complete(self, task_id: str, *, outcome: str, evidence: list[str]) -> TaskRecord:
        task = self._require(task_id)
        task.outcome = outcome
        task.outcome_evidence = list(evidence)
        self.ledger.save_task(task)
        return self._advance(task_id, TaskStatus.COMPLETED, "task_completed")

    def verify(self, task_id: str, evaluator: Callable[[TaskRecord], VerificationResult]) -> TaskRecord:
        task = self._require(task_id)
        if task.status != TaskStatus.COMPLETED:
            raise ValueError("Only COMPLETED tasks may be verified")
        result = evaluator(task)
        record = {
            "verification_id": new_id("verify"),
            "task_id": task.task_id,
            "acceptance_test": task.acceptance_test,
            "passed": result.passed,
            "evidence": list(result.evidence),
            "reason": result.reason,
            "timestamp": utcnow(),
        }
        self.ledger.save_verification(record)
        task.outcome_evidence.extend(e for e in result.evidence if e not in task.outcome_evidence)
        self.ledger.save_task(task)
        if result.passed:
            return self._advance(task_id, TaskStatus.VERIFIED, "task_verified")
        return self._advance(task_id, TaskStatus.REWORK, "verification_failed")

    def close(self, task_id: str) -> TaskRecord:
        return self._advance(task_id, TaskStatus.CLOSED)

    def reassign(self, task_id: str, new_owner: str) -> TaskRecord:
        self.registry.get(new_owner)
        task = self._require(task_id)
        before = task.to_dict()
        task.accountable_agent = new_owner
        self.ledger.save_task(task)
        self._audit(task, "task_reassigned", before=before)
        return task
