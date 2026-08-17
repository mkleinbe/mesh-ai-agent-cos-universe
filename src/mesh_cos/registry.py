from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import re
from typing import Any


HEALTH_STATES = {"SHADOW", "ACTIVE", "WATCH", "RESTRICTED", "QUARANTINED", "RETIRED"}


def _authority_level(value: Any) -> tuple[int, str]:
    if isinstance(value, int):
        return value, f"L{value}"
    policy = str(value or "L0")
    match = re.search(r"L([0-5])", policy)
    return (int(match.group(1)) if match else 0), policy


def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
    item = deepcopy(raw)
    agent_version = str(item.pop("version", "1.0.0"))
    level, policy = _authority_level(item.get("decision_authority"))
    item["version"] = "mesh.cos.agent-record.v1"
    item["agent_version"] = agent_version
    item["decision_authority"] = level
    item["decision_authority_policy"] = policy
    item.setdefault("role", item.get("display_name", item.get("agent_id", "agent")))
    item.setdefault("description", item.get("accountable_domain", ""))
    item.setdefault("parent_agent_id", None)
    item.setdefault("authoritative_sources", [])
    item.setdefault("allowed_sources", [])
    item.setdefault("skills", [])
    item.setdefault("tools", [])
    item.setdefault("input_contracts", [])
    item.setdefault("output_contracts", [])
    item.setdefault("permitted_actions", [])
    item.setdefault("prohibited_actions", [])
    item.setdefault("required_approvals", [])
    item.setdefault("delegation_permissions", [])
    item.setdefault("normal_SLA", "configurable")
    item.setdefault("performance_policy", "phase1-scorecard-v1")
    item.setdefault("confidentiality_class", "internal-confidential")
    item.setdefault("runtime_health", item.get("status", "SHADOW"))
    return item


class AgentRegistry:
    def __init__(self, records: dict[str, dict[str, Any]], *, source_path: str | None = None) -> None:
        self._records = records
        self.source_path = source_path
        self.validate()

    @classmethod
    def from_file(cls, path: str | Path) -> "AgentRegistry":
        p = Path(path)
        data = json.loads(p.read_text())
        records = {_normalize(item)["agent_id"]: _normalize(item) for item in data["agents"]}
        return cls(records, source_path=str(p))

    @classmethod
    def default(cls) -> "AgentRegistry":
        configured = os.getenv("MESH_COS_AGENT_REGISTRY_PATH")
        if configured:
            return cls.from_file(configured)
        repo_path = Path(__file__).resolve().parents[2] / "agents" / "registry.json"
        if repo_path.exists():
            return cls.from_file(repo_path)
        return cls.from_file(Path("agents") / "registry.json")

    def ids(self) -> list[str]:
        return sorted(self._records)

    def get(self, agent_id: str) -> dict[str, Any]:
        if agent_id not in self._records:
            raise KeyError(agent_id)
        return deepcopy(self._records[agent_id])

    def validate(self) -> None:
        for agent_id, record in self._records.items():
            parent = record.get("parent_agent_id")
            if parent and parent not in self._records:
                raise ValueError(f"Unknown parent for {agent_id}: {parent}")
            if record.get("status") not in HEALTH_STATES:
                raise ValueError(f"Invalid health state for {agent_id}")
            if record.get("runtime_health") not in HEALTH_STATES:
                raise ValueError(f"Invalid runtime health for {agent_id}")
            if not 0 <= int(record.get("decision_authority", -1)) <= 5:
                raise ValueError(f"Invalid decision authority for {agent_id}")
            if not 0 <= int(record.get("max_delegation_depth", -1)) <= 2:
                raise ValueError(f"Invalid delegation depth for {agent_id}")

    def with_runtime_health(self, agent_id: str, health: str) -> dict[str, Any]:
        if health not in HEALTH_STATES:
            raise ValueError(f"Invalid runtime health: {health}")
        self._records[agent_id]["runtime_health"] = health
        self._records[agent_id]["status"] = health
        return self.get(agent_id)


_DEFAULT: AgentRegistry | None = None


def _default() -> AgentRegistry:
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = AgentRegistry.default()
    return _DEFAULT


def get_agent(agent_id: str) -> dict[str, Any]:
    return _default().get(agent_id)


def validate_registry() -> None:
    _default().validate()
