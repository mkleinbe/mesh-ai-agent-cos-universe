from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_runtime import MCPRuntime, ReplayExecutorRegistry
from mesh_cos.models import AuthorityLevel, TaskRecord, TaskStatus

ROOT = Path(__file__).resolve().parents[2]


def make_task(task_id: str, owner: str = "cro") -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        objective="objective",
        expected_outcome="outcome",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent=owner,
        decision_owner="michael",
        authority_level=AuthorityLevel.L2,
        acceptance_test="accepted",
    )


def test_mcp_runtime_has_one_serialized_handler_per_contract_tool() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file(ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json")
    runtime = MCPRuntime(TaskLedger(), policy=policy)
    assert runtime.tool_names() == {tool["name"] for tool in policy.contract["tools"]}


def test_agent_calls_cannot_spoof_human_approval_or_override() -> None:
    ledger = TaskLedger()
    policy = WorkspaceAgentMCPPolicy.from_file(ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json")
    runtime = MCPRuntime(ledger, policy=policy)
    task = make_task("T1")
    task.status = TaskStatus.IN_PROGRESS
    ledger.save_task(task)

    approval = runtime.call_agent(
        "cos",
        "approval.request",
        {
            "task_id": "T1",
            "requested_by": "cos",
            "approval_owner": "michael",
            "authority_level": 4,
            "action": "pricing",
        },
    )
    assert approval["status"] == "PENDING"

    with pytest.raises(PermissionError):
        runtime.call_agent(
            "cos",
            "approval.record_decision",
            {
                "approval_id": approval["approval_id"],
                "actor": "michael",
                "approved": True,
                "reason": "spoof attempt",
            },
        )
    with pytest.raises(PermissionError):
        runtime.call_agent(
            "cos",
            "reliability.human_override",
            {"effect_id": "E1", "actor": "michael", "disposition": "close", "reason": "spoof"},
        )

    decided = runtime.call_human(
        "michael",
        "approval.record_decision",
        {
            "approval_id": approval["approval_id"],
            "actor": "not-michael",
            "approved": True,
            "reason": "explicit human approval",
        },
    )
    assert decided["status"] == "APPROVED"
    assert decided["decided_by"] == "michael"


def test_task_writes_are_scoped_to_canonical_accountable_owner() -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    task = make_task("T-cfo", owner="cfo")
    ledger.save_task(task)

    for unauthorized in ("cro", "cos"):
        with pytest.raises(PermissionError, match="accountable owner"):
            runtime.call_agent(unauthorized, "task.transition", {"task_id": "T-cfo", "target": "TRIAGED"})

    transitioned = runtime.call_agent("cfo", "task.transition", {"task_id": "T-cfo", "target": "TRIAGED"})
    assert transitioned["status"] == "TRIAGED"


def test_governance_actor_identity_is_server_derived() -> None:
    runtime = MCPRuntime(TaskLedger())
    event = runtime.call_agent(
        "cro",
        "governance.record_event",
        {
            "event_type": "commercial.reviewed",
            "event_category": "EXECUTION",
            "action": "REVIEW",
            "actor_id": "michael",
            "actor_role": "CEO",
            "task_id": None,
            "correlation_id": "corr-1",
            "authority_level": 2,
            "policy_rule_ids": ["test"],
            "capability_tool": "review",
            "target_resource": "opportunity",
            "source_system": "test",
            "input_summary": "review",
            "result_status": "SUCCESS",
            "output_summary": "reviewed",
            "evidence_references": [],
            "risk_severity": "LOW",
            "data_classification": "INTERNAL",
            "model_provider": None,
            "model_id_version": None,
            "skill_agent_version": "spoofed",
            "environment": "TEST",
            "retention_class": "GOVERNANCE_LONG_TERM",
        },
    )
    assert event["actor_id"] == "cro"
    assert event["actor_role"] == "CRO"
    assert event["skill_agent_version"] == "1.0.0"


def test_replay_is_remote_safe_and_uses_only_server_registered_executor(monkeypatch) -> None:
    monkeypatch.setenv("MESH_COS_KILL_SWITCH", "false")
    ledger = TaskLedger()
    executors = ReplayExecutorRegistry()
    executors.register("crm-write-v1", lambda payload: {"replayed": payload["record_id"]})
    runtime = MCPRuntime(ledger, replay_executors=executors)

    ledger.save_record(
        "execution_failure",
        "E1",
        {
            "effect_id": "E1",
            "task_id": "T1",
            "agent_id": "cos",
            "error_type": "ConnectionError",
            "error": "down",
            "payload": {"record_id": "R1"},
            "replay_key": "crm-write-v1",
            "status": "FAILED",
            "failed_at": "2026-08-17T00:00:00+00:00",
            "replayed_at": None,
            "overridden_at": None,
        },
    )
    assert runtime.call_agent("cos", "reliability.replay", {"effect_id": "E1"}) == {"replayed": "R1"}

    ledger.save_record(
        "execution_failure",
        "E2",
        {
            "effect_id": "E2",
            "task_id": "T1",
            "agent_id": "cos",
            "error_type": "ConnectionError",
            "error": "down",
            "payload": {},
            "replay_key": "unregistered",
            "status": "FAILED",
            "failed_at": "2026-08-17T00:00:00+00:00",
            "replayed_at": None,
            "overridden_at": None,
        },
    )
    with pytest.raises(PermissionError, match="registered replay executor"):
        runtime.call_agent("cos", "reliability.replay", {"effect_id": "E2", "callable": "os.system"})


def test_unknown_tools_and_human_tools_fail_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError):
        runtime.call_agent("cro", "unknown.tool", {})
    with pytest.raises(PermissionError):
        runtime.call_human("michael", "task.transition", {})
    with pytest.raises(KeyError):
        runtime.call_human(
            "michael",
            "reliability.human_override",
            {"effect_id": "missing", "disposition": "close", "reason": "none"},
        )
