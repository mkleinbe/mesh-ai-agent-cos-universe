from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .adapters import AdapterRegistry, AuthorizationGateway, FunctionalAgentAdapter
from .registry import AgentRegistry

PHASE1_FUNCTIONAL_AGENTS = (
    "cro", "cfo", "coo", "consultant-network-steward",
    "cmo", "vp-content", "devils-advocate", "message-ops",
)


class MessageOperationsAdapter(FunctionalAgentAdapter):
    def execute(self, *, tool: str, source: str | None, payload: dict[str, Any]) -> Any:
        if payload.get("consequential_external_send") and not payload.get("approval_reference"):
            raise PermissionError("Consequential external send requires recorded human approval")
        return super().execute(tool=tool, source=source, payload=payload)


class FunctionalRuntime:
    """Executable adapter composition layer with injected real integrations."""

    def __init__(self, registry: AgentRegistry, invokers: dict[str, Callable[[str, str | None, dict[str, Any]], Any]] | None = None) -> None:
        self.registry = registry
        self.gateway = AuthorizationGateway(registry)
        self.adapters = AdapterRegistry()
        for agent_id, invoker in (invokers or {}).items():
            self.configure(agent_id, invoker)

    def configure(self, agent_id: str, invoker: Callable[[str, str | None, dict[str, Any]], Any]) -> None:
        if agent_id not in PHASE1_FUNCTIONAL_AGENTS:
            raise ValueError(f"{agent_id} is not a Phase 1 functional adapter")
        adapter_cls = MessageOperationsAdapter if agent_id == "message-ops" else FunctionalAgentAdapter
        self.adapters.register(adapter_cls(agent_id, gateway=self.gateway, invoker=invoker))

    def execute(self, agent_id: str, *, tool: str, source: str | None = None, payload: dict[str, Any] | None = None) -> Any:
        return self.adapters.execute(agent_id, tool=tool, source=source, payload=payload or {})

    def readiness(self) -> dict[str, bool]:
        result: dict[str, bool] = {}
        for agent_id in PHASE1_FUNCTIONAL_AGENTS:
            try:
                self.adapters.get(agent_id)
                result[agent_id] = True
            except KeyError:
                result[agent_id] = False
        return result

    def missing(self) -> list[str]:
        return [agent_id for agent_id, ready in self.readiness().items() if not ready]
