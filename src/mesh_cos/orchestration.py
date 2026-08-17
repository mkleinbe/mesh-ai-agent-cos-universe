from __future__ import annotations

from collections.abc import Callable

from .adapters import GovernedAdapterRegistry
from .agentops import stalled
from .audit import AuditEvent
from .ledger import TaskLedger
from .lifecycle import transition
from .models import AuthorityLevel, TaskRecord, TaskStatus, new_id, utcnow
from .reliability import assert_runtime_enabled


class ChiefOfStaffService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def intake(
        self,
        objective: str,
        expected_outcome: str,
        requested_by: str,
        executive_sponsor: str,
        accountable_agent: str,
        decision_owner: str,
        authority_level: AuthorityLevel,
        acceptance_test: str,
        idempotency_key: str | None = None,
    ) -> TaskRecord:
        assert_runtime_enabled()
        if idempotency_key:
            existing = self.ledger.get_record("intake_idempotency", idempotency_key)
            if existing:
                return self._require(existing["task_id"])
        task = TaskRecord(
            task_id=new_id("task"),
            objective=objective,
            expected_outcome=expected_outcome,
            requested_by=requested_by,
            executive_sponsor=executive_sponsor,
            accountable_agent=accountable_agent,
            decision_owner=decision_owner,
            authority_level=authority_level,
            acceptance_test=acceptance_test,
        )
        self.ledger.save_task(task)
        if idempotency_key:
            self.ledger.save_record("intake_idempotency", idempotency_key, {"task_id": task.task_id})
        self._audit(task, "task_intake", "created")
        return task

    def decompose(self, parent_task_id: str, work_packages: list[dict]) -> list[TaskRecord]:
        """Validate the complete decomposition before writing any child task.

        A malformed later work package must not leave earlier children persisted. This
        preserves canonical work-graph atomicity for deterministic validation errors.
        """

        assert_runtime_enabled()
        parent = self._require(parent_task_id)
        children: list[TaskRecord] = []
        for package in work_packages:
            child = TaskRecord(
                task_id=new_id("task"),
                objective=package["objective"],
                expected_outcome=package["expected_outcome"],
                requested_by="cos",
                executive_sponsor=parent.executive_sponsor,
                accountable_agent=package["accountable_agent"],
                decision_owner=package.get("decision_owner", parent.decision_owner),
                priority=package.get("priority", parent.priority),
                authority_level=AuthorityLevel(package.get("authority_level", int(parent.authority_level))),
                parent_task_id=parent.task_id,
                correlation_id=parent.correlation_id,
                contributors=list(package.get("contributors", [])),
                dependencies=list(package.get("dependencies", [])),
                deliverable_contract=package.get("deliverable_contract", ""),
                due_at=package.get("due_at"),
                next_check_at=package.get("next_check_at"),
                success_metrics=list(package.get("success_metrics", [])),
                acceptance_test=package["acceptance_test"],
            )
            if int(child.authority_level) > int(parent.authority_level):
                raise PermissionError("Child work package cannot widen parent authority")
            children.append(child)

        for child in children:
            self.ledger.save_task(child)
            self._audit(child, "task_decomposed", f"parent={parent.task_id}")
        self.ledger.save_record(
            "work_graph",
            parent.task_id,
            {"parent_task_id": parent.task_id, "child_task_ids": [child.task_id for child in children]},
        )
        return children

    def dependencies_ready(self, task_id: str) -> bool:
        task = self._require(task_id)
        for dependency_id in task.dependencies:
            dependency = self.ledger.get_task(dependency_id)
            if dependency is None or dependency.status not in {TaskStatus.VERIFIED, TaskStatus.CLOSED}:
                return False
        return True

    def advance(self, task_id: str, target: TaskStatus) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        if target == TaskStatus.IN_PROGRESS and not self.dependencies_ready(task_id):
            raise RuntimeError("Task dependencies are not verified")
        before = task.status.value
        transition(task, target)
        self.ledger.save_task(task)
        self._audit(task, "task_transition", f"{before}->{target.value}")
        return task

    def complete(self, task_id: str, *, outcome: str, evidence: list[str]) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        task.outcome = outcome
        task.outcome_evidence = list(evidence)
        transition(task, TaskStatus.COMPLETED)
        self.ledger.save_task(task)
        self._audit(task, "task_complete", "completed")
        return task

    def verify(self, task_id: str, acceptance: Callable[[TaskRecord], tuple[bool, str]]) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        passed, reason = acceptance(task)
        return self._persist_verification(
            task,
            passed=bool(passed),
            reason=reason,
            verifier_id="runtime-acceptance-callback",
            evidence=list(task.outcome_evidence),
            verification_source="RUNTIME_CALLBACK",
        )

    def record_verification_result(
        self,
        task_id: str,
        *,
        passed: bool,
        reason: str,
        verifier_id: str,
        evidence_references: list[str],
    ) -> TaskRecord:
        """Persist a serializable Workspace Agent/MCP verification result.

        This is the remote-safe counterpart to ``verify``. The verifier evaluates the
        configured acceptance test outside the Python process and must provide an
        explicit identity plus evidence references. A passing result without evidence
        fails closed and does not mutate task state.
        """

        assert_runtime_enabled()
        task = self._require(task_id)
        evidence = list(dict.fromkeys(evidence_references))
        if not verifier_id.strip():
            raise ValueError("verifier_id is required")
        if not reason.strip():
            raise ValueError("verification reason is required")
        if passed and not evidence:
            raise ValueError("passing verification requires evidence")
        return self._persist_verification(
            task,
            passed=bool(passed),
            reason=reason,
            verifier_id=verifier_id,
            evidence=evidence,
            verification_source="WORKSPACE_AGENT_MCP",
        )

    def _persist_verification(
        self,
        task: TaskRecord,
        *,
        passed: bool,
        reason: str,
        verifier_id: str,
        evidence: list[str],
        verification_source: str,
    ) -> TaskRecord:
        record = {
            "version": "mesh.cos.verification.v1",
            "task_id": task.task_id,
            "acceptance_test": task.acceptance_test,
            "passed": passed,
            "reason": reason,
            "evidence": list(evidence),
            "verifier_id": verifier_id,
            "verification_source": verification_source,
            "attempt": task.rework_count + 1,
            "verified_at": utcnow(),
        }
        self.ledger.save_record("verification", task.task_id, record)
        transition(task, TaskStatus.VERIFIED if passed else TaskStatus.REWORK)
        self.ledger.save_task(task)
        self._audit(task, "task_verify", "passed" if passed else "failed")
        return task

    def close(self, task_id: str) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        transition(task, TaskStatus.CLOSED)
        self.ledger.save_task(task)
        self._audit(task, "task_close", "closed")
        return task

    def reassign(self, task_id: str, expected_owner: str, new_owner: str, *, reason: str) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        if task.accountable_agent != expected_owner:
            raise ValueError("Current accountable owner does not match expected owner")
        if not new_owner:
            raise ValueError("New accountable owner is required")
        before = task.accountable_agent
        task.accountable_agent = new_owner
        self.ledger.save_task(task)
        record_id = new_id("reassignment")
        self.ledger.save_record(
            "reassignment",
            record_id,
            {
                "record_id": record_id,
                "task_id": task_id,
                "from_agent": before,
                "to_agent": new_owner,
                "reason": reason,
                "timestamp": utcnow(),
            },
        )
        self._audit(task, "task_reassigned", f"{before}->{new_owner}: {reason}")
        return task

    def record_checkin(
        self,
        task_id: str,
        *,
        agent_id: str,
        note: str,
        evidence: list[str] | None = None,
    ) -> dict:
        assert_runtime_enabled()
        task = self._require(task_id)
        record_id = new_id("checkin")
        record = {
            "record_id": record_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "note": note,
            "evidence": list(evidence or []),
            "timestamp": utcnow(),
        }
        self.ledger.save_record("checkin", record_id, record)
        self._audit(task, "task_checkin", note)
        return record

    def remediate_stalled(
        self,
        task_id: str,
        *,
        new_owner: str | None = None,
        reason: str = "stalled",
    ) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        if not stalled(task):
            return task
        if new_owner and new_owner != task.accountable_agent:
            return self.reassign(task_id, task.accountable_agent, new_owner, reason=reason)
        if task.status == TaskStatus.IN_PROGRESS:
            transition(task, TaskStatus.BLOCKED)
            task.blockers.append(reason)
            self.ledger.save_task(task)
            self._audit(task, "task_stalled", reason)
        return task

    def escalate(
        self,
        task_id: str,
        *,
        reason: str,
        approval_owner: str | None = None,
    ) -> TaskRecord:
        assert_runtime_enabled()
        task = self._require(task_id)
        task.escalation_count += 1
        task.approval_owner = approval_owner or task.decision_owner
        if task.status in {TaskStatus.IN_PROGRESS, TaskStatus.READY_FOR_DECISION}:
            transition(task, TaskStatus.AWAITING_APPROVAL)
        self.ledger.save_task(task)
        record_id = new_id("escalation")
        self.ledger.save_record(
            "escalation",
            record_id,
            {
                "record_id": record_id,
                "task_id": task_id,
                "reason": reason,
                "approval_owner": task.approval_owner,
                "classification": "correct",
                "timestamp": utcnow(),
            },
        )
        self._audit(task, "task_escalated", reason)
        return task

    def invoke(
        self,
        task_id: str,
        adapters: GovernedAdapterRegistry,
        *,
        capability: str,
        payload: dict,
    ) -> dict:
        assert_runtime_enabled()
        task = self._require(task_id)
        result = adapters.execute(task.accountable_agent, capability, payload)
        record_id = new_id("invoke")
        self.ledger.save_record(
            "functional_invocation",
            record_id,
            {
                "record_id": record_id,
                "task_id": task_id,
                "agent_id": task.accountable_agent,
                "capability": capability,
                "result": result,
                "timestamp": utcnow(),
            },
        )
        self._audit(task, "functional_invocation", capability)
        return result

    def _require(self, task_id: str) -> TaskRecord:
        task = self.ledger.get_task(task_id)
        if not task:
            raise KeyError(task_id)
        return task

    def _audit(self, task: TaskRecord, event_type: str, result: str) -> None:
        event = AuditEvent(
            event_type,
            "cos",
            task.task_id,
            task.correlation_id,
            int(task.authority_level),
            result,
        )
        self.ledger.record_event(event.to_dict())
