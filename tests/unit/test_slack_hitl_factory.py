from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.slack_hitl import SlackHITLConfig

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"


def test_hitl_config_requires_governed_channel_and_human_user_identity() -> None:
    with pytest.raises(RuntimeError, match="channel ID"):
        SlackHITLConfig(channel_id="", approver_user_id=APPROVER_USER_ID)
    with pytest.raises(RuntimeError, match="begin with U or W"):
        SlackHITLConfig(channel_id=CHANNEL_ID, approver_user_id="D0DIRECTMESSAGE")


def test_hitl_config_reads_protected_approver_identity_without_verifier_credential(
    tmp_path: Path,
) -> None:
    identity_file = tmp_path / "slack-approver-user-id"
    identity_file.write_text(APPROVER_USER_ID + "\n", encoding="utf-8")
    config = SlackHITLConfig.from_env(
        {
            "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
            "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(identity_file),
            "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
        }
    )
    assert config.channel_id == CHANNEL_ID
    assert config.approver_user_id == APPROVER_USER_ID
    assert config.approver_principal == "michael"


def test_hitl_config_rejects_missing_or_empty_identity_file(tmp_path: Path) -> None:
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
