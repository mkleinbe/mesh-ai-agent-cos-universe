from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from mesh_cos.adapters import GovernedAdapterRegistry, SkillAdapter
from mesh_cos.agentops import AgentOpsEvaluator
from mesh_cos.approval import ApprovalService
from mesh_cos.contracts import agent_record_contract, validate_runtime_contract
from mesh_cos.ledger import TaskLedger
from mesh_cos.metrics import MetricsService
from mesh_cos.models import AuthorityLevel, Delegation, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.reliability import ExecutionLeaseManager, ExecutionPolicy, assert_runtime_enabled, execute_with_policy
from mesh_cos.slack import SlackCoordinator, SlackInboundService, SlackWebClient, verify_slack_request

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_objects_validate_against_canonical_contracts() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = service.intake(
        "Prepare pursuit recommendation", "Decision-ready recommendation", "michael", "michael",
        "cro", "michael", AuthorityLevel.L3, "evidence accepted", idempotency_key="intake:1",
    )
    validate_runtime_contract("task", task.to_dict(), ROOT / "contracts")

    delegation = Delegation(
        "D1", task.task_id, "cos", "cro", "Win qualified pursuit", "Decision-ready pursuit",
        "brief", ["evidence-backed"], "P1", AuthorityLevel.L3, "brief accepted",
        permitted_actions=["commercial_analysis"], prohibited_actions=["pricing_approval"],
        approval_gates=["pricing"],
    )
    validate_runtime_contract("delegation", delegation.to_dict(), ROOT / "contracts")

    registry = load_registry(ROOT / "agents" / "registry.json")
    validate_runtime_contract("agent-record", agent_record_contract(registry["cro"]), ROOT / "contracts")


def test_all_contract_examples_and_runtime_shapes_are_strict() -> None:
    for schema_path in sorted((ROOT / "contracts").glob("*.schema.json")):
        schema = json.loads(schema_path.read_text())
        assert schema.get("additionalProperties") is False
        assert "version" in schema.get("required", [])
        Draft202012Validator.check_schema(schema)


def test_cos_manages_work_graph_delegation_dependencies_and_reassignment() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    parent = service.intake(
        "Decide pursuit", "Go/no-go decision", "michael", "michael", "cos", "michael",
        AuthorityLevel.L3, "decision brief complete", idempotency_key="pursuit:42",
    )
    children = service.decompose(parent.task_id, [
        {"objective": "Commercial case", "expected_outcome": "Qualified opportunity", "accountable_agent": "cro", "acceptance_test": "evidence present"},
        {"objective": "Economics", "expected_outcome": "Margin scenario", "accountable_agent": "cfo", "acceptance_test": "economics validated"},
        {"objective": "Delivery feasibility", "expected_outcome": "Staffing feasible", "accountable_agent": "coo", "acceptance_test": "capacity verified"},
    ])
    assert len(children) == 3
    assert all(c.parent_task_id == parent.task_id for c in children)

    cfo_task = children[1]
    coo_task = children[2]
    cfo_task.dependencies = [coo_task.task_id]
    ledger.save_task(cfo_task)
    assert service.dependencies_ready(cfo_task.task_id) is False

    for state in [TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.QA]:
        service.advance(coo_task.task_id, state)
    service.complete(coo_task.task_id, outcome="capacity available", evidence=["resource://1"])
    service.verify(coo_task.task_id, lambda _: (True, "capacity verified"))
    service.close(coo_task.task_id)
    assert service.dependencies_ready(cfo_task.task_id) is True

    service.reassign(children[0].task_id, "cro", "cmo", reason="commercial owner unavailable")
    assert ledger.get_task(children[0].task_id).accountable_agent == "cmo"
    assert ledger.list_records("reassignment")


def test_cos_invokes_governed_functional_skill_adapter() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = service.intake("Qualify account", "Qualified evidence", "m", "m", "cro", "m", AuthorityLevel.L2, "qualified")
    registry = load_registry(ROOT / "agents" / "registry.json")
    adapters = GovernedAdapterRegistry(registry)
    adapters.register(SkillAdapter("cro", "mesh-revenue-intelligence", lambda payload: {"qualified": True, "task_id": payload["task_id"]}))
    result = service.invoke(task.task_id, adapters, capability="mesh-revenue-intelligence", payload={"task_id": task.task_id})
    assert result["qualified"] is True
    assert ledger.list_records("functional_invocation")[-1]["capability"] == "mesh-revenue-intelligence"


def test_approval_is_persistent_audited_and_drives_task_state() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = service.intake("Approve price", "Authorized price", "cro", "michael", "cro", "michael", AuthorityLevel.L4, "approval recorded")
    for state in [TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
        service.advance(task.task_id, state)
    approvals = ApprovalService(ledger)
    approval = approvals.request(task.task_id, "cro", "michael", AuthorityLevel.L4, "pricing")
    assert ledger.get_task(task.task_id).status == TaskStatus.AWAITING_APPROVAL
    approvals.decide(approval.approval_id, actor="michael", approved=True, reason="approved")
    assert ledger.get_task(task.task_id).status == TaskStatus.READY_FOR_ACTION
    assert any(e["event_type"].startswith("approval_") for e in ledger.list_events())


def test_slack_inbound_has_freshness_dedupe_parser_thread_and_approval_notification() -> None:
    ledger = TaskLedger()
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, payload, token))
        return {"ok": True, "ts": "171234.567"}

    client = SlackWebClient("xoxb-test", transport=transport)
    coordinator = SlackCoordinator(ledger, "C0BRL4GCL3A")
    mapping = coordinator.ensure_thread("T1", client, "[ASSIGN] T1\nAgent: cro\nAction: qualify")
    assert mapping["thread_ts"] == "171234.567"
    coordinator.notify_approval("T1", client, "michael", "pricing")
    assert calls[-1][1]["thread_ts"] == "171234.567"

    now = datetime.now(timezone.utc)
    timestamp = str(int(now.timestamp()))
    body = '{"type":"event_callback"}'
    import hashlib, hmac
    signature = "v0=" + hmac.new(b"secret", f"v0:{timestamp}:{body}".encode(), hashlib.sha256).hexdigest()
    assert verify_slack_request("secret", timestamp, body, signature, now=now)
    stale = str(int((now - timedelta(minutes=10)).timestamp()))
    assert not verify_slack_request("secret", stale, body, signature, now=now)

    inbound = SlackInboundService(coordinator)
    parsed = inbound.handle("Ev1", "[UPDATE] T1\nAgent: cro\nAction: qualified\nEvidence: crm://1")
    assert parsed["kind"] == "UPDATE"
    assert inbound.handle("Ev1", "[UPDATE] T1\nAgent: cro\nAction: duplicate") is None


def test_agentops_is_durable_supports_rolling_windows_workload_and_health_changes() -> None:
    ledger = TaskLedger()
    policy = json.loads((ROOT / "config" / "performance-policy.v1.json").read_text())
    evaluator = AgentOpsEvaluator(policy, ledger=ledger, window_size=5)
    for i in range(6):
        evaluator.record("cro", f"T{i}", "outcome_achievement", 0.95, reason="verified")
    scorecard = evaluator.scorecard("cro")
    assert scorecard["event_count"] == 5
    assert ledger.list_records("performance_event")
    assert ledger.get_record("scorecard", "cro")["weighted_score"] > 0.9
    assert {"CONTINUE", "WATCH", "DECREASE_ROUTING", "RESTRICT", "QUARANTINE", "RETRAIN_OR_REVISE", "RETIRE", "INCREASE_ROUTING", "BUILD_NEW_SPECIALIST"}.issubset(evaluator.supported_recommendations())

    service = ChiefOfStaffService(ledger)
    t1 = service.intake("a", "a", "m", "m", "cro", "m", AuthorityLevel.L1, "a")
    t2 = service.intake("b", "b", "m", "m", "cro", "m", AuthorityLevel.L1, "b")
    for task in [t1, t2]:
        task.status = TaskStatus.IN_PROGRESS
        task.next_check_at = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        ledger.save_task(task)
    observation = evaluator.observe_tasks(ledger.list_tasks(), max_concurrency={"cro": 1})
    assert len(observation["stalled_task_ids"]) == 2
    assert observation["overloaded_agents"] == ["cro"]
    evaluator.record_health_change("cro", "ACTIVE", "WATCH", "repeated stalls", approved_by="cos")
    assert ledger.get_record("registry_change", "cro")["to_state"] == "WATCH"


def test_reliability_timeout_leases_kill_switch_and_duplicate_intake() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    first = service.intake("o", "e", "m", "m", "cro", "m", AuthorityLevel.L1, "a", idempotency_key="same")
    second = service.intake("o", "e", "m", "m", "cro", "m", AuthorityLevel.L1, "a", idempotency_key="same")
    assert first.task_id == second.task_id

    leases = ExecutionLeaseManager(ledger)
    assert leases.acquire("T1", "worker-a", ttl_seconds=60)
    assert not leases.acquire("T1", "worker-b", ttl_seconds=60)
    leases.release("T1", "worker-a")
    assert leases.acquire("T1", "worker-b", ttl_seconds=60)

    with pytest.raises(TimeoutError):
        execute_with_policy(lambda: __import__("time").sleep(0.05), ExecutionPolicy(max_attempts=1, timeout_seconds=0.01))
    with pytest.raises(RuntimeError):
        assert_runtime_enabled({"MESH_COS_KILL_SWITCH": "true"})


def test_metrics_cover_phase1_operating_requirements() -> None:
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = service.intake("o", "e", "m", "m", "cro", "m", AuthorityLevel.L2, "a")
    for state in [TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.QA]:
        service.advance(task.task_id, state)
    service.complete(task.task_id, outcome="done", evidence=["e://1"])
    service.verify(task.task_id, lambda _: (True, "ok"))
    service.close(task.task_id)
    ledger.save_record("answer_desk", "Q1", {"disposition": "ANSWERED"})
    ledger.save_record("answer_desk", "Q2", {"disposition": "ESCALATED"})
    ledger.save_record("cost", task.task_id, {"task_id": task.task_id, "amount": 12.5})
    summary = MetricsService(ledger).summary()
    expected = {
        "verified_outcomes", "tasks_resolved_without_ceo", "ceo_time_avoided_minutes",
        "first_pass_acceptance_rate", "rework_rate", "correct_escalations", "false_escalations",
        "missed_escalations", "median_cycle_time_minutes", "stalled_task_rate", "execution_failures",
        "approval_median_time_minutes", "conflicts", "coordination_loops", "avg_contributors_per_task",
        "cost_per_verified_outcome", "answer_desk_deflection_rate",
    }
    assert expected.issubset(summary)
    assert summary["verified_outcomes"] == 1
    assert summary["cost_per_verified_outcome"] == 12.5


def test_end_to_end_pursuit_flow_uses_actual_services() -> None:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    registry = load_registry(ROOT / "agents" / "registry.json")
    adapters = GovernedAdapterRegistry(registry)
    adapters.register(SkillAdapter("cro", "mesh-revenue-intelligence", lambda p: {"evidence": "ri://42", "qualified": True}))
    parent = cos.intake("Pursuit decision", "Decision brief", "michael", "michael", "cos", "michael", AuthorityLevel.L3, "brief accepted")
    child = cos.decompose(parent.task_id, [{"objective": "Qualify", "expected_outcome": "Qualified", "accountable_agent": "cro", "acceptance_test": "source evidence"}])[0]
    result = cos.invoke(child.task_id, adapters, capability="mesh-revenue-intelligence", payload={"task_id": child.task_id})
    for state in [TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.QA]:
        cos.advance(child.task_id, state)
    cos.complete(child.task_id, outcome="qualified", evidence=[result["evidence"]])
    cos.verify(child.task_id, lambda t: (bool(t.outcome_evidence), "source evidence present"))
    cos.close(child.task_id)
    assert ledger.get_task(child.task_id).status == TaskStatus.CLOSED
    assert ledger.list_records("functional_invocation")
    assert ledger.list_events()
