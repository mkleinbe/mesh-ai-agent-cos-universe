from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.preflight import ProductionPreflight

ROOT = Path(__file__).resolve().parents[2]
APPROVER_USER_ID = "U0TESTAPPROVER"
APP_ID = "A0B49RNF4K0"


def production_env(tmp_path: Path) -> dict[str, str]:
    bot_file = tmp_path / "slack-bot-token"
    bot_file.write_text("xoxb-test-secret\n", encoding="utf-8")
    return {
        "MESH_COS_KILL_SWITCH": "false",
        "MESH_COS_AGENT_ID": "cos",
        "MESH_COS_LEDGER_PATH": ".mesh-cos/test-task-ledger.sqlite3",
        "MESH_COS_PYTHON_BIN": "python",
        "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": "C0BRL4GCL3A",
        "MESH_COS_SLACK_APPROVER_USER_ID": APPROVER_USER_ID,
        "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
        "MESH_COS_SLACK_APP_ID": APP_ID,
        "MESH_COS_SLACK_HITL_MODE": "CHATGPT_NATIVE_EVENT_TRIGGER",
        "MESH_COS_SLACK_BOT_TOKEN_FILE": str(bot_file),
        "MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID": "CANSWER",
    }


def test_production_preflight_passes_without_exposing_secrets(tmp_path: Path) -> None:
    ledger = TaskLedger()
    result = ProductionPreflight(
        root=ROOT,
        env=production_env(tmp_path),
        ledger=ledger,
        require_slack=True,
        require_answer_desk=True,
    ).check()
    assert result["ready"] is True
    assert all(check["status"] == "PASS" for check in result["checks"])
    rendered = str(result)
    assert "xoxb-test-secret" not in rendered
    assert APPROVER_USER_ID not in rendered
    assert ".mesh-cos/test-task-ledger.sqlite3" not in rendered
    assert "slack_approval_command" not in rendered


def test_production_preflight_fails_closed_for_missing_local_runtime_config(tmp_path: Path) -> None:
    missing = production_env(tmp_path)
    missing.pop("MESH_COS_LEDGER_PATH")
    result = ProductionPreflight(root=ROOT, env=missing).check()
    assert result["ready"] is False
    assert any(
        check["name"] == "mcp_ledger_path" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    with pytest.raises(RuntimeError, match="mcp_ledger_path"):
        ProductionPreflight(root=ROOT, env=missing).assert_ready()

    killed = production_env(tmp_path)
    killed["MESH_COS_KILL_SWITCH"] = "true"
    result = ProductionPreflight(root=ROOT, env=killed).check()
    assert result["ready"] is False
    assert any(
        check["name"] == "kill_switch" and check["status"] == "FAIL"
        for check in result["checks"]
    )


def test_production_preflight_enforces_requested_slack_surfaces_only(tmp_path: Path) -> None:
    env = production_env(tmp_path)
    env.pop("MESH_COS_SLACK_APPROVER_USER_ID")
    env.pop("MESH_COS_SLACK_APP_ID")
    env.pop("MESH_COS_SLACK_HITL_MODE")
    env.pop("MESH_COS_SLACK_BOT_TOKEN_FILE")
    env.pop("MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID")

    assert ProductionPreflight(root=ROOT, env=env, require_slack=False).check()["ready"] is True

    slack = ProductionPreflight(root=ROOT, env=env, require_slack=True).check()
    assert slack["ready"] is False
    for name in (
        "slack_approver_identity",
        "slack_app_identity",
        "slack_native_trigger_mode",
        "slack_bot_credential",
    ):
        assert any(
            check["name"] == name and check["status"] == "FAIL"
            for check in slack["checks"]
        )
    assert all(check["name"] != "slack_approval_command" for check in slack["checks"])

    answer = ProductionPreflight(
        root=ROOT,
        env=production_env(tmp_path) | {"MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID": ""},
        require_answer_desk=True,
    ).check()
    assert answer["ready"] is False
    assert any(
        check["name"] == "answer_desk_channel" and check["status"] == "FAIL"
        for check in answer["checks"]
    )


def test_production_preflight_rejects_slack_identity_app_mode_and_credential_drift(
    tmp_path: Path,
) -> None:
    wrong_channel = production_env(tmp_path)
    wrong_channel["MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID"] = "C0WRONG"
    result = ProductionPreflight(root=ROOT, env=wrong_channel, require_slack=True).check()
    assert any(
        check["name"] == "agent_ops_channel" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    wrong_principal = production_env(tmp_path)
    wrong_principal["MESH_COS_SLACK_APPROVER_PRINCIPAL"] = "other"
    result = ProductionPreflight(root=ROOT, env=wrong_principal, require_slack=True).check()
    assert any(
        check["name"] == "slack_approver_identity" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    wrong_app = production_env(tmp_path)
    wrong_app["MESH_COS_SLACK_APP_ID"] = "A0OTHERAPP"
    result = ProductionPreflight(root=ROOT, env=wrong_app, require_slack=True).check()
    assert any(
        check["name"] == "slack_app_identity" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    wrong_mode = production_env(tmp_path)
    wrong_mode["MESH_COS_SLACK_HITL_MODE"] = "SOCKET_MODE"
    result = ProductionPreflight(root=ROOT, env=wrong_mode, require_slack=True).check()
    assert any(
        check["name"] == "slack_native_trigger_mode" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    socket_file = tmp_path / "legacy-socket"
    socket_file.write_text("xapp-legacy-secret\n", encoding="utf-8")
    legacy_socket = production_env(tmp_path)
    legacy_socket["MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE"] = str(socket_file)
    result = ProductionPreflight(root=ROOT, env=legacy_socket, require_slack=True).check()
    assert any(
        check["name"] == "slack_native_trigger_mode" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    bad_bot = tmp_path / "bad-bot"
    bad_bot.write_text("not-a-bot-token\n", encoding="utf-8")
    bad_bot_env = production_env(tmp_path)
    bad_bot_env["MESH_COS_SLACK_BOT_TOKEN_FILE"] = str(bad_bot)
    result = ProductionPreflight(root=ROOT, env=bad_bot_env, require_slack=True).check()
    assert any(
        check["name"] == "slack_bot_credential" and check["status"] == "FAIL"
        for check in result["checks"]
    )

    legacy_command = production_env(tmp_path)
    legacy_command["MESH_COS_SLACK_APPROVAL_COMMAND"] = "/wrong-and-ignored"
    result = ProductionPreflight(root=ROOT, env=legacy_command, require_slack=True).check()
    assert result["ready"] is True
    assert all(check["name"] != "slack_approval_command" for check in result["checks"])


def test_production_preflight_fails_closed_when_bot_secret_read_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    env = production_env(tmp_path)
    bot_file = Path(env["MESH_COS_SLACK_BOT_TOKEN_FILE"])
    original = Path.read_text

    def read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path == bot_file:
            raise OSError("simulated unreadable Slack credential")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    result = ProductionPreflight(root=ROOT, env=env, require_slack=True).check()
    assert result["ready"] is False
    assert any(
        check["name"] == "slack_bot_credential" and check["status"] == "FAIL"
        for check in result["checks"]
    )


def test_production_preflight_detects_audit_chain_corruption(tmp_path: Path) -> None:
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

    result = ProductionPreflight(root=ROOT, env=production_env(tmp_path), ledger=ledger).check()
    assert result["ready"] is False
    assert any(
        check["name"] == "audit_chain" and check["status"] == "FAIL"
        for check in result["checks"]
    )
