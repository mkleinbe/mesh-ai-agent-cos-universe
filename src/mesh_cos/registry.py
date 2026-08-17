from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

VALID_STATES = {"SHADOW", "ACTIVE", "WATCH", "RESTRICTED", "QUARANTINED", "RETIRED"}
REGISTRY_MIGRATION_TIMESTAMP = "2026-08-17T00:00:00+00:00"
DISPLAY_VERSION_PATTERN = re.compile(r"\bv\d+(?:\.\d+)*\b", re.IGNORECASE)
IMPLEMENTATION_VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")


def _authority_level(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        primary_clause = value.split(";", 1)[0]
        levels = [int(item) for item in re.findall(r"L([0-5])", primary_clause)]
        if levels:
            return max(levels)
        lowered = primary_clause.lower()
        if "advisory" in lowered or "execution" in lowered:
            return 1
    raise ValueError(f"Invalid decision authority: {value!r}")


def _validate_role_identity(record: dict[str, Any]) -> None:
    agent_id = record.get("agent_id", "unknown")
    display_name = record.get("display_name")
    if not isinstance(display_name, str) or not display_name.strip():
        raise ValueError(f"Agent {agent_id} must have a stable display_name")
    if DISPLAY_VERSION_PATTERN.search(display_name):
        raise ValueError(
            f"Agent {agent_id} display_name must not embed implementation version: {display_name!r}"
        )
    version = record.get("version")
    if not isinstance(version, str) or not IMPLEMENTATION_VERSION_PATTERN.fullmatch(version):
        raise ValueError(
            f"Agent {agent_id} must carry implementation version as MAJOR.MINOR.PATCH metadata"
        )


def _load_governance_policy(registry_path: Path) -> dict[str, Any]:
    root = registry_path.parent.parent
    policy_path = root / "config" / "governance-policy.v1.json"
    if not policy_path.exists():
        return {}
    policy = json.loads(policy_path.read_text())
    if policy.get("applies_to") != "ALL_REGISTERED_AGENTS":
        raise ValueError("Governance policy must explicitly target all registered agents")
    return policy


def _apply_governance_policy(record: dict[str, Any], policy: dict[str, Any]) -> None:
    if not policy:
        return
    governance_tool = policy["governance_tool"]
    tools = record.setdefault("tools", [])
    if governance_tool not in tools:
        tools.append(governance_tool)
    outputs = record.setdefault("output_contracts", [])
    for contract in policy.get("output_contracts", []):
        if contract not in outputs:
            outputs.append(contract)
    record["governance_policy"] = deepcopy(policy["governance_policy"])


def load_registry(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    path = Path(path) if path else Path(__file__).resolve().parents[2] / "agents" / "registry.json"
    raw = json.loads(path.read_text())
    policy = _load_governance_policy(path)
    agents = raw.get("agents", [])
    if not isinstance(agents, list):
        raise ValueError("Registry agents must be a list")  # noqa: TRY004 - stable public validation contract
    result: dict[str, dict[str, Any]] = {}
    for source_record in agents:
        record = deepcopy(source_record)
        agent_id = record.get("agent_id")
        if not agent_id or agent_id in result:
            raise ValueError("Every agent must have a unique agent_id")
        if record.get("status") not in VALID_STATES:
            raise ValueError(f"Invalid health state for {agent_id}")
        _validate_role_identity(record)
        original_authority = record.get("decision_authority")
        record["decision_authority_description"] = original_authority
        record["decision_authority"] = _authority_level(original_authority)
        record.setdefault("runtime_health", record["status"])
        record.setdefault("created_at", REGISTRY_MIGRATION_TIMESTAMP)
        record.setdefault("updated_at", REGISTRY_MIGRATION_TIMESTAMP)
        _apply_governance_policy(record, policy)
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
