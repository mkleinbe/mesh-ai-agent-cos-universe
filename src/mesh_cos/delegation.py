from __future__ import annotations

from .models import Delegation


def validate_delegation(d: Delegation, *, parent_authority: int, depth: int, active_owner: str | None = None,
                        ancestry: list[str] | None = None) -> None:
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
