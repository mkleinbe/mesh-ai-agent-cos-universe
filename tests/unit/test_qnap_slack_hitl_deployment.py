from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_qnap_compose_mounts_only_slack_human_and_bot_credentials_read_only() -> None:
    compose = yaml.safe_load((ROOT / "deployment/qnap/compose.yaml").read_text(encoding="utf-8"))
    service = compose["services"]["mesh-cos-mcp"]
    env = service["environment"]
    volumes = service["volumes"]

    assert env["MESH_COS_SLACK_HITL_REQUIRED"] == "true"
    assert env["MESH_COS_SLACK_HITL_MODE"] == "CHATGPT_NATIVE_EVENT_TRIGGER"
    assert env["MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID"]
    assert env["MESH_COS_SLACK_APPROVER_USER_ID_FILE"] == "/run/secrets/slack_approver_user_id"
    assert "MESH_COS_SLACK_APPROVER_USER_ID" not in env
    assert env["MESH_COS_SLACK_APPROVER_PRINCIPAL"]
    assert env["MESH_COS_SLACK_APP_ID"]
    assert "MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE" not in env
    assert env["MESH_COS_SLACK_BOT_TOKEN_FILE"] == "/run/secrets/slack_bot_token"
    assert "MESH_COS_SLACK_APPROVAL_COMMAND" not in env
    assert "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS" not in env
    assert "MESH_COS_SLACK_VERIFIER_TOKEN_FILE" not in env
    assert any("/run/secrets/slack_approver_user_id:ro" in volume for volume in volumes)
    assert not any("slack_socket_app_token" in volume for volume in volumes)
    assert any("/run/secrets/slack_bot_token:ro" in volume for volume in volumes)
    assert not any("slack_verifier" in volume for volume in volumes)


def test_qnap_networks_force_mcp_egress_over_qnet_and_keep_tunnel_private_ingress() -> None:
    compose = yaml.safe_load((ROOT / "deployment/qnap/compose.yaml").read_text(encoding="utf-8"))
    networks = compose["networks"]
    mcp = compose["services"]["mesh-cos-mcp"]
    tunnel = compose["services"]["tunnel-client"]

    assert networks["mesh-cos-private"]["internal"] is True
    assert networks["mesh-cos-private"]["ipam"]["config"][0]["subnet"] == "172.30.60.0/29"
    assert networks["mesh-cos-egress"]["driver"] == "bridge"
    assert networks["mesh-cos-egress"]["ipam"]["config"][0]["subnet"] == "172.30.61.0/29"
    assert networks["lan7"] == {"external": True, "name": "lan7"}

    assert mcp["networks"]["lan7"]["ipv4_address"] == "192.168.7.60"
    assert mcp["networks"]["mesh-cos-private"]["ipv4_address"] == "172.30.60.2"
    assert "mesh-cos-egress" not in mcp["networks"]
    assert mcp["environment"]["MCP_TRUSTED_CLIENT_IP"] == "172.30.60.3"

    assert tunnel["networks"]["mesh-cos-private"]["ipv4_address"] == "172.30.60.3"
    assert tunnel["networks"]["mesh-cos-egress"]["ipv4_address"] == "172.30.61.2"
    assert "lan7" not in tunnel["networks"]


def test_qnap_reference_env_uses_only_required_protected_slack_paths() -> None:
    text = (ROOT / "deployment/qnap/.env.example").read_text(encoding="utf-8")
    assert "QNAP_SLACK_APPROVER_USER_ID_FILE=" in text
    assert "QNAP_SLACK_SOCKET_APP_TOKEN_FILE=" not in text
    assert "QNAP_SLACK_BOT_TOKEN_FILE=" in text
    assert "MESH_COS_SLACK_APP_ID=A0B49RNF4K0" in text
    assert "MESH_COS_SLACK_HITL_MODE=CHATGPT_NATIVE_EVENT_TRIGGER" in text
    assert "MESH_COS_DEPLOYMENT_RELEASE=4.2.0" in text
    assert "QNAP_SLACK_VERIFIER_TOKEN_FILE=" not in text
    assert "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS=" not in text
    assert "MESH_COS_SLACK_APPROVER_USER_ID=" not in text
    assert "MESH_COS_SLACK_APPROVER_PRINCIPAL=michael" in text
    assert "MESH_COS_SLACK_APPROVAL_COMMAND=" not in text
    assert "hooks.slack.com/services/" not in text
    assert "xoxb-" not in text
