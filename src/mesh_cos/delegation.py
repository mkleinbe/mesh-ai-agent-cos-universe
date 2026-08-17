from __future__ import annotations

from dataclasses import asdict

from .ledger import TaskLedger
from .models import Delegation


def validate_delegation(d: Delegation, *, parent_authority: int, depth: int, active_owner: str | None = None,
                        ancestry: list[str] | None = None, parent_approval_gates: list[str] | None = None) -> None:
    if not d.accountable_agent:
        raise ValueError("Exactly one accountable agent is required")
    if d.accountable_agent in d.contributing_agents:
        raise ValueError("Accountable agent must not be duplicated as a contributor")
    if depth > 2:
        raise ValueError("Phase 1 delegation depth exceeded")
    if int(d.authority_level) > parent_authority:
        raise PermissionError("Delegation cannot widen authority")
    if active_owner and active_owner != d.accountable_agent:
        raise ValueError("Duplicate active ownership detected")
    if ancestry and d.accountable_agent in ancestry:
        raise ValueError("Circular delegation detected")
    if not d.acceptance_test or not d.success_criteria:
        raise ValueError("Delegation requires measurable acceptance conditions")
    required_gates = set(parent_approval_gates or [])
    if not required_gates.issubset(set(d.approval_gates)):
        raise PermissionError("Delegation cannot drop parent approval obligations")
    if set(d.permitted_actions) & set(d.prohibited_actions):
        raise PermissionError("Delegation cannot both permit and prohibit the same action")


class DelegationService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def create(self, delegation: Delegation, *, parent_authority: int, depth: int,
               active_owner: str | None = None, ancestry: list[str] | None = None,
               parent_approval_gates: list[str] | None = None) -> dict:
        validate_delegation(
            delegation, parent_authority=parent_authority, depth=depth, active_owner=active_owner,
            ancestry=ancestry, parent_approval_gates=parent_approval_gates,
        )
        payload = asdict(delegation)
        payload["authority_level"] = int(delegation.authority_level)
        self.ledger.save_record("delegation", delegation.delegation_id, payload)
        return payload
