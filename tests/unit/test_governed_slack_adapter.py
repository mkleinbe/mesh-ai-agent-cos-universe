from __future__ import annotations

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.registry import load_registry
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI

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


def test_connector_handoff_is_retired() -> None:
    with pytest.raises(PermissionError, match="connector handoff is retired"): _registry().execute("cos", "slack-adapter", {"operation": "handoff", "channel_id": CHANNEL_ID, "payload": {}})


def test_slack_adapter_cannot_record_or_ingest_human_approval() -> None:
    registry = _registry()
    for operation in ("bind_notice", "ingest_decision", "record_approval"):
        with pytest.raises(PermissionError, match="Unsupported governed Slack bot operation"): registry.execute("cos", "slack-adapter", {"operation": operation, "channel_id": CHANNEL_ID, "payload": {}})
    for forbidden_field in ("approved", "approval_status", "actor", "principal"):
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
