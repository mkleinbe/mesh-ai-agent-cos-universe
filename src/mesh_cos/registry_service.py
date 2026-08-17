from __future__ import annotations

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import new_id, utcnow
from .registry import AgentRegistry


class RegistryControlPlane:
    def __init__(self, *, registry: AgentRegistry, ledger: TaskLedger) -> None:
        self.registry = registry
        self.ledger = ledger

    def apply_persisted_overrides(self) -> None:
        for agent_id in self.registry.ids():
            changes = self.ledger.list_registry_changes(agent_id)
            if changes:
                self.registry.with_runtime_health(agent_id, changes[-1]["to_health"])

    def set_health(
        self,
        agent_id: str,
        health: str,
        *,
        actor: str,
        reason: str,
        approved_by_michael: bool = False,
        approval_reference: str | None = None,
    ) -> dict:
        current = self.registry.get(agent_id)["runtime_health"]
        if current in {"RESTRICTED", "QUARANTINED"} and health == "ACTIVE" and not approved_by_michael:
            raise PermissionError("Restoring material agent authority requires Michael approval")
        record = self.registry.with_runtime_health(agent_id, health)
        change = {
            "change_id": new_id("registry"),
            "agent_id": agent_id,
            "from_health": current,
            "to_health": health,
            "actor": actor,
            "reason": reason,
            "timestamp": utcnow(),
            "approval_reference": approval_reference,
        }
        self.ledger.save_registry_change(change)
        event = AuditEvent(
            event_type="registry_health_changed",
            actor_agent=actor,
            task_id=f"registry:{agent_id}",
            correlation_id=change["change_id"],
            authority_level=3,
            result=health,
            before_state={"runtime_health": current},
            after_state={"runtime_health": health},
            approval_reference=approval_reference,
            evidence_references=[f"registry-change://{change['change_id']}"],
        )
        self.ledger.record_event(event.to_dict())
        return record
