from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

CONTRACT_FILES = {
    "agent-record": "agent-record.v1.schema.json",
    "task": "task.v1.schema.json",
    "delegation": "delegation.v1.schema.json",
    "agent-event": "agent-event.v1.schema.json",
    "decision": "decision.v1.schema.json",
    "conflict": "conflict.v1.schema.json",
    "approval": "approval.v1.schema.json",
    "performance-event": "performance-event.v1.schema.json",
    "performance-scorecard": "performance-scorecard.v1.schema.json",
}


def validate_runtime_contract(kind: str, payload: dict[str, Any], contracts_dir: str | Path) -> None:
    if kind not in CONTRACT_FILES:
        raise KeyError(kind)
    schema = json.loads((Path(contracts_dir) / CONTRACT_FILES[kind]).read_text())
    Draft202012Validator(schema).validate(payload)


def agent_record_contract(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": "mesh.cos.agent-record.v1",
        "agent_id": record["agent_id"],
        "display_name": record["display_name"],
        "role": record["role"],
        "description": record["description"],
        "parent_agent_id": record.get("parent_agent_id"),
        "agent_type": record["agent_type"],
        "status": record["status"],
        "accountable_domain": record["accountable_domain"],
        "authoritative_sources": list(record.get("authoritative_sources", [])),
        "allowed_sources": list(record.get("allowed_sources", [])),
        "skills": list(record.get("skills", [])),
        "tools": list(record.get("tools", [])),
        "input_contracts": list(record.get("input_contracts", [])),
        "output_contracts": list(record.get("output_contracts", [])),
        "permitted_actions": list(record.get("permitted_actions", [])),
        "prohibited_actions": list(record.get("prohibited_actions", [])),
        "decision_authority": int(record["decision_authority"]),
        "required_approvals": list(record.get("required_approvals", [])),
        "delegation_permissions": list(record.get("delegation_permissions", [])),
        "max_delegation_depth": int(record.get("max_delegation_depth", 0)),
        "normal_SLA": str(record.get("normal_SLA", "configurable")),
        "performance_policy": str(record.get("performance_policy", "phase1-scorecard-v1")),
        "confidentiality_class": str(record.get("confidentiality_class", "internal-confidential")),
        "runtime_health": str(record.get("runtime_health", record["status"])),
    }
