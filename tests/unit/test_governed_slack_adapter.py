from __future__ import annotations

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.registry import load_registry
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_native_trigger import SlackNativeTriggerApprovalService

CHANNEL_ID = "C0BRL4GCL3A"


def _registry() -> GovernedAdapterRegistry:
    ledger = TaskLedger()
    api = SlackBotAPI("xoxb-test", lambda method, payload, token: {"ok": True, "channel": CHANNEL_ID, "ts": "1787843216.789639"})
    return GovernedAdapterRegistry(load_registry(), GovernanceJournal(ledger), slack_notifier=SlackApprovalNotifier(ledger, api, CHANNEL_ID))


def test_slack_adapter_is_registered_only_for_cos() -> None:
    registry = _registry(); assert ("cos", "slack-adapter") in registry.adapters; assert ("cro", "slack-adapter") not in registry.adapters
    with pytest.raises(PermissionError, match="Capability not allowed"): registry.execute("cro", "slack-adapter", {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "test"}})


def test_slack_adapter_posts_collaboration_through_dedicated_bot() -> None:
    result = _registry().execute("cos", "slack-adapter", {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "governed collaboration"}})
    assert result["status"] == "POSTED"; assert result["execution_mode"] == "SLACK_BOT_API"; assert result["authority"] == "COLLABORATION_ONLY"; assert result["channel_id"] == CHANNEL_ID


def test_native_trigger_adapter_passes_only_provider_locators(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def reconcile(
        self: SlackNativeTriggerApprovalService,
        *,
        thread_ts: str,
        message_ts: str,
    ) -> dict[str, object]:
        captured.update(thread_ts=thread_ts, message_ts=message_ts)
        return {
            "status": "IGNORED",
            "trigger_is_authority": False,
            "provider_reconciled": True,
        }

    monkeypatch.setattr(SlackNativeTriggerApprovalService, "reconcile", reconcile)
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_USER_ID", "U01KG3CNYHK")
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_PRINCIPAL", "michael")
    monkeypatch.setenv("MESH_COS_SLACK_APP_ID", "A0B49RNE4K0")
    result = _registry().execute(
        "cos",
        "slack-adapter",
        {
            "operation": "reconcile_triggered_message",
            "channel_id": CHANNEL_ID,
            "payload": {"thread_ts": "123.456", "message_ts": "123.789"},
        },
    )
    assert captured == {"thread_ts": "123.456", "message_ts": "123.789"}
    assert result["trigger_is_authority"] is False


def test_native_trigger_adapter_requires_canonical_governance_and_exact_locator_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    notifier = SlackApprovalNotifier(
        TaskLedger(),
        SlackBotAPI("xoxb-test", lambda method, payload, token: {"ok": True}),
        CHANNEL_ID,
    )
    registry = GovernedAdapterRegistry(load_registry(), None, slack_notifier=notifier)
    with pytest.raises(RuntimeError, match="canonical TaskLedger"):
        registry.execute(
            "cos",
            "slack-adapter",
            {
                "operation": "reconcile_triggered_message",
                "channel_id": CHANNEL_ID,
                "payload": {"thread_ts": "123.456", "message_ts": "123.789"},
            },
        )

    governed = _registry()
    with pytest.raises(ValueError, match="Unexpected Slack collaboration payload fields: text"):
        governed.execute(
            "cos",
            "slack-adapter",
            {
                "operation": "reconcile_triggered_message",
                "channel_id": CHANNEL_ID,
                "payload": {
                    "thread_ts": "123.456",
                    "message_ts": "123.789",
                    "text": "APPROVE",
                },
            },
        )


def test_connector_handoff_is_retired() -> None:
    with pytest.raises(PermissionError, match="connector handoff is retired"): _registry().execute("cos", "slack-adapter", {"operation": "handoff", "channel_id": CHANNEL_ID, "payload": {}})


def test_slack_adapter_cannot_record_or_ingest_human_approval() -> None:
    registry = _registry()
    for operation in ("bind_notice", "ingest_decision", "record_approval"):
        with pytest.raises(PermissionError, match="Unsupported governed Slack bot operation"): registry.execute("cos", "slack-adapter", {"operation": operation, "channel_id": CHANNEL_ID, "payload": {}})
    for forbidden_field in ("approved", "approval_status", "actor", "principal", "decision", "text", "user_id"):
        with pytest.raises(PermissionError, match="cannot carry canonical approval authority"): registry.execute("cos", "slack-adapter", {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "x"}, forbidden_field: True})


def test_slack_adapter_rejects_wrong_channel_and_non_object_payload() -> None:
    registry = _registry()
    with pytest.raises(PermissionError, match="channel mismatch"): registry.execute("cos", "slack-adapter", {"operation": "post_message", "channel_id": "C0OTHER", "payload": {"text": "x"}})
    with pytest.raises(TypeError, match="payload must be an object"): registry.execute("cos", "slack-adapter", {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": "not-an-object"})


def test_slack_adapter_rejects_incomplete_or_unexpected_collaboration_fields() -> None:
    registry = _registry()
    with pytest.raises(ValueError, match="Missing Slack collaboration payload fields: payload"): registry.execute("cos", "slack-adapter", {"operation": "post_message", "channel_id": CHANNEL_ID})
    with pytest.raises(ValueError, match="Unexpected Slack collaboration payload fields: note"): registry.execute("cos", "slack-adapter", {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {}, "note": "uncontracted field"})


def test_server_owned_tool_binding_is_absent_without_cos_or_declared_tool() -> None:
    no_cos = {"worker": {"agent_id": "worker", "skills": [], "tools": [], "role": "worker", "version": "1"}}
    assert GovernedAdapterRegistry(no_cos, GovernanceJournal(TaskLedger())).adapters == {}
    cos_without_slack = {"cos": {"agent_id": "cos", "skills": [], "tools": [], "role": "cos", "version": "1"}}
    assert ("cos", "slack-adapter") not in GovernedAdapterRegistry(cos_without_slack, GovernanceJournal(TaskLedger())).adapters