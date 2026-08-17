from __future__ import annotations

from .delegation import validate_delegation
from .ledger import TaskLedger
from .models import Delegation, TaskRecord
from .registry import AgentRegistry


class DelegationService:
    def __init__(self, *, ledger: TaskLedger, registry: AgentRegistry) -> None:
        self.ledger = ledger
        self.registry = registry

    def create(self, task: TaskRecord, delegation: Delegation, *, depth: int, ancestry: list[str] | None = None) -> Delegation:
        if delegation.task_id != task.task_id:
            raise ValueError("Delegation task does not match parent task")
        if delegation.business_objective != task.objective:
            raise ValueError("Child delegation cannot redefine the parent objective")
        if delegation.expected_outcome != task.expected_outcome:
            raise ValueError("Child delegation cannot redefine the parent expected outcome")
        if task.approval_owner and not delegation.approval_gates:
            raise PermissionError("Parent approval obligations must be inherited by the delegation")
        if ancestry and delegation.accountable_agent in ancestry:
            raise ValueError("Circular delegation detected")

        active_owner = self.ledger.active_owner_for_task(task.task_id)
        validate_delegation(
            delegation,
            parent_authority=int(task.authority_level),
            depth=depth,
            active_owner=active_owner,
            ancestry=ancestry,
        )

        agent = self.registry.get(delegation.accountable_agent)
        allowed = set(agent.get("permitted_actions", []))
        prohibited = set(agent.get("prohibited_actions", []))
        if delegation.permitted_actions and not set(delegation.permitted_actions).issubset(allowed):
            unknown = sorted(set(delegation.permitted_actions) - allowed)
            raise PermissionError(f"Delegation attempted actions outside agent authority: {unknown}")
        if prohibited.intersection(delegation.permitted_actions):
            raise PermissionError("Delegation attempted to permit an agent-prohibited action")
        if depth > int(agent.get("max_delegation_depth", 0)) + 1 and delegation.delegating_agent != "cos":
            raise ValueError("Agent-specific delegation depth exceeded")

        self.ledger.save_delegation(delegation.to_dict())
        return delegation
