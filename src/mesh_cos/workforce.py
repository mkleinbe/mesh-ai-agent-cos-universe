from __future__ import annotations

from datetime import datetime

from .agentops import AgentOpsEvaluator
from .audit import AuditEvent
from .delegation import DelegationService
from .ledger import TaskLedger
from .lifecycle import transition
from .models import Delegation, TaskStatus, new_id, utcnow
from .orchestration import ChiefOfStaffService


class ChiefOfStaffWorkforceManager:
    """Management loop above task mechanics. The CoS manages work, not functional truth."""

    def __init__(self, ledger: TaskLedger, *, agentops: AgentOpsEvaluator | None = None) -> None:
        self.ledger = ledger
        self.cos = ChiefOfStaffService(ledger)
        self.delegations = DelegationService(ledger)
        self.agentops = agentops

    def delegate(
        self,
        delegation: Delegation,
        *,
        parent_authority: int,
        depth: int,
        active_owner: str | None = None,
        ancestry: list[str] | None = None,
        parent_approval_gates: list[str] | None = None,
    ) -> dict:
        return self.delegations.create(
            delegation,
            parent_authority=parent_authority,
            depth=depth,
            active_owner=active_owner,
            ancestry=ancestry,
            parent_approval_gates=parent_approval_gates,
        )

    def management_cycle(
        self,
        *,
        now: datetime | None = None,
        max_concurrency: dict[str, int] | None = None,
    ) -> dict:
        tasks = self.ledger.list_tasks()
        if self.agentops is not None:
            observation = self.agentops.observe_tasks(
                tasks,
                max_concurrency=max_concurrency,
                now=now,
            )
        else:
            from .agentops import stalled

            observation = {
                "stalled_task_ids": [task.task_id for task in tasks if stalled(task, now=now)],
                "active_by_agent": {},
                "overloaded_agents": [],
            }
        remediated: list[str] = []
        for task_id in observation["stalled_task_ids"]:
            before = self.ledger.get_task(task_id)
            if before and before.status == TaskStatus.IN_PROGRESS:
                self.cos.remediate_stalled(task_id, reason="missed configured check-in")
                remediated.append(task_id)
        report = {**observation, "remediated_task_ids": remediated, "timestamp": utcnow()}
        self.ledger.save_record("management_cycle", new_id("cycle"), report)
        return report

    def supersede(
        self,
        task_id: str,
        replacement_task_id: str,
        *,
        actor: str = "cos",
        reason: str,
    ) -> dict:
        task = self.ledger.get_task(task_id)
        replacement = self.ledger.get_task(replacement_task_id)
        if task is None or replacement is None:
            raise KeyError(task_id if task is None else replacement_task_id)
        if task.status in {TaskStatus.CLOSED, TaskStatus.VERIFIED, TaskStatus.CANCELLED}:
            raise ValueError("Terminal task cannot be superseded")
        transition(task, TaskStatus.CANCELLED)
        self.ledger.save_task(task)
        record = {
            "task_id": task_id,
            "replacement_task_id": replacement_task_id,
            "actor": actor,
            "reason": reason,
            "timestamp": utcnow(),
        }
        self.ledger.save_record("supersession", task_id, record)
        self.ledger.record_event(
            AuditEvent(
                "task_superseded",
                actor,
                task_id,
                task.correlation_id,
                int(task.authority_level),
                replacement_task_id,
            ).to_dict()
        )
        return record

    def recommend_portfolio_change(self, agent_id: str, recommendation: str, reason: str) -> dict:
        if self.agentops is not None and recommendation not in self.agentops.supported_recommendations():
            raise ValueError("Unsupported AgentOps recommendation")
        if recommendation == "BUILD_NEW_SPECIALIST":
            action = "recommend only; human approval required before agent creation"
        else:
            action = "recommend to CoS; material authority changes require Michael approval"
        record_id = new_id("portfolio")
        record = {
            "record_id": record_id,
            "agent_id": agent_id,
            "recommendation": recommendation,
            "reason": reason,
            "authority_boundary": action,
            "timestamp": utcnow(),
        }
        self.ledger.save_record("portfolio_recommendation", record_id, record)
        return record
