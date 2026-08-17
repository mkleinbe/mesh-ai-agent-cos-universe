from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

VALID_STATES = {"SHADOW", "ACTIVE", "WATCH", "RESTRICTED", "QUARANTINED", "RETIRED"}
REGISTRY_MIGRATION_TIMESTAMP = "2026-08-17T00:00:00+00:00"


def _authority_level(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        levels = [int(item) for item in re.findall(r"L([0-5])", value)]
        if levels:
            return max(levels)
        lowered = value.lower()
        if "advisory" in lowered or "execution" in lowered:
            return 1
    raise ValueError(f"Invalid decision authority: {value!r}")


def load_registry(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    path = Path(path) if path else Path(__file__).resolve().parents[2] / "agents" / "registry.json"
    raw = json.loads(path.read_text())
    agents = raw.get("agents", [])
    if not isinstance(agents, list):
        raise ValueError("Registry agents must be a list")
    result: dict[str, dict[str, Any]] = {}
    for source_record in agents:
        record = deepcopy(source_record)
        agent_id = record.get("agent_id")
        if not agent_id or agent_id in result:
            raise ValueError("Every agent must have a unique agent_id")
        if record.get("status") not in VALID_STATES:
            raise ValueError(f"Invalid health state for {agent_id}")
        original_authority = record.get("decision_authority")
        record["decision_authority_description"] = original_authority
        record["decision_authority"] = _authority_level(original_authority)
        record.setdefault("runtime_health", record["status"])
        record.setdefault("created_at", REGISTRY_MIGRATION_TIMESTAMP)
        record.setdefault("updated_at", REGISTRY_MIGRATION_TIMESTAMP)
        result[agent_id] = record
    for agent_id, record in result.items():
        parent = record.get("parent_agent_id")
        if parent and parent not in result:
            raise ValueError(f"Unknown parent for {agent_id}: {parent}")
    return result


AGENTS = load_registry()


def get_agent(agent_id: str) -> dict[str, Any]:
    if agent_id not in AGENTS:
        raise KeyError(agent_id)
    return deepcopy(AGENTS[agent_id])


def validate_registry() -> None:
    load_registry()
