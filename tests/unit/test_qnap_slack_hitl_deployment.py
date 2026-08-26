from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_qnap_compose_mounts_slack_hitl_identity_and_credentials_read_only() -> None:
    compose = yaml.safe_load((ROOT / "deployment/qnap/compose.yaml").read_text(encoding="utf-8"))
    service = compose["services"]["mesh-cos-mcp"]
    env = service["environment"]
    volumes = service["volumes"]

    assert env["MESH_COS_SLACK_HITL_REQUIRED"] == "true"
    assert env["MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID"]
    assert env["MESH_COS_SLACK_APPROVER_USER_ID_FILE"] == "/run/secrets/slack_approver_user_id"
    assert "MESH_COS_SLACK_APPROVER_USER_ID" not in env
    assert env["MESH_COS_SLACK_APPROVER_PRINCIPAL"]
    assert env["MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS"]
    assert env["MESH_COS_SLACK_VERIFIER_TOKEN_FILE"] == "/run/secrets/slack_verifier_token"
    assert env["MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE"] == "/run/secrets/slack_socket_app_token"
    assert env["MESH_COS_SLACK_APPROVAL_COMMAND"] == "/mesh-approval"
    assert any("/run/secrets/slack_approver_user_id:ro" in volume for volume in volumes)
    assert any("/run/secrets/slack_verifier_token:ro" in volume for volume in volumes)
    assert any("/run/secrets/slack_socket_app_token:ro" in volume for volume in volumes)


def test_qnap_reference_env_uses_protected_file_paths_not_human_identity_value() -> None:
    text = (ROOT / "deployment/qnap/.env.example").read_text(encoding="utf-8")
    assert "QNAP_SLACK_APPROVER_USER_ID_FILE=" in text
    assert "QNAP_SLACK_VERIFIER_TOKEN_FILE=" in text
    assert "QNAP_SLACK_SOCKET_APP_TOKEN_FILE=" in text
    assert "MESH_COS_SLACK_APPROVER_USER_ID=" not in text
    assert "MESH_COS_SLACK_APPROVER_PRINCIPAL=michael" in text
    assert "MESH_COS_SLACK_APPROVAL_COMMAND=/mesh-approval" in text
