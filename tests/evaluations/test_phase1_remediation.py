import hashlib
import hmac
import json
from pathlib import Path

import pytest

from mesh_cos.adapters import AdapterRegistry, FunctionalAdapter
from mesh_cos.agentops import AgentOpsEvaluator
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.security import assert_agent_invocation_allowed
from mesh_cos.slack import SlackCoordinator, verify_slack_signature

ROOT = Path(__file__).resolve().parents[2]


def test_contract_and_registry_are_single_runtime_source_of_truth():
    registry = load_registry(ROOT / "agents" / "registry.json")
    assert registry["cro"]["decision_authority"] == 3
    assert registry["devils-advocate"]["skills"] == ["mesh-devils-advocate"]
    assert len(registry) == 11


def test_ledger_persists_all_consequential_record_types():
    ledger = TaskLedger()
    for kind in ["delegation", "decision", "conflict", "approval", "registry_change", "performance_event", "scorecard"]:
        record_id = f"{kind}-1"
        ledger.save_record(kind, record_id, {"id": record_id, "kind": kind})
        assert ledger.get_record(kind, record_id)["kind"] == kind


def test_cos_orchestrates_to_verified_outcome_and_records_acceptance():
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = service.intake(
        objective="Prepare governed pursuit recommendation",
        expected_outcome="Decision-ready recommendation",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        authority_level=AuthorityLevel.L3,
        acceptance_test="recommendation_has_evidence",
    )
    service.advance(task.task_id, TaskStatus.TRIAGED)
    service.advance(task.task_id, TaskStatus.PLANNED)
    service.advance(task.task_id, TaskStatus.ASSIGNED)
    service.advance(task.task_id, TaskStatus.IN_PROGRESS)
    service.advance(task.task_id, TaskStatus.QA)
    service.complete(task.task_id, outcome="Recommendation prepared", evidence=["evidence://pursuit/1"])
    service.verify(task.task_id, lambda t: (True, "evidence accepted"))
    reloaded = ledger.get_task(task.task_id)
    assert reloaded.status == TaskStatus.VERIFIED
    verification = ledger.get_record("verification", task.task_id)
    assert verification["passed"] is True
    assert verification["evidence"] == ["evidence://pursuit/1"]


def test_failed_acceptance_test_routes_to_rework():
    ledger = TaskLedger()
    service = ChiefOfStaffService(ledger)
    task = service.intake("o", "e", "m", "m", "cro", "m", AuthorityLevel.L2, "must_pass")
    for state in [TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.QA]:
        service.advance(task.task_id, state)
    service.complete(task.task_id, outcome="done", evidence=["evidence://1"])
    service.verify(task.task_id, lambda _: (False, "quality gate failed"))
    assert ledger.get_task(task.task_id).status == TaskStatus.REWORK


def test_slack_signature_thread_mapping_and_durable_dedupe():
    ledger = TaskLedger()
    coordinator = SlackCoordinator(ledger, channel_id="C0BRL4GCL3A")
    mapping = coordinator.bind_thread("T-1", "171234.567")
    assert mapping["channel_id"] == "C0BRL4GCL3A"
    assert coordinator.thread_for("T-1")["thread_ts"] == "171234.567"
    assert coordinator.accept_event("Ev1") is True
    assert SlackCoordinator(ledger, channel_id="C0BRL4GCL3A").accept_event("Ev1") is False

    secret = "secret"
    timestamp = "12345"
    body = '{"type":"event_callback"}'
    digest = hmac.new(secret.encode(), f"v0:{timestamp}:{body}".encode(), hashlib.sha256).hexdigest()
    assert verify_slack_signature(secret, timestamp, body, f"v0={digest}")


def test_agentops_uses_versioned_policy_and_full_recommendation_set(tmp_path):
    policy = {
        "version": "perf.v1",
        "weights": {"outcome_achievement": 1.0},
        "thresholds": {"restrict_below": 0.3, "watch_below": 0.65, "increase_above": 0.9, "minimum_events_for_increase": 2},
    }
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(policy))
    evaluator = AgentOpsEvaluator.from_file(path)
    evaluator.record("cro", "T1", "outcome_achievement", 0.95)
    evaluator.record("cro", "T2", "outcome_achievement", 0.96)
    scorecard = evaluator.scorecard("cro")
    assert scorecard["weights_version"] == "perf.v1"
    assert scorecard["recommendation"] == "INCREASE_ROUTING"


def test_invocation_security_enforces_registry_allowlists():
    registry = {
        "cro": {
            "allowed_sources": ["revenue-intelligence"],
            "tools": ["crm-read"],
            "prohibited_actions": ["pricing_approval"],
        }
    }
    assert_agent_invocation_allowed(registry, "cro", source="revenue-intelligence", tool="crm-read")
    with pytest.raises(PermissionError):
        assert_agent_invocation_allowed(registry, "cro", source="private-dm")


def test_functional_adapter_registry_is_thin_and_governed():
    adapters = AdapterRegistry()
    adapters.register(FunctionalAdapter("cro", lambda payload: {"status": "ok", "payload": payload}))
    result = adapters.execute("cro", {"task_id": "T1"})
    assert result["status"] == "ok"
    with pytest.raises(KeyError):
        adapters.execute("unknown", {})
