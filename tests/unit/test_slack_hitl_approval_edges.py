from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.slack_hitl import SlackHITLConfig, _parse_decision

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"


def test_config_rejects_missing_noncanonical_and_conversation_identity_values() -> None:
    with pytest.raises(RuntimeError, match="channel ID"):
        SlackHITLConfig(channel_id="", approver_user_id=APPROVER_USER_ID)
    for invalid in ("", "D0DIRECT", "C0CHANNEL", "michael"):
        with pytest.raises(RuntimeError, match="begin with U or W"):
            SlackHITLConfig(channel_id=CHANNEL_ID, approver_user_id=invalid)
    with pytest.raises(RuntimeError, match="principal michael"):
        SlackHITLConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
            approver_principal="mk",
        )


def test_config_from_process_environment_uses_safe_principal_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_USER_ID", APPROVER_USER_ID)
    monkeypatch.delenv("MESH_COS_SLACK_APPROVER_PRINCIPAL", raising=False)
    config = SlackHITLConfig.from_env()
    assert config.approver_principal == "michael"


def test_config_file_errors_fail_closed(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(RuntimeError, match="unavailable"):
        SlackHITLConfig.from_env(
            {
                "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
                "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(missing),
            }
        )

    empty = tmp_path / "empty"
    empty.write_text("\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="empty"):
        SlackHITLConfig.from_env(
            {
                "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
                "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(empty),
            }
        )


def test_parse_decision_rejects_wrong_ids_malformed_change_and_nonexact_commands() -> None:
    with pytest.raises(PermissionError, match="Approval ID mismatch"):
        _parse_decision("APPROVE approval-wrong", "approval-right")
    with pytest.raises(PermissionError, match="Approval ID mismatch"):
        _parse_decision("CHANGES approval-wrong: revise", "approval-right")
    for text in (
        "please APPROVE approval-right",
        "APPROVED approval-right",
        "CHANGES approval-right:",
        "approve approval-right",
        "APPROVE",
    ):
        with pytest.raises(PermissionError, match="not exact"):
            _parse_decision(text, "approval-right")
