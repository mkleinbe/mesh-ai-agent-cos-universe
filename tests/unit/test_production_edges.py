from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mesh_cos.agentops import AgentOpsEvaluator, stalled
from mesh_cos.approval import ApprovalService
from mesh_cos.audit import AuditEvent
from mesh_cos.governance import GovernanceJournal, GovernanceMirror
from mesh_cos.ledger import TaskLedger
from mesh_cos.lifecycle import transition
from mesh_cos.models import AuthorityLevel, TaskRecord, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.reliability import ReplayManager
from mesh_cos.slack import verify_slack_request
from mesh_cos.staffing import readiness


def task(task_id: str, status: TaskStatus = TaskStatus.INTAKE) -> TaskRecord:
    return TaskRecord(
        task_id=task_id,
        objective="objective",
        expected_outcome="outcome",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        status=status,
        authority_level=AuthorityLevel.L2,
        acceptance_test="accepted",
    )


def test_time_boundaries_normalize_naive_values_and_validate_age() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        readiness(
            capability_match=True,
            availability_checked_at=datetime.now(timezone.utc).isoformat(),
            max_age_days=-1,
            rate_valid=True,
            contracting_ready=True,
            availability_confirmed=True,
        )

    item = task("T", TaskStatus.IN_PROGRESS)
    item.next_check_at = (datetime.now() - timedelta(minutes=2)).replace(microsecond=0).isoformat()
    assert stalled(item, now=datetime.now()) is True

    policy = {
        "version": "edge-v1",
        "weights": {"outcome_achievement": 1.0},
        "thresholds": {
            "restrict_below": 0.3,
            "watch_below": 0.65,
            "increase_above": 0.9,
            "minimum_events_for_increase": 2,
        },
    }
    evaluator = AgentOpsEvaluator(policy)
    item.due_at = (datetime.now() - timedelta(days=1)).replace(microsecond=0).isoformat()
    signals = evaluator.analyze_signals([item], now=datetime.now())
    assert signals["missed_deadline_task_ids"] == ["T"]
    assert evaluator.observe_tasks([item], now=datetime.now())["stalled_task_ids"] == ["T"]

    secret = "secret"
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    body = "{}"
    import hashlib
    import hmac

    signature = "v0=" + hmac.new(
        secret.encode(), f"v0:{timestamp}:{body}".encode(), hashlib.sha256
    ).hexdigest()
    assert verify_slack_request(secret, timestamp, body, signature, now=datetime.now())


def test_approval_service_preserves_states_when_transition_is_not_applicable() -> None:
    ledger = TaskLedger()
    approval_service = ApprovalService(ledger)
    untouched = task("T")
    ledger.save_task(untouched)

    approval = approval_service.request(
        "T", "cos", "michael", AuthorityLevel.L4, "pricing"
    )
    assert ledger.get_task("T").status == TaskStatus.INTAKE

    approval_service.decide(
        approval.approval_id, actor="michael", approved=True, reason="approved"
    )
    stored = ledger.get_task("T")
    assert stored.status == TaskStatus.INTAKE
    assert stored.approval_status == "APPROVED"


def test_replay_corruption_and_terminal_override_states_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MESH_COS_KILL_SWITCH", "false")
    ledger = TaskLedger()
    replay = ReplayManager(ledger)

    replay.record_failure("corrupt", "T", agent_id="cro", error=RuntimeError("x"))
    corrupted = ledger.get_record("execution_failure", "corrupt")
    corrupted["status"] = "REPLAYED"
    ledger.save_record("execution_failure", "corrupt", corrupted)
    with pytest.raises(RuntimeError, match="stored result"):
        replay.replay("corrupt", lambda: 1, actor="cos")

    replay.record_failure("replayed", "T", agent_id="cro", error=RuntimeError("x"))
    assert replay.replay("replayed", lambda: 1, actor="cos") == 1
    with pytest.raises(RuntimeError, match="already been replayed"):
        replay.override("replayed", actor="michael", disposition="close", reason="done")

    replay.record_failure("overridden", "T", agent_id="cro", error=RuntimeError("x"))
    replay.override("overridden", actor="michael", disposition="close", reason="manual")
    with pytest.raises(RuntimeError, match="already been overridden"):
        replay.override("overridden", actor="michael", disposition="close", reason="again")


def test_governance_null_mirror_and_taskless_events_are_safe() -> None:
    mirror = GovernanceMirror()
    assert mirror.mirror_decision({}) is None
    assert mirror.mirror_event({}) is None

    ledger = TaskLedger()
    journal = GovernanceJournal(ledger, mirror)
    record = journal.record_event(
        event_type="system.preflight",
        event_category="GOVERNANCE",
        action="CHECK",
        actor_type="SERVICE",
        actor_id="preflight",
        actor_role="runtime preflight",
        task_id=None,
        correlation_id="corr",
        authority_level=0,
        policy_rule_ids=["p1"],
        capability_tool="preflight",
        target_resource="runtime",
        source_system="repository",
        input_summary="check",
        result_status="SUCCESS",
        output_summary="ok",
        evidence_references=[],
        risk_severity="LOW",
        data_classification="INTERNAL",
        model_provider=None,
        model_id_version=None,
        skill_agent_version="1.0.0",
        environment="TEST",
        retention_class="GOVERNANCE_LONG_TERM",
    )
    assert record["task_id"] is None
    assert ledger.list_events() == []


def test_nonlegacy_event_does_not_bridge_and_record_order_is_insertion_order() -> None:
    ledger = TaskLedger()
    ledger.save_record("order", "z", {"id": "first"})
    ledger.save_record("order", "a", {"id": "second"})
    assert [item["id"] for item in ledger.list_records("order")] == ["first", "second"]

    event = {
        "event_id": "E-v2",
        "task_id": "T",
        "idempotency_key": "E-v2",
        "version": "mesh.cos.agent-event.v2",
    }
    assert ledger.record_event(event)
    assert ledger.list_records("audit_event_v2") == []


def test_orchestration_handles_nontransitioning_remediation_and_escalation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MESH_COS_KILL_SWITCH", "false")
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)

    blocked = task("blocked", TaskStatus.BLOCKED)
    blocked.next_check_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    ledger.save_task(blocked)
    result = cos.remediate_stalled("blocked", new_owner="cro", reason="still blocked")
    assert result.status == TaskStatus.BLOCKED
    assert result.accountable_agent == "cro"

    planned = task("planned")
    transition(planned, TaskStatus.TRIAGED)
    transition(planned, TaskStatus.PLANNED)
    ledger.save_task(planned)
    escalated = cos.escalate("planned", reason="decision needed")
    assert escalated.status == TaskStatus.PLANNED
    assert escalated.escalation_count == 1


def test_agentops_window_retains_local_evidence_when_persisted_agent_has_none() -> None:
    ledger = TaskLedger()
    policy = {
        "version": "edge-v1",
        "weights": {"outcome_achievement": 1.0},
        "thresholds": {
            "restrict_below": 0.3,
            "watch_below": 0.65,
            "increase_above": 0.9,
            "minimum_events_for_increase": 2,
        },
    }
    evaluator = AgentOpsEvaluator(policy, ledger=ledger)
    evaluator.events.append(
        __import__("mesh_cos.performance", fromlist=["PerformanceEvent"]).PerformanceEvent(
            "cro", "T", "outcome_achievement", 0.8
        )
    )
    ledger.save_record(
        "performance_event",
        "other",
        {
            "version": "mesh.cos.performance-event.v1",
            "agent_id": "cfo",
            "task_id": "X",
            "category": "outcome_achievement",
            "score": 1.0,
            "severity": "LOW",
            "reason": "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    scorecard = evaluator.scorecard("cro")
    assert scorecard["event_count"] == 1
    assert scorecard["recommendation"] == "CONTINUE"


def test_registry_policy_application_is_idempotent_for_existing_tool_and_contract(
    tmp_path: Path,
) -> None:
    root = tmp_path / "repo"
    (root / "agents").mkdir(parents=True)
    (root / "config").mkdir()
    (root / "config" / "governance-policy.v1.json").write_text(
        json.dumps(
            {
                "applies_to": "ALL_REGISTERED_AGENTS",
                "governance_tool": "governance-journal",
                "output_contracts": ["decision.v2"],
                "governance_policy": {"audit_logging": "REQUIRED"},
            }
        )
    )
    (root / "agents" / "registry.json").write_text(
        json.dumps(
            {
                "agents": [
                    {
                        "agent_id": "a",
                        "display_name": "Agent A",
                        "version": "1.0.0",
                        "status": "ACTIVE",
                        "parent_agent_id": None,
                        "decision_authority": "execution only",
                        "tools": ["governance-journal"],
                        "output_contracts": ["decision.v2"],
                    }
                ]
            }
        )
    )
    loaded = load_registry(root / "agents" / "registry.json")["a"]
    assert loaded["decision_authority"] == 1
    assert loaded["tools"] == ["governance-journal"]
    assert loaded["output_contracts"] == ["decision.v2"]
