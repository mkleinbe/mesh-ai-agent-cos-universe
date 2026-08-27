from __future__ import annotations

import os
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
    """Governed runtime bindings for Mesh skills and server-owned capabilities."""

    def __init__(
        self,
        registry: dict[str, dict],
        governance: GovernanceJournal | None = None,
    ) -> None:
        self.registry = registry
        self.governance = governance
        self.adapters: dict[tuple[str, str], SkillAdapter] = {}
        self._known_capabilities = {
            str(capability)
            for record in registry.values()
            for key in ("skills", "tools")
            for capability in record.get(key, [])
        }
        self._bind_declared_skill_handoffs()
        self._bind_server_owned_tools()

    @staticmethod
    def _skill_handoff_executor(agent_id: str, capability: str) -> Callable[[dict], dict]:
        def execute(payload: dict) -> dict:
            return {
                "status": "AUTHORIZED",
                "execution_mode": "CHATGPT_SKILL_HANDOFF",
                "agent_id": agent_id,
                "capability": capability,
                "payload": dict(payload),
            }

        return execute

    def _bind_declared_skill_handoffs(self) -> None:
        """Server-register declared ChatGPT Skills as authorization/handoff adapters."""
        for agent_id, record in self.registry.items():
            for raw_capability in record.get("skills", []):
                capability = str(raw_capability)
                self.adapters[(agent_id, capability)] = SkillAdapter(
                    agent_id,
                    capability,
                    self._skill_handoff_executor(agent_id, capability),
                )

    @staticmethod
    def _require_exact_payload(payload: dict, required: set[str]) -> None:
        fields = set(payload)
        unexpected = sorted(fields - required)
        missing = sorted(required - fields)
        if unexpected:
            raise ValueError("Unexpected Slack collaboration payload fields: " + ", ".join(unexpected))
        if missing:
            raise ValueError("Missing Slack collaboration payload fields: " + ", ".join(missing))

    @staticmethod
    def _slack_collaboration_executor() -> Callable[[dict], dict]:
        """Authorize a connected Slack connector handoff without conferring approval authority."""

        def execute(payload: dict) -> dict:
            required = {"operation", "channel_id", "payload"}
            GovernedAdapterRegistry._require_exact_payload(payload, required)
            if str(payload.get("operation") or "") != "connector_handoff":
                raise PermissionError(
                    "Slack collaboration adapter authorizes connector handoff only"
                )
            configured_channel = str(
                os.environ.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "C0BRL4GCL3A")
            ).strip()
            channel_id = str(payload.get("channel_id") or "").strip()
            if channel_id != configured_channel:
                raise PermissionError("Slack connector handoff channel mismatch")
            forbidden = {
                "approved",
                "approval_status",
                "actor",
                "principal",
                "record_decision",
                "ingest_decision",
            }
            if forbidden.intersection(payload):
                raise PermissionError(
                    "Connected Slack collaboration handoff cannot carry canonical approval authority"
                )
            handoff_payload = payload.get("payload", {})
            if not isinstance(handoff_payload, dict):
                raise TypeError("Slack connector handoff payload must be an object")
            return {
                "status": "AUTHORIZED",
                "execution_mode": "CHATGPT_CONNECTOR_HANDOFF",
                "connector": "Slack",
                "channel_id": configured_channel,
                "authority": "COLLABORATION_ONLY",
                "payload": dict(handoff_payload),
            }

        return execute

    def _bind_server_owned_tools(self) -> None:
        record = self.registry.get("cos")
        if record is None or "slack-adapter" not in record.get("tools", []):
            return
        self.register(
            SkillAdapter(
                "cos",
                "slack-adapter",
                self._slack_collaboration_executor(),
            )
        )

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
        return {
            agent_id: list(record.get("skills", []))
            for agent_id, record in self.registry.items()
            if record.get("skills")
        }

    def execute(self, agent_id: str, capability: str, payload: dict) -> dict:
        if agent_id not in self.registry:
            raise PermissionError(f"Unknown agent principal: {agent_id}")
        key = (agent_id, capability)
        if key not in self.adapters:
            if capability not in self._known_capabilities:
                raise KeyError(capability)
            allowed = set(self.registry[agent_id].get("skills", [])) | set(
                self.registry[agent_id].get("tools", [])
            )
            if capability not in allowed:
                raise PermissionError(f"Capability not allowed for {agent_id}: {capability}")
            raise RuntimeError(f"Declared capability is not server-registered: {capability}")
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
        authority_level = int(payload.get("authority_level", 0))
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
