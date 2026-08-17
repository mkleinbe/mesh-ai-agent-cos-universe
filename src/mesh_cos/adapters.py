from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

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
    def __init__(self, registry: dict[str, dict]) -> None:
        self.registry = registry
        self.adapters: dict[tuple[str, str], SkillAdapter] = {}

    def register(self, adapter: SkillAdapter) -> None:
        if adapter.agent_id not in self.registry:
            raise KeyError(adapter.agent_id)
        record = self.registry[adapter.agent_id]
        allowed = set(record.get("skills", [])) | set(record.get("tools", []))
        if adapter.capability not in allowed:
            raise PermissionError(f"Capability not allowed for {adapter.agent_id}: {adapter.capability}")
        self.adapters[(adapter.agent_id, adapter.capability)] = adapter

    def execute(self, agent_id: str, capability: str, payload: dict) -> dict:
        key = (agent_id, capability)
        if key not in self.adapters:
            raise KeyError(key)
        adapter = self.adapters[key]
        if adapter.source or adapter.tool or adapter.action:
            assert_agent_invocation_allowed(
                self.registry,
                agent_id,
                source=adapter.source,
                tool=adapter.tool,
                action=adapter.action,
            )
        return adapter.execute(payload)
