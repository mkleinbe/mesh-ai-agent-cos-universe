from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.agentops import AgentOpsEvaluator
from mesh_cos.answer_desk import AnswerDeskService, decide
from mesh_cos.audit import AuditEvent
from mesh_cos.conflict import ConflictService
from mesh_cos.contracts import agent_record_contract, validate_runtime_contract
from mesh_cos.ledger import TaskLedger
from mesh_cos.metrics import MetricsService
from mesh_cos.models import AuthorityLevel, Delegation, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.reliability import ExecutionPolicy, ReplayManager
from mesh_cos.slack import AnswerDeskSlackService, SlackCoordinator, SlackInboundService, SlackWebClient
from mesh_cos.workforce import ChiefOfStaffWorkforceManager

ROOT = Path(__file__).resolve().parents[2]


def test_agent_record_runtime_contract_includes_created_and_updated_timestamps() -> None:
    registry = load_registry(ROOT / "agents" / "registry.json")
    record = agent_record_contract(registry["cro"])
    assert record["created_at"]
    assert record["updated_at"]
    validate_runtime_contract("agent-record", record, ROOT / "contracts")


def test_audit_event_matches_full_event_contract_including_event_version() -> None:
    event = AuditEvent("delegation_created", "cos", "T1", "corr-1", 3, "D1").to_dict()
    assert event["event_version"] == "mesh.cos.agent-event.v1"
    validate_runtime_contract("agent-event", event, ROOT / "contracts")


def test_material_conflict_uses_full_source_authority_contract() -> None:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake("Decide pursuit", "Decision", "m", "m", "cos", "m", AuthorityLevel.L3, "decision recorded")
    conflicts = ConflictService(ledger)
    conflict = conflicts.open(
        task.task_id,
        "Strategic value versus margin",
        ["CRO prefers A", "CFO prefers B"],
        participants=["cro", "cfo"],
        uncontested_facts=["Both options are deliverable"],
        source_authority={"financial_calculation": "cfo", "commercial_evidence": "mesh-revenue-intelligence"},
        business_consequence="material pursuit decision",
        option_a={"label": "A"},
        option_b={"label": "B"},
        agent_positions={"cro": "A", "cfo": "B"},
        confidence="MEDIUM",
        reversibility="REVERSIBLE",
        cos_recommendation="A",
        reversal_condition="economics materially worsen",
    )
    validate_runtime_contract("conflict", conflict, ROOT / "contracts")
    decision = conflicts.decide(conflict["conflict_id"], owner="cos", disposition="A", reversal_condition="economics materially worsen")
    validate_runtime_contract("decision", decision, ROOT / "contracts")
    assert any(event["event_type"] == "conflict_decided" for event in ledger.list_events())


def test_answer_desk_supports_routing_approval_and_correction_tracking() -> None:
    routed = decide(
        known_fact=False,
        source_accessible=True,
        established_policy=False,
        reversible=True,
        requires_judgment=False,
        ceo_authority=False,
        requester_permissions=set(),
        functional_owner="cfo",
    )
    assert routed.disposition == "ROUTED"
    assert routed.routed_to == "cfo"
    approval = decide(
        known_fact=False,
        source_accessible=True,
        established_policy=False,
        reversible=False,
        requires_judgment=False,
        ceo_authority=False,
        requester_permissions=set(),
        approval_required=True,
    )
    assert approval.disposition == "APPROVAL_REQUIRED"

    ledger = TaskLedger()
    service = AnswerDeskService(ledger)
    service.handle(
        request_id="Q1",
        known_fact=True,
        source_accessible=True,
        established_policy=False,
        reversible=True,
        requires_judgment=False,
        ceo_authority=False,
        requester_permissions=set(),
    )
    service.record_correction("Q1", actor="cfo", reason="source refreshed")
    assert ledger.get_record("answer_desk", "Q1")["corrected"] is True


def test_slack_inbound_verifies_signature_freshness_and_answer_desk_is_separate() -> None:
    ledger = TaskLedger()
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, payload, token))
        return {"ok": True, "ts": "171234.567"}

    client = SlackWebClient("xoxb-test", transport=transport)
    coordinator = SlackCoordinator(ledger, "C0BRL4GCL3A")
    inbound = SlackInboundService(coordinator, signing_secret="secret")
    now = datetime.now(timezone.utc)
    timestamp = str(int(now.timestamp()))
    body = '{"type":"event_callback"}'
    signature = "v0=" + hmac.new(b"secret", f"v0:{timestamp}:{body}".encode(), hashlib.sha256).hexdigest()
    parsed = inbound.handle_request(
        "Ev1",
        "[UPDATE] T1\nAgent: cro\nAction: qualified\nEvidence: crm://1",
        timestamp=timestamp,
        body=body,
        signature=signature,
        now=now,
    )
    assert parsed and parsed["kind"] == "UPDATE"
    with pytest.raises(PermissionError):
        inbound.handle_request(
            "Ev2",
            "[UPDATE] T1\nAgent: cro\nAction: stale",
            timestamp=str(int((now - timedelta(minutes=10)).timestamp())),
            body=body,
            signature=signature,
            now=now,
        )

    answer_desk = AnswerDeskService(ledger)
    interface = AnswerDeskSlackService("CANSWER", answer_desk, client)
    result = interface.handle_question(
        "Q2",
        "What is policy X?",
        known_fact=True,
        source_accessible=True,
        established_policy=False,
        reversible=True,
        requires_judgment=False,
        ceo_authority=False,
        requester_permissions=set(),
    )
    assert result["disposition"] == "ANSWERED"
    assert calls[-1][1]["channel"] == "CANSWER"


def test_agentops_covers_required_signal_analysis_and_recommendations() -> None:
    ledger = TaskLedger()
    policy = json.loads((ROOT / "config" / "performance-policy.v1.json").read_text())
    evaluator = AgentOpsEvaluator(policy, ledger=ledger, window_size=5)
    service = ChiefOfStaffService(ledger)
    task = service.intake("o", "e", "m", "m", "cro", "m", AuthorityLevel.L1, "a")
    task.status = TaskStatus.IN_PROGRESS
    task.due_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    task.rework_count = 2
    ledger.save_task(task)
    ledger.save_record("tool_failure", "tf1", {"agent_id": "cro", "error_type": "TimeoutError"})
    ledger.save_record("execution_failure", "ef1", {"agent_id": "cro", "error_type": "ConnectionError"})
    evaluator.record("cro", task.task_id, "evidence_governance", 0.2, reason="missing source authority")
    signals = evaluator.analyze_signals(ledger.list_tasks())
    assert task.task_id in signals["missed_deadline_task_ids"]
    assert task.task_id in signals["rework_task_ids"]
    assert signals["error_taxonomy"]["ConnectionError"] == 1
    assert evaluator.recommend_for_signals("cro", repeated_tool_failures=3) == "RETRAIN_OR_REVISE"
    assert evaluator.recommend_for_signals("cro", workload_gap=True) == "BUILD_NEW_SPECIALIST"
    assert evaluator.recommend_for_signals("cro", retirement_candidate=True) == "RETIRE"


def test_reliability_records_partial_failure_replay_and_human_override() -> None:
    ledger = TaskLedger()
    replay = ReplayManager(ledger)
    replay.record_failure("effect-1", "T1", agent_id="cro", error=TimeoutError("timed out"), payload={"x": 1})
    result = replay.replay("effect-1", lambda: "ok", actor="cos", policy=ExecutionPolicy(max_attempts=1))
    assert result == "ok"
    assert replay.replay("effect-1", lambda: "different", actor="cos", policy=ExecutionPolicy(max_attempts=1)) == "ok"
    replay.record_failure("effect-2", "T2", agent_id="coo", error=ConnectionError("down"))
    overridden = replay.override("effect-2", actor="michael", disposition="cancel", reason="manual handling")
    assert overridden["status"] == "OVERRIDDEN"
    assert ledger.get_record("human_override", "effect-2")["actor"] == "michael"


def test_metrics_expose_exact_original_phase1_instrumentation_set() -> None:
    keys = set(MetricsService(TaskLedger()).summary())
    required = {
        "work_resolved_without_michael_rate",
        "questions_deflected_from_michael",
        "ceo_touches_per_completed_task",
        "first_pass_acceptance_rate",
        "rework_rate",
        "correct_escalation_rate",
        "false_escalation_rate",
        "missed_escalation_rate",
        "median_cycle_time_minutes",
        "stalled_task_rate",
        "verified_outcome_rate",
        "agent_failure_rate",
        "approval_median_time_minutes",
        "cross_agent_conflict_rate",
        "agent_conversation_loop_rate",
        "avg_contributors_per_task",
        "cost_per_verified_outcome",
    }
    assert required.issubset(keys)


def test_workforce_manager_keeps_delegated_work_visible_until_terminal() -> None:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    parent = cos.intake("Pursuit", "Decision", "m", "m", "cos", "m", AuthorityLevel.L3, "decision")
    child = cos.decompose(parent.task_id, [{"objective": "Qualify", "expected_outcome": "qualified", "accountable_agent": "cro", "acceptance_test": "evidence"}])[0]
    delegation = Delegation(
        "D1",
        child.task_id,
        "cos",
        "cro",
        "Qualify pursuit",
        "qualified evidence",
        "brief",
        ["evidence-backed"],
        "P1",
        AuthorityLevel.L3,
        "evidence",
    )
    manager = ChiefOfStaffWorkforceManager(ledger)
    manager.delegate(delegation, parent_authority=3, depth=1)
    assert ledger.get_record("delegation", "D1")["accountable_agent"] == "cro"
    assert ledger.get_task(child.task_id).status == TaskStatus.INTAKE
    recommendation = manager.recommend_portfolio_change("cro", "BUILD_NEW_SPECIALIST", "persistent workload gap")
    assert "human approval required" in recommendation["authority_boundary"]


def test_governed_adapter_registry_can_bind_existing_mesh_skills_without_reimplementation() -> None:
    registry = load_registry(ROOT / "agents" / "registry.json")
    adapters = GovernedAdapterRegistry(registry)
    available = {
        "mesh-revenue-intelligence": lambda payload: {"status": "ok", "payload": payload},
        "mesh-devils-advocate": lambda payload: {"status": "challenged", "payload": payload},
    }
    assert adapters.bind_available_skills(available) >= 2
    assert adapters.execute("cro", "mesh-revenue-intelligence", {"task_id": "T1"})["status"] == "ok"
    assert adapters.execute("cro", "mesh-devils-advocate", {"task_id": "T1"})["status"] == "challenged"
    assert adapters.execute("cos", "mesh-devils-advocate", {"task_id": "T1"})["status"] == "challenged"
    with pytest.raises(PermissionError):
        adapters.execute("cfo", "mesh-devils-advocate", {"task_id": "T1"})
