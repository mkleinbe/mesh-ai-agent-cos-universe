#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from mesh_cos.audit import AuditEvent
from mesh_cos.contracts import agent_record_contract, validate_runtime_contract
from mesh_cos.models import AuthorityLevel, Delegation, TaskRecord
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


for schema_path in sorted(CONTRACTS.glob("*.schema.json")):
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    require(schema.get("additionalProperties") is False, f"{schema_path.name}: contracts must be closed")
    require("version" in schema.get("required", []), f"{schema_path.name}: version must be required")

registry = load_registry(ROOT / "agents" / "registry.json")
for record in registry.values():
    validate_runtime_contract("agent-record", agent_record_contract(record), CONTRACTS)

task = TaskRecord("T-drift", "objective", "outcome", "michael", "michael", "cro", "michael", acceptance_test="accepted")
validate_runtime_contract("task", task.to_dict(), CONTRACTS)

delegation = Delegation(
    "D-drift", "T-drift", "cos", "cro", "objective", "outcome", "brief", ["accepted"], "P1", AuthorityLevel.L2, "accepted"
)
validate_runtime_contract("delegation", delegation.to_dict(), CONTRACTS)
validate_runtime_contract("agent-event", AuditEvent("drift_check", "cos", "T-drift", "corr-drift", 2, "ok").to_dict(), CONTRACTS)

env_text = (ROOT / ".env.example").read_text()
require("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID=C0BRL4GCL3A" in env_text, "Agent Ops Slack channel drifted")

required_docs = {
    "README.md": ["#mesh-agent-ops", "C0BRL4GCL3A", "TaskLedger", "ChiefOfStaffService"],
    "docs/architecture.md": ["TaskLedger", "Slack", "AgentOps"],
    "docs/phase-1-operating-contract.md": ["L4", "L5", "VERIFIED"],
    "docs/testing-evaluation.md": ["13", "contract"],
}
for relative, tokens in required_docs.items():
    text = (ROOT / relative).read_text()
    for token in tokens:
        require(token in text, f"{relative}: expected documented runtime token {token!r}")

print("runtime/documentation drift check: OK")
