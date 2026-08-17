from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .registry import AgentRegistry


class AuthorizationGateway:
    """Enforces the canonical Agent Registry before tool/source invocation."""

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def authorize(self, agent_id: str, *, tool: str, source: str | None = None) -> None:
        agent = self.registry.get(agent_id)
        health = agent.get("runtime_health", agent.get("status"))
        if health in {"QUARANTINED", "RETIRED"}:
            raise PermissionError(f"Agent {agent_id} is not eligible for production invocation")
        allowed_tools = set(agent.get("tools", [])) | set(agent.get("skills", []))
        if tool not in allowed_tools:
            raise PermissionError(f"Tool {tool} is not allowed for {agent_id}")
        if source:
            allowed_sources = set(agent.get("allowed_sources", [])) | set(agent.get("authoritative_sources", []))
            if source not in allowed_sources:
                raise PermissionError(f"Source {source} is not allowed for {agent_id}")

    def invoke(
        self,
        agent_id: str,
        *,
        tool: str,
        source: str | None,
        function: Callable[..., Any],
        **kwargs: Any,
    ) -> Any:
        self.authorize(agent_id, tool=tool, source=source)
        return function(tool, source, kwargs)


class FunctionalAgentAdapter:
    def __init__(self, agent_id: str, *, gateway: AuthorizationGateway, invoker: Callable[[str, str | None, dict[str, Any]], Any]) -> None:
        self.agent_id = agent_id
        self.gateway = gateway
        self.invoker = invoker
        self.gateway.registry.get(agent_id)

    def execute(self, *, tool: str, source: str | None, payload: dict[str, Any]) -> Any:
        self.gateway.authorize(self.agent_id, tool=tool, source=source)
        return self.invoker(tool, source, payload)


class AdapterRegistry:
    def __init__(self, adapters: list[FunctionalAgentAdapter] | None = None) -> None:
        self._adapters = {a.agent_id: a for a in adapters or []}

    def register(self, adapter: FunctionalAgentAdapter) -> None:
        self._adapters[adapter.agent_id] = adapter

    def get(self, agent_id: str) -> FunctionalAgentAdapter:
        if agent_id not in self._adapters:
            raise KeyError(f"No executable adapter configured for {agent_id}")
        return self._adapters[agent_id]

    def execute(self, agent_id: str, *, tool: str, source: str | None = None, payload: dict[str, Any] | None = None) -> Any:
        return self.get(agent_id).execute(tool=tool, source=source, payload=payload or {})
