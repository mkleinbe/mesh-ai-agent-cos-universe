from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.slack_hitl import SlackHITLConfig

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"


def _env(identity_file: Path) -> dict[str, str]:
    return {
        "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
        "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(identity_file),
        "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
    }


def test_identity_file_must_exist_and_be_nonempty(tmp_path: Path) -> None:
    missing = tmp_path / "missing-id"
    with pytest.raises(RuntimeError, match="identity file is unavailable"):
        SlackHITLConfig.from_env(_env(missing))

    empty = tmp_path / "empty-id"
    empty.write_text("\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="identity file is empty"):
        SlackHITLConfig.from_env(_env(empty))


def test_identity_file_supplies_approver_without_environment_persistence(tmp_path: Path) -> None:
    identity_file = tmp_path / "slack-approver-user-id"
    identity_file.write_text(APPROVER_USER_ID + "\n", encoding="utf-8")
    config = SlackHITLConfig.from_env(_env(identity_file))
    assert config.approver_user_id == APPROVER_USER_ID
    assert config.approver_principal == "michael"
