from __future__ import annotations

import json
from pathlib import Path

import pytest

from mesh_cos import mcp_stdio_bridge as bridge
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.mcp_validation import RequestValidationError, load_input_schemas, validate_tool_arguments
from mesh_cos.models import TaskStatus

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_AGENTS = {
    "cos",
    "agentops",
    "answer-desk",
    "cro",
    "cfo",
    "coo",
    "consultant-network-steward",
    "cmo",
    "vp-content",
    "message-ops",
}


def test_input_schema_registry_is_exactly_the_public_tool_catalog() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    schemas = load_input_schemas()
    contract_tools = {tool["name"] for tool in policy.contract["tools"]}
    assert set(schemas) == contract_tools
    assert len(schemas) == 30  # includes delegated-owner execution plus two human-principal-only operations
    for name, schema in schemas.items():
        assert schema["type"] == "object", name
        assert schema["additionalProperties"] is False, name


def test_task_intake_missing_required_field_returns_structured_validation_detail() -> None:
    with pytest.raises(RequestValidationError) as caught:
        validate_tool_arguments(
            "task.intake",
            {
                "objective": "probe",
                "expected_outcome": "probe",
                "requested_by": "michael",
                "executive_sponsor": "michael",
                "decision_owner": "michael",
                "authority_level": 0,
                "acceptance_test": "probe",
            },
        )
    details = caught.value.details
    assert {item["field"] for item in details} == {"accountable_agent"}
    assert details[0]["reason"] == "required"
    assert "secret" not in json.dumps(details)


def test_task_decompose_alias_is_validation_failed_not_resource_not_found() -> None:
    with pytest.raises(RequestValidationError) as caught:
        validate_tool_arguments("task.decompose", {"parent": "task-123", "work_packages": []})
    details = caught.value.details
    assert {item["field"] for item in details} == {"parent", "parent_task_id"}
    assert {item["reason"] for item in details} == {"unknown_field", "required"}


def test_agentops_recommend_valid_and_invalid_requests_share_public_contract() -> None:
    assert validate_tool_arguments("agentops.recommend", {"agent_id": "cos"}) == {"agent_id": "cos"}
    with pytest.raises(RequestValidationError) as caught:
        validate_tool_arguments("agentops.recommend", {"agent_id": "cos", "repeated_failures": "3"})
    assert {item["field"] for item in caught.value.details} == {"repeated_failures"}


def test_bridge_validation_error_payload_is_safe_and_actionable() -> None:
    exc = RequestValidationError([{"field": "accountable_agent", "reason": "required"}])
    payload = bridge._safe_error(exc)
    assert payload == {
        "ok": False,
        "runtime_version": "4.0.0",
        "error": "validation_failed",
        "details": [{"field": "accountable_agent", "reason": "required"}],
    }


def test_canonical_task_identifier_resolves_through_shared_ledger_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MESH_COS_KILL_SWITCH", "false")
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    task = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "lookup contract",
            "expected_outcome": "same task resolves everywhere",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cos",
            "decision_owner": "michael",
            "authority_level": 0,
            "acceptance_test": "same canonical identifier",
        },
    )
    task_id = task["task_id"]
    assert runtime.call_agent("cos", "task.get", {"task_id": task_id})["task_id"] == task_id
    assert runtime.call_agent("cos", "task.decompose", {"parent_task_id": task_id, "work_packages": []}) == []
    assert runtime.call_agent("cos", "task.check_in", {"task_id": task_id, "note": "probe"})["task_id"] == task_id
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        transitioned = runtime.call_agent("cos", "task.transition", {"task_id": task_id, "target": target})
        assert transitioned["task_id"] == task_id
    completed = runtime.call_agent(
        "cos",
        "task.complete",
        {"task_id": task_id, "outcome": "done", "evidence": ["synthetic://completion"]},
    )
    assert completed["task_id"] == task_id
    assert completed["status"] == TaskStatus.COMPLETED.value
    assert completed["verified_at"] is None
    verified = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": task_id,
            "passed": True,
            "reason": "acceptance passed",
            "evidence_references": ["synthetic://verification"],
        },
    )
    assert verified["task_id"] == task_id
    assert verified["status"] == TaskStatus.VERIFIED.value


def test_declared_skill_has_governed_handoff_and_skill_errors_are_distinct(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MESH_COS_KILL_SWITCH", "false")
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    granted = runtime.call_agent(
        "cos",
        "skills.invoke_governed",
        {
            "capability": "mesh-ppmd-bot",
            "payload": {"task_id": "synthetic-task", "authority_level": 0},
        },
    )
    assert granted["status"] == "AUTHORIZED"
    assert granted["execution_mode"] == "CHATGPT_SKILL_HANDOFF"
    assert granted["agent_id"] == "cos"
    assert granted["capability"] == "mesh-ppmd-bot"
    assert granted["payload"]["task_id"] == "synthetic-task"
    assert ledger.list_records("audit_event_v2")[-1]["capability_tool"] == "mesh-ppmd-bot"

    with pytest.raises(KeyError):
        runtime.call_agent("cos", "skills.invoke_governed", {"capability": "does-not-exist", "payload": {}})
    with pytest.raises(PermissionError):
        runtime.call_agent("cos", "skills.invoke_governed", {"capability": "mesh-firm-360", "payload": {}})


def test_all_ten_agent_identities_are_server_bound_and_human_tools_remain_absent(tmp_path: Path) -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    assert set(policy.contract["agent_tool_allowlists"]) == EXPECTED_AGENTS
    for agent_id in sorted(EXPECTED_AGENTS):
        values = {
            "MESH_COS_KILL_SWITCH": "false",
            "MESH_COS_AGENT_ID": agent_id,
            "MESH_COS_LEDGER_PATH": str(tmp_path / f"{agent_id}.sqlite3"),
        }
        response = bridge.execute_request(
            {"tool_name": "registry.get_agent", "arguments": {"agent_id": agent_id}},
            env=values,
            runtime_factory=MCPRuntime,
        )
        assert response["agent_id"] == agent_id
        allowed = set(policy.allowed_tools(agent_id))
        assert "approval.record_decision" not in allowed
        assert "reliability.human_override" not in allowed
        if agent_id != "cos":
            assert "task.verify" not in allowed
