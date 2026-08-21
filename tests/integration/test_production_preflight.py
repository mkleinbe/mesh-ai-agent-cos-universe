from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.preflight import ProductionPreflight

ROOT = Path(__file__).resolve().parents[2]


def production_env() -> dict[str, str]:
    return {
        "MESH_COS_KILL_SWITCH": "false",
        "MESH_COS_AGENT_ID": "cos",
        "MESH_COS_LEDGER_PATH": ".mesh-cos/test-task-ledger.sqlite3",
        "MESH_COS_PYTHON_BIN": "python",
        "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": "C0BRL4GCL3A",
        "MESH_COS_SLACK_BOT_TOKEN": "xoxb-test-secret",
        "MESH_COS_SLACK_SIGNING_SECRET": "signing-secret",
        "MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID": "CANSWER",
    }


def test_production_preflight_passes_without_exposing_secrets() -> None:
    ledger = TaskLedger()
    result = ProductionPreflight(
        root=ROOT,
        env=production_env(),
        ledger=ledger,
        require_slack=True,
        require_answer_desk=True,
    ).check()
    assert result["ready"] is True
    assert all(check["status"] == "PASS" for check in result["checks"])
    rendered = str(result)
    assert "xoxb-test-secret" not in rendered
    assert "signing-secret" not in rendered
    assert ".mesh-cos/test-task-ledger.sqlite3" not in rendered


def test_production_preflight_fails_closed_for_missing_local_runtime_config() -> None:
    missing = production_env()
    missing.pop("MESH_COS_LEDGER_PATH")
    result = ProductionPreflight(root=ROOT, env=missing).check()
    assert result["ready"] is False
    assert any(
        check["name"] == "mcp_ledger_path" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    with pytest.raises(RuntimeError, match="mcp_ledger_path"):
        ProductionPreflight(root=ROOT, env=missing).assert_ready()

    killed = production_env()
    killed["MESH_COS_KILL_SWITCH"] = "true"
    result = ProductionPreflight(root=ROOT, env=killed).check()
    assert result["ready"] is False
    assert any(check["name"] == "kill_switch" and check["status"] == "FAIL" for check in result["checks"])


def test_production_preflight_enforces_requested_slack_surfaces_only() -> None:
    env = production_env()
    env.pop("MESH_COS_SLACK_BOT_TOKEN")
    env.pop("MESH_COS_SLACK_SIGNING_SECRET")
    env.pop("MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID")

    assert ProductionPreflight(root=ROOT, env=env, require_slack=False).check()["ready"] is True

    slack = ProductionPreflight(root=ROOT, env=env, require_slack=True).check()
    assert slack["ready"] is False
    assert any(check["name"] == "slack_credentials" and check["status"] == "FAIL" for check in slack["checks"])

    answer = ProductionPreflight(
        root=ROOT,
        env=production_env() | {"MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID": ""},
        require_answer_desk=True,
    ).check()
    assert answer["ready"] is False
    assert any(check["name"] == "answer_desk_channel" and check["status"] == "FAIL" for check in answer["checks"])


def test_production_preflight_detects_audit_chain_corruption() -> None:
    ledger = TaskLedger()
    journal = GovernanceJournal(ledger)
    event = journal.record_event(
        event_type="preflight.seed",
        event_category="GOVERNANCE",
        action="SEED",
        actor_type="SERVICE",
        actor_id="test",
        actor_role="test",
        task_id=None,
        correlation_id="corr",
        authority_level=0,
        policy_rule_ids=["test"],
        capability_tool="test",
        target_resource="runtime",
        source_system="test",
        input_summary="seed",
        result_status="SUCCESS",
        output_summary="seeded",
        evidence_references=[],
        risk_severity="LOW",
        data_classification="INTERNAL",
        model_provider=None,
        model_id_version=None,
        skill_agent_version="test",
        environment="TEST",
        retention_class="GOVERNANCE_LONG_TERM",
    )
    event["event_hash"] = "tampered"
    ledger.save_record("audit_event_v2", event["event_id"], event)

    result = ProductionPreflight(root=ROOT, env=production_env(), ledger=ledger).check()
    assert result["ready"] is False
    assert any(check["name"] == "audit_chain" and check["status"] == "FAIL" for check in result["checks"])
