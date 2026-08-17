from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .governance import GovernanceJournal
from .security import assert_agent_invocation_allowed


@dataclass(slots=True)
class FunctionalAdapter:
    agent_id: str
    execute_fn: Callable[[dict], dict]

    def execute(self, payload: dict) -> dict:
        return self.execute_fn(payload)


@dataclass(slots=True)
class AdapterRegistry:
    adapters: dict[str, FunctionalAdapter] = field(default_factory=dict)

    def register(self, adapter: FunctionalAdapter) -> None:
        self.adapters[adapter.agent_id] = adapter

    def execute(self, agent_id: str, payload: dict) -> dict:
        if agent_id not in self.adapters:
            raise KeyError(agent_id)
        return self.adapters[agent_id].execute(payload)


@dataclass(slots=True)
class SkillAdapter:
    agent_id: str
    capability: str
    execute_fn: Callable[[dict], dict]
    source: str | None = None
    tool: str | None = None
    action: str | None = None

    def execute(self, payload: dict) -> dict:
        return self.execute_fn(payload)


class GovernedAdapterRegistry:
    """Thin runtime binding for existing Mesh skills with cross-agent governance logging."""

    def __init__(self, registry: dict[str, dict], governance: GovernanceJournal | None = None) -> None:
        self.registry = registry
        self.governance = governance
        self.adapters: dict[tuple[str, str], SkillAdapter] = {}

    def register(self, adapter: SkillAdapter) -> None:
        if adapter.agent_id not in self.registry:
            raise KeyError(adapter.agent_id)
        record = self.registry[adapter.agent_id]
        allowed = set(record.get("skills", [])) | set(record.get("tools", []))
        if adapter.capability not in allowed:
            raise PermissionError(f"Capability not allowed for {adapter.agent_id}: {adapter.capability}")
        self.adapters[(adapter.agent_id, adapter.capability)] = adapter

    def bind_available_skills(self, executors: dict[str, Callable[[dict], dict]]) -> int:
        bound = 0
        for agent_id, record in self.registry.items():
            for capability in record.get("skills", []):
                if capability in executors:
                    self.register(SkillAdapter(agent_id, capability, executors[capability]))
                    bound += 1
        return bound

    def required_capabilities(self) -> dict[str, list[str]]:
        return {agent_id: list(record.get("skills", [])) for agent_id, record in self.registry.items() if record.get("skills")}

    def execute(self, agent_id: str, capability: str, payload: dict) -> dict:
        key = (agent_id, capability)
        if key not in self.adapters:
            raise KeyError(key)
        adapter = self.adapters[key]
        record = self.registry[agent_id]
        if adapter.source or adapter.tool or adapter.action:
            assert_agent_invocation_allowed(
                self.registry,
                agent_id,
                source=adapter.source,
                tool=adapter.tool,
                action=adapter.action,
            )
        try:
            result = adapter.execute(payload)
        except Exception as exc:
            self._audit_invocation(record, adapter, payload, "FAILURE", type(exc).__name__, str(exc))
            raise
        self._audit_invocation(record, adapter, payload, "SUCCESS", None, None)
        return result

    def _audit_invocation(
        self,
        record: dict,
        adapter: SkillAdapter,
        payload: dict,
        result_status: str,
        error_code: str | None,
        error_summary: str | None,
    ) -> None:
        if self.governance is None:
            return
        task_id = payload.get("task_id")
        correlation_id = payload.get("correlation_id") or f"skill:{adapter.agent_id}:{adapter.capability}"
        authority_level = int(payload.get("authority_level", record.get("decision_authority", 0)))
        self.governance.record_event(
            event_type="agent.capability_invoked",
            event_category="EXECUTION",
            action=adapter.action or "INVOKE",
            actor_type="AGENT",
            actor_id=adapter.agent_id,
            actor_role=record.get("role", adapter.agent_id),
            task_id=task_id,
            correlation_id=correlation_id,
            decision_id=payload.get("decision_id"),
            authority_level=authority_level,
            policy_rule_ids=["registry-source-tool-action-policy", "governance-policy-v1"],
            capability_tool=adapter.capability,
            target_resource=adapter.source or adapter.tool or adapter.capability,
            source_system=adapter.source or "Mesh governed capability adapter",
            input_summary=payload.get("governance_input_summary", "Governed capability invocation."),
            result_status=result_status,
            output_summary=(
                payload.get("governance_output_summary", "Governed capability completed.")
                if result_status == "SUCCESS"
                else "Governed capability failed; error metadata recorded without raw payload disclosure."
            ),
            evidence_references=list(payload.get("evidence_references", [])),
            approval_reference=payload.get("approval_reference"),
            human_approver=payload.get("human_approver"),
            risk_severity=payload.get("risk_severity", "LOW"),
            data_classification=payload.get("data_classification", "INTERNAL"),
            error_code=error_code,
            error_summary=error_summary,
            model_provider=payload.get("model_provider"),
            model_id_version=payload.get("model_id_version"),
            skill_agent_version=str(record.get("version", "unknown")),
            environment=payload.get("environment", "RUNTIME"),
            retention_class=payload.get("retention_class", "GOVERNANCE_LONG_TERM"),
        )
