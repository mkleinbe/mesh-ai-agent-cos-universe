from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

import pytest

from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.mcp_runtime import MCPRuntime, ReplayExecutorRegistry
from mesh_cos.models import AuthorityLevel, TaskRecord, TaskStatus


def make_task(
    task_id: str = "T1",
    owner: str = "cro",
    *,
    parent_task_id: str | None = None,
) -> TaskRecord:
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
        parent_task_id=parent_task_id,
    )


def test_replay_executor_registry_validates_keys_and_resolution() -> None:
    registry = ReplayExecutorRegistry()
    with pytest.raises(ValueError, match="replay_key"):
        registry.register("", lambda payload: payload)
    with pytest.raises(PermissionError, match="server-registered"):
        registry.resolve("missing")
    registry.register("ok", lambda payload: payload["value"])
    assert registry.resolve("ok")({"value": 3}) == 3


def test_runtime_rejects_handler_contract_drift() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file()
    contract = deepcopy(policy.contract)
    contract["tools"] = contract["tools"][:-1]
    drifted = WorkspaceAgentMCPPolicy(contract)
    with pytest.raises(ValueError, match="handler drift"):
        MCPRuntime(TaskLedger(), policy=drifted)


def test_agent_dispatch_fails_closed_if_an_allowed_handler_is_missing() -> None:
    runtime = MCPRuntime(TaskLedger())
    runtime._handlers.pop("registry.get_agent")
    with pytest.raises(PermissionError, match="Unknown MCP tool"):
        runtime.call_agent("cro", "registry.get_agent", {"agent_id": "cro"})


def test_human_dispatch_requires_identity_and_only_human_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="Authenticated human"):
        runtime.call_human("", "approval.record_decision", {})
    with pytest.raises(PermissionError, match="human-authorized"):
        runtime.call_human("michael", "task.get", {"task_id": "T"})

    monkeypatch.setattr(
        WorkspaceAgentMCPPolicy,
        "authorize_human",
        lambda self, _: {"name": "unexpected"},
    )
    with pytest.raises(PermissionError, match="not authorized"):
        runtime.call_human("michael", "unexpected", {})


def test_agent_record_and_task_write_guards_fail_closed() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="Unknown agent principal"):
        runtime._agent_record("unknown")
    runtime.registry["cro"]["runtime_health"] = "QUARANTINED"
    with pytest.raises(PermissionError, match="not routable"):
        runtime._agent_record("cro")
    runtime.registry["cro"]["runtime_health"] = "ACTIVE"
    with pytest.raises(KeyError):
        runtime._require_task_write_access("cro", "missing")
    with pytest.raises(KeyError):
        runtime._require_task_owner_access("cro", "missing")
    runtime.ledger.save_task(make_task())
    with pytest.raises(PermissionError, match="canonical accountable owner"):
        runtime._require_task_owner_access("cos", "T1")
    assert runtime._require_task_owner_access("cro", "T1").task_id == "T1"


def test_registry_and_task_read_handlers_cover_present_and_missing_records() -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    assert runtime.call_agent("cro", "registry.get_agent", {"agent_id": "cro"})["agent_id"] == "cro"
    with pytest.raises(KeyError):
        runtime._registry_get_agent("cro", {"agent_id": "missing"})
    agents = runtime._registry_list_agents("cos", {})
    assert len(agents) == 10
    assert all(record["agent_id"] != "devils-advocate" for record in agents)
    assert any(record["agent_id"] == "message-ops" for record in agents)
    assert runtime._task_get("cro", {"task_id": "missing"}) is None
    ledger.save_task(make_task())
    assert runtime._task_get("cro", {"task_id": "T1"})["task_id"] == "T1"
    assert runtime._task_list("cro", {})[0]["task_id"] == "T1"


def test_task_handler_serialization_and_owner_scoping(monkeypatch: pytest.MonkeyPatch) -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    task = make_task()
    task.status = TaskStatus.IN_PROGRESS
    ledger.save_task(task)

    monkeypatch.setattr(runtime.cos, "record_checkin", lambda *args, **kwargs: {"record_id": "C1"})
    assert runtime._task_check_in("cro", {"task_id": "T1", "note": "ok"}) == {"record_id": "C1"}

    monkeypatch.setattr(runtime.cos, "complete", lambda *args, **kwargs: make_task("T1"))
    assert runtime._task_complete("cro", {"task_id": "T1", "outcome": "done"})["task_id"] == "T1"

    monkeypatch.setattr(runtime.cos, "reassign", lambda *args, **kwargs: make_task("T1", "cfo"))
    assert runtime._task_reassign("cos", {"task_id": "T1", "expected_owner": "cro", "new_owner": "cfo", "reason": "load"})["accountable_agent"] == "cfo"

    monkeypatch.setattr(runtime.cos, "remediate_stalled", lambda *args, **kwargs: make_task("T1"))
    assert runtime._task_remediate_stall("cos", {"task_id": "T1"})["task_id"] == "T1"

    monkeypatch.setattr(runtime.cos, "record_verification_result", lambda *args, **kwargs: make_task("T1"))
    assert runtime._task_verify("cro", {"task_id": "T1", "passed": False, "reason": "no", "evidence_references": []})["task_id"] == "T1"

    monkeypatch.setattr(runtime.cos, "decompose", lambda *args, **kwargs: [make_task("C1")])
    assert runtime._task_decompose("cro", {"parent_task_id": "T1", "work_packages": []})[0]["task_id"] == "C1"
    with pytest.raises(PermissionError, match="canonical accountable owner"):
        runtime._task_decompose("cos", {"parent_task_id": "T1", "work_packages": []})


def test_delegation_handler_derives_canonical_parent_child_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    parent = make_task("P1", "cos")
    child = make_task("T1", "cro", parent_task_id="P1")
    ledger.save_task(parent)
    ledger.save_task(child)
    captured = {}

    def delegate(value, **kwargs):
        captured["delegation"] = value
        captured.update(kwargs)
        ledger.save_record("delegation", value.delegation_id, value.to_dict())
        return value.to_dict()

    monkeypatch.setattr(runtime.workforce, "delegate", delegate)
    payload = {
        "delegation": {
            "delegation_id": "D1",
            "task_id": "T1",
            "parent_task_id": "P1",
            "delegating_agent": "spoof",
            "accountable_agent": "cro",
            "business_objective": "sell",
            "expected_outcome": "decision",
            "deliverable": "brief",
            "success_criteria": ["supported"],
            "priority": "P1",
            "authority_level": 2,
            "acceptance_test": "supported",
        },
        "parent_authority": 2,
        "depth": 1,
        "ancestry": ["cos"],
    }
    result = runtime._delegation_create("cos", payload)
    assert result["delegating_agent"] == "cos"
    assert result["authority_level"] == 2
    assert captured["parent_authority"] == 2
    assert captured["depth"] == 1
    assert captured["ancestry"] == ["cos"]
    assert runtime.ledger.get_record("owner_execution_route", "D1")["accountable_owner"] == "cro"

    with pytest.raises(PermissionError, match="direct child"):
        runtime._delegation_create("cro", payload)


def test_service_adapter_handlers_return_serialized_results(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())

    monkeypatch.setattr(runtime.approvals, "request", lambda *args, **kwargs: SimpleNamespace(to_dict=lambda: {"approval_id": "A1"}))
    assert runtime._approval_request("cro", {"task_id": "T1", "approval_owner": "michael", "authority_level": 4, "action": "pricing"}) == {"approval_id": "A1"}
    assert runtime._approval_get("cro", {"approval_id": "missing"}) is None

    monkeypatch.setattr(runtime.conflicts, "open", lambda *args, **kwargs: {"conflict_id": "C1"})
    assert runtime._conflict_open("cro", {"task_id": "T1", "summary": "conflict", "disputed_points": ["x"]}) == {"conflict_id": "C1"}
    monkeypatch.setattr(runtime.conflicts, "decide", lambda *args, **kwargs: {"decision_id": "D1", "owner": kwargs["owner"]})
    assert runtime._conflict_decide("cos", {"conflict_id": "C1", "owner": "spoof", "disposition": "resolve", "reversal_condition": "new facts"})["owner"] == "cos"

    monkeypatch.setattr(runtime.agentops, "record", lambda *args, **kwargs: None)
    assert runtime._agentops_record_event("agentops", {"agent_id": "cro", "task_id": "T1", "category": "outcome_achievement", "value": 1}) == {"recorded": True}
    monkeypatch.setattr(runtime.agentops, "scorecard", lambda agent_id: {"agent_id": agent_id, "weighted_score": 1})
    assert runtime._agentops_score("agentops", {"agent_id": "cro"})["weighted_score"] == 1
    monkeypatch.setattr(runtime.agentops, "recommend_for_signals", lambda agent_id, **kwargs: "CONTINUE")
    assert runtime._agentops_recommend("agentops", {"agent_id": "cro"}) == {"agent_id": "cro", "recommendation": "CONTINUE"}

    monkeypatch.setattr(runtime.answer_desk, "handle", lambda **kwargs: SimpleNamespace(disposition="ANSWERED", reason="known", routed_to=None))
    assert runtime._answer_desk_resolve("answer-desk", {"request_id": "R1", "source_accessible": True, "evidence_sufficient": True, "established_policy": True, "reversible": True, "judgment_required": False, "ceo_authority_required": False})["disposition"] == "ANSWERED"

    monkeypatch.setattr(runtime.adapters, "execute", lambda agent_id, capability, payload: {"agent_id": agent_id, "capability": capability, "payload": payload})
    assert runtime._skill_invoke("cro", {"capability": "mesh-revenue-intelligence", "payload": {"x": 1}})["agent_id"] == "cro"
    assert runtime._skill_invoke("cro", {"capability": "mesh-devils-advocate", "payload": {"x": 1}})["capability"] == "mesh-devils-advocate"
    assert runtime._skill_invoke("cro", {"capability": "mesh-message-operations", "payload": {"x": 1}})["capability"] == "mesh-message-operations"

    monkeypatch.setattr(runtime.metrics, "summary", lambda: {"verified_outcomes": 1})
    assert runtime._metrics_snapshot("cos", {}) == {"verified_outcomes": 1}


def test_governance_handlers_override_spoofed_agent_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())
    captured_decision = {}
    captured_event = {}

    def decision(self, **kwargs):
        captured_decision.update(kwargs)
        return kwargs

    def event(self, **kwargs):
        captured_event.update(kwargs)
        return kwargs

    monkeypatch.setattr(GovernanceJournal, "record_decision", decision)
    monkeypatch.setattr(GovernanceJournal, "record_event", event)
    runtime._governance_record_decision("cro", {"agent_id": "michael", "agent_role": "CEO", "skill_agent_version": "fake"})
    assert captured_decision["agent_id"] == "cro"
    assert captured_decision["agent_role"] == "CRO"
    assert captured_decision["skill_agent_version"] == "1.0.0"

    runtime._governance_record_event("cro", {"actor_id": "michael", "actor_role": "CEO", "actor_type": "HUMAN", "skill_agent_version": "fake"})
    assert captured_event["actor_id"] == "cro"
    assert captured_event["actor_role"] == "CRO"
    assert captured_event["actor_type"] == "AGENT"


def test_audit_chain_handler_reports_empty_chain_valid() -> None:
    assert MCPRuntime(TaskLedger())._governance_verify_audit_chain("cos", {}) == {"valid": True, "event_count": 0}


def test_replay_handler_fails_closed_for_missing_and_nonreplayable_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MESH_COS_KILL_SWITCH", "false")
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    with pytest.raises(KeyError):
        runtime._reliability_replay("cos", {"effect_id": "missing"})
    ledger.save_record("execution_failure", "E1", {"effect_id": "E1", "status": "FAILED", "payload": {}})
    with pytest.raises(PermissionError, match="does not name"):
        runtime._reliability_replay("cos", {"effect_id": "E1"})


def test_human_override_success_uses_authenticated_principal(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = MCPRuntime(TaskLedger())
    monkeypatch.setattr(runtime.replay, "override", lambda effect_id, **kwargs: {"effect_id": effect_id, **kwargs})
    result = runtime.call_human("michael", "reliability.human_override", {"effect_id": "E1", "actor": "spoof", "disposition": "close", "reason": "manual"})
    assert result["actor"] == "michael"
