from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_qnap_dedicated_bot_remains_canonical_outbound_and_reconciliation_path() -> None:
    source = read("src/mesh_cos/slack_bot.py")
    adapters = read("src/mesh_cos/adapters.py")
    native = read("src/mesh_cos/slack_native_trigger.py")
    post_body = source[source.index("    def post_message("):source.index("    def update_message(")]
    assert 'SLACK_API_BASE = "https://slack.com/api"' in source
    assert '"chat.postMessage"' in post_body
    assert "MESH_COS_SLACK_BOT_TOKEN_FILE" in source
    assert "xoxb-" in source
    assert 'payload["username"]' not in post_body
    assert 'payload["icon_emoji"]' not in post_body
    assert 'payload["icon_url"]' not in post_body
    assert "SLACK_BOT_API" in adapters
    assert '"conversations.replies"' in native
    assert "CHATGPT_CONNECTOR_HANDOFF" not in adapters


def test_approval_blocks_are_reply_driven_without_nonfunctional_buttons() -> None:
    source = read("src/mesh_cos/slack_bot.py")
    assert '"type": "rich_text"' in source
    assert "Reply in this thread" in source
    assert "APPROVE" in source
    assert "DENY" in source
    assert "CHANGE" in source
    assert '"type": "actions"' not in source
    assert "mesh_approval_approve" not in source
    assert "mesh_approval_deny" not in source
    assert "mesh_approval_change" not in source


def test_native_trigger_reconciles_provider_state_and_does_not_assert_authority() -> None:
    native = read("src/mesh_cos/slack_native_trigger.py")
    adapters = read("src/mesh_cos/adapters.py")
    assert '"conversations.replies"' in native
    assert "Edited Slack messages cannot create approval authority" in native
    assert "trigger_is_authority" in native
    assert "provider_reconciled" in native
    assert "CHATGPT_NATIVE_SLACK_EVENT_TRIGGER_RECONCILIATION" in native
    assert "reconcile_triggered_message" in adapters
    for forbidden in ("decision", "approved", "actor", "principal", "user_id"):
        assert f'"{forbidden}"' in adapters


def test_change_instruction_remains_governed_and_not_direct_authority() -> None:
    service = read("src/mesh_cos/slack_socket_approval.py")
    bot = read("src/mesh_cos/slack_bot.py")
    assert "CHANGE_REQUEST_KIND" in service
    assert "approval_change_request" in bot
    assert "PENDING_AGENT_REVISION" in service
    assert "SUPERSEDED_BY_CHANGE" in service
    assert "change_instruction" in service
    assert "provider_identity_verified" in service


def test_v420_manifest_disables_socket_mode_events_and_interactivity() -> None:
    manifest = json.loads(read("deployment/qnap/slack-app-manifest.v4.2.0.json"))
    assert manifest["display_information"]["name"] == "ChatGPT Enterprise AI Agent"
    assert manifest["features"]["bot_user"]["display_name"] == "ChatGPT Enterprise AI Agent"
    assert {"chat:write", "groups:history"}.issubset(
        set(manifest["oauth_config"]["scopes"]["bot"])
    )
    assert manifest["settings"]["event_subscriptions"]["bot_events"] == []
    assert manifest["settings"]["socket_mode_enabled"] is False
    assert manifest["settings"]["interactivity"]["is_enabled"] is False


def test_qnap_runtime_requires_bot_token_but_not_socket_token() -> None:
    compose = read("deployment/qnap/compose.yaml")
    env = read("deployment/qnap/.env.example")
    preflight = read("deployment/qnap/runtime_preflight.py")
    assert "MESH_COS_SLACK_BOT_TOKEN_FILE: /run/secrets/slack_bot_token" in compose
    assert "/run/secrets/slack_bot_token:ro" in compose
    assert "QNAP_SLACK_BOT_TOKEN_FILE=" in env
    assert "QNAP_SLACK_SOCKET_APP_TOKEN_FILE=" not in env
    assert "MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE:" not in compose
    assert "CHATGPT_NATIVE_EVENT_TRIGGER" in compose
    assert "slack_native_trigger_mode_invalid" in preflight
    assert "MESH_COS_SLACK_APPROVAL_COMMAND" not in compose
    assert "MESH_COS_SLACK_APPROVAL_COMMAND" not in env


def test_no_webhook_or_socket_secret_is_committed_to_v420_surfaces() -> None:
    for path in (
        "deployment/qnap/.env.example",
        "deployment/qnap/compose.yaml",
        "deployment/qnap/slack-app-manifest.v4.2.0.json",
        "src/mesh_cos/slack_bot.py",
        "src/mesh_cos/slack_native_trigger.py",
    ):
        text = read(path)
        assert "hooks.slack.com/services/" not in text
        assert "incoming_webhook_url" not in text
        assert "xapp-" not in text
