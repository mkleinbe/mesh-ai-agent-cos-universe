from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from mesh_cos.models import AuthorityLevel, Delegation, TaskRecord
from mesh_cos.registry import AgentRegistry

ROOT = Path(__file__).resolve().parents[2]


def validate(name: str, payload: dict) -> None:
    schema = json.loads((ROOT / "contracts" / f"{name}.schema.json").read_text())
    Draft202012Validator(schema).validate(payload)


def test_task_runtime_payload_is_contract_complete():
    task = TaskRecord(
        task_id="T1",
        objective="o",
        expected_outcome="e",
        requested_by="m",
        executive_sponsor="m",
        accountable_agent="cro",
        decision_owner="m",
        acceptance_test="accept",
    )
    payload = task.to_dict()
    validate("task.v1", payload)
    assert payload["version"] == "mesh.cos.task.v1"
    assert "correlation_id" in payload
    assert "slack_channel_id" in payload
    assert "audit_events" in payload


def test_delegation_runtime_payload_is_contract_complete():
    d = Delegation(
        delegation_id="D1",
        task_id="T1",
        delegating_agent="cos",
        accountable_agent="cro",
        business_objective="o",
        expected_outcome="e",
        deliverable="brief",
        success_criteria=["accepted"],
        priority="P1",
        authority_level=AuthorityLevel.L3,
        acceptance_test="accept",
        contributing_agents=["cfo"],
        permitted_actions=["analysis"],
        prohibited_actions=["pricing_approval"],
        approval_gates=["pricing"],
    )
    payload = d.to_dict()
    validate("delegation.v1", payload)
    assert payload["version"] == "mesh.cos.delegation.v1"
    assert payload["contributing_agents"] == ["cfo"]


def test_agent_registry_records_validate_against_agent_contract():
    registry = AgentRegistry.from_file(ROOT / "agents" / "registry.json")
    assert registry.ids()
    for agent_id in registry.ids():
        payload = registry.get(agent_id)
        validate("agent-record.v1", payload)
        assert payload["agent_id"] == agent_id
        assert "input_contracts" in payload
        assert "runtime_health" in payload
