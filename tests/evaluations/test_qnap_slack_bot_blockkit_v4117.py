from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read(path: str) -> str: return (ROOT / path).read_text(encoding="utf-8")

def test_qnap_122_dedicated_bot_is_canonical_outbound_slack_path() -> None:
    source = read("src/mesh_cos/slack_bot.py"); adapters = read("src/mesh_cos/adapters.py"); post_body = source[source.index("    def post_message("):source.index("    def update_message(")]
    assert 'SLACK_API_BASE = "https://slack.com/api"' in source; assert '"chat.postMessage"' in post_body; assert "MESH_COS_SLACK_BOT_TOKEN_FILE" in source; assert "xoxb-" in source; assert 'payload["username"]' not in post_body; assert 'payload["icon_emoji"]' not in post_body; assert 'payload["icon_url"]' not in post_body; assert "SLACK_BOT_API" in adapters; assert "CHATGPT_CONNECTOR_HANDOFF" not in adapters

def test_qnap_122_123_approval_blocks_use_rich_text_and_three_buttons() -> None:
    source = read("src/mesh_cos/slack_bot.py")
    for token in ('"type": "rich_text"', '"type": "actions"', '"mesh_approval_approve"', '"mesh_approval_deny"', '"mesh_approval_change"', '"style": "primary"', '"style": "danger"'): assert token in source

def test_qnap_123_124_socket_mode_dispatches_block_actions_and_change_prompt() -> None:
    socket = read("mcp/src/slack-socket-mode.ts"); service = read("src/mesh_cos/slack_socket_approval.py"); assert "interactive" in socket; assert "block_actions" in service; assert "AWAITING_CHANGE_INPUT" in service; assert "What would you like to change?" in service; assert "post_thread_reply" in service

def test_qnap_125_change_instruction_is_governed_and_not_direct_authority() -> None:
    service = read("src/mesh_cos/slack_socket_approval.py"); bot = read("src/mesh_cos/slack_bot.py"); assert "CHANGE_REQUEST_KIND" in service; assert "approval_change_request" in bot; assert "PENDING_AGENT_REVISION" in service; assert "SUPERSEDED_BY_CHANGE" in service; assert "change_instruction" in service; assert "provider_identity_verified" in service

def test_qnap_127_manifest_matches_private_channel_bot_surface() -> None:
    manifest = json.loads(read("deployment/qnap/slack-app-manifest.v4.1.17.json")); assert manifest["display_information"]["name"] == "ChatGPT Enterprise AI Agent"; assert manifest["features"]["bot_user"]["display_name"] == "ChatGPT Enterprise AI Agent"; assert {"chat:write", "groups:history"}.issubset(set(manifest["oauth_config"]["scopes"]["bot"])); assert "message.groups" in set(manifest["settings"]["event_subscriptions"]["bot_events"]); assert manifest["settings"]["socket_mode_enabled"] is True; assert manifest["settings"]["interactivity"]["is_enabled"] is True

def test_qnap_120_bot_token_is_protected_and_slash_command_is_absent() -> None:
    compose = read("deployment/qnap/compose.yaml"); env = read("deployment/qnap/.env.example"); preflight = read("deployment/qnap/runtime_preflight.py"); provision = read("deployment/qnap/scripts/mesh-cos-slack-hitl-provision.sh"); assert "MESH_COS_SLACK_BOT_TOKEN_FILE: /run/secrets/slack_bot_token" in compose; assert "/run/secrets/slack_bot_token:ro" in compose; assert "QNAP_SLACK_BOT_TOKEN_FILE=" in env; assert "MESH_COS_SLACK_APPROVAL_COMMAND" not in compose; assert "MESH_COS_SLACK_APPROVAL_COMMAND" not in env; assert "MESH_COS_SLACK_APPROVAL_COMMAND" not in preflight; assert "Slack bot OAuth token" in provision; assert "xoxb-*" in provision

def test_qnap_128_no_webhook_secret_is_committed() -> None:
    for path in ("deployment/qnap/.env.example", "deployment/qnap/compose.yaml", "deployment/qnap/slack-app-manifest.v4.1.17.json", "src/mesh_cos/slack_bot.py"):
        text = read(path); assert "hooks.slack.com/services/" not in text; assert "incoming_webhook_url" not in text
