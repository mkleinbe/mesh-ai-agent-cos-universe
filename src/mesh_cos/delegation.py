from __future__ import annotations

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import Delegation, new_id


def validate_delegation(
    delegation: Delegation,
    *,
    parent_authority: int,
    depth: int,
    max_depth: int | None = None,
    active_owner: str | None = None,
    ancestry: list[str] | None = None,
    parent_approval_gates: list[str] | None = None,
) -> None:
    if not delegation.accountable_agent:
        raise ValueError("Exactly one accountable agent is required")
    if delegation.accountable_agent in delegation.contributing_agents:
        raise ValueError("Accountable agent must not be duplicated as a contributor")
    if max_depth is not None and depth > max_depth:
        raise ValueError("Canonical registry delegation depth exceeded")
    if int(delegation.authority_level) > parent_authority:
        raise PermissionError("Delegation cannot widen authority")
    if active_owner and active_owner != delegation.accountable_agent:
        raise ValueError("Duplicate active ownership detected")
    if ancestry and delegation.accountable_agent in ancestry:
        raise ValueError("Circular delegation detected")
    if not delegation.acceptance_test or not delegation.success_criteria:
        raise ValueError("Delegation requires measurable acceptance conditions")
    required_gates = set(parent_approval_gates or [])
    if not required_gates.issubset(set(delegation.approval_gates)):
        raise PermissionError("Delegation cannot drop parent approval obligations")
    if set(delegation.permitted_actions) & set(delegation.prohibited_actions):
        raise PermissionError("Delegation cannot both permit and prohibit the same action")


class DelegationService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def create(
        self,
        delegation: Delegation,
        *,
        parent_authority: int,
        depth: int,
        max_depth: int | None = None,
        active_owner: str | None = None,
        ancestry: list[str] | None = None,
        parent_approval_gates: list[str] | None = None,
    ) -> dict:
        validate_delegation(
            delegation,
            parent_authority=parent_authority,
            depth=depth,
            max_depth=max_depth,
            active_owner=active_owner,
            ancestry=ancestry,
            parent_approval_gates=parent_approval_gates,
        )
        payload = delegation.to_dict()
        self.ledger.save_record("delegation", delegation.delegation_id, payload)
        task = self.ledger.get_task(delegation.task_id)
        correlation_id = task.correlation_id if task else new_id("corr")
        event = AuditEvent(
            "delegation_created",
            delegation.delegating_agent,
            delegation.task_id,
            correlation_id,
            int(delegation.authority_level),
            delegation.delegation_id,
        )
        self.ledger.record_event(event.to_dict())
        return payload
