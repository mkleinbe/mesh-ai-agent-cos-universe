from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


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
