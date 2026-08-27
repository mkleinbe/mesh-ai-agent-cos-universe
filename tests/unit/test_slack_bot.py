from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import (
    CHANGE_REQUEST_KIND,
    SLACK_BOT_API,
    THREAD_BINDING_KIND,
    SlackApprovalNotifier,
    SlackBotAPI,
    approval_blocks,
    read_slack_bot_token,
    resolved_blocks,
)

CHANNEL = "C0BRL4GCL3A"
FINGERPRINT = "a" * 64


def _pending(ledger: TaskLedger, *, action: str | None = None) -> tuple[str, str]:
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Send one exact governed message",
        expected_outcome="Bot collaboration precedes human authority",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="provider-authenticated approval is required",
        idempotency_key="SLACK-BOT-UNIT-001",
    )
    for target in (
        TaskStatus.TRIAGED,
        TaskStatus.PLANNED,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
    ):
        cos.advance(task.task_id, target)
    approval = ApprovalService(ledger).request(
        task.task_id,
        "cos",
        "michael",
        AuthorityLevel.L4,
        action or f"Send payload_fingerprint={FINGERPRINT}",
    )
    return task.task_id, approval.approval_id


def _token_file(tmp_path: Path, value: str = "xoxb-test") -> str:
    path = tmp_path / "slack-bot-token"
    path.write_text(value, encoding="utf-8")
    return str(path)


def test_read_bot_token_requires_protected_xoxb_file(tmp_path: Path) -> None:
    path = _token_file(tmp_path)
    assert read_slack_bot_token({"MESH_COS_SLACK_BOT_TOKEN_FILE": path}) == "xoxb-test"
    with pytest.raises(RuntimeError, match="required"):
        read_slack_bot_token({})
    with pytest.raises(RuntimeError, match="unavailable"):
        read_slack_bot_token({"MESH_COS_SLACK_BOT_TOKEN_FILE": str(tmp_path / "missing")})
    bad = _token_file(tmp_path, "xapp-wrong")
    with pytest.raises(RuntimeError, match="xoxb"):
        read_slack_bot_token({"MESH_COS_SLACK_BOT_TOKEN_FILE": bad})


def test_bot_api_posts_without_identity_override_and_updates(tmp_path: Path) -> None:
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, payload, token))
        return {"ok": True, "channel": CHANNEL, "ts": "123.456"}

    api = SlackBotAPI.from_env(
        {"MESH_COS_SLACK_BOT_TOKEN_FILE": _token_file(tmp_path)},
        transport=transport,
    )
    response = api.post_message(
        channel_id=CHANNEL,
        text="hello",
        blocks=[{"type": "section"}],
        thread_ts="111.222",
    )
    assert response["ts"] == "123.456"
    method, payload, token = calls[-1]
    assert method == "chat.postMessage"
    assert token == "xoxb-test"
    assert payload["thread_ts"] == "111.222"
    assert payload["blocks"] == [{"type": "section"}]
    assert not {"username", "icon_emoji", "icon_url"}.intersection(payload)

    api.post_message(channel_id=CHANNEL, text="root")
    assert "thread_ts" not in calls[-1][1]
    assert "blocks" not in calls[-1][1]

    api.update_message(
        channel_id=CHANNEL,
        message_ts="123.456",
        text="resolved",
        blocks=[{"type": "rich_text"}],
    )
    assert calls[-1][0] == "chat.update"
    assert calls[-1][1]["ts"] == "123.456"


def test_block_factories_use_reply_driven_rich_text_without_buttons() -> None:
    blocks = approval_blocks("approval-abc", "Send this exact message")
    assert any(block.get("type") == "rich_text" for block in blocks)
    assert not any(block.get("type") == "actions" for block in blocks)
    rendered = str(blocks)
    assert "APPROVE" in rendered
    assert "DENY" in rendered
    assert "CHANGE" in rendered
    assert "re-checks Slack provider state" in rendered
    assert "..." in str(approval_blocks("approval-long", "x" * 3000))
    assert "APPROVE" in str(resolved_blocks("approval-abc", "APPROVE"))


def test_notifier_posts_and_binds_pending_approval_idempotently() -> None:
    ledger = TaskLedger()
    task_id, approval_id = _pending(ledger)
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, payload, token))
        return {"ok": True, "channel": CHANNEL, "ts": "123.456"}

    notifier = SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", transport), CHANNEL)
    result = notifier.post_approval(approval_id)
    assert result == {
        "status": "POSTED",
        "execution_mode": SLACK_BOT_API,
        "authority": "COLLABORATION_ONLY",
        "approval_id": approval_id,
        "channel_id": CHANNEL,
        "thread_ts": "123.456",
        "format": "BLOCK_KIT_REPLY_DRIVEN_V2",
    }
    binding = ledger.get_record(THREAD_BINDING_KIND, "123.456")
    assert binding["version"] == "mesh.cos.slack-thread-binding.v3"
    assert binding["approval_id"] == approval_id
    assert binding["task_id"] == task_id
    assert binding["payload_fingerprint"] == FINGERPRINT
    assert calls[0][0] == "chat.postMessage"

    replay = notifier.post_approval(approval_id)
    assert replay["status"] == "ALREADY_POSTED"
    assert len(calls) == 1


def test_notifier_rejects_invalid_approval_or_provider_post() -> None:
    ledger = TaskLedger()
    notifier = SlackApprovalNotifier(
        ledger,
        SlackBotAPI("xoxb-test", lambda *_: {"ok": True, "channel": CHANNEL, "ts": "1"}),
        CHANNEL,
    )
    with pytest.raises(KeyError):
        notifier.post_approval("approval-missing")

    _, no_fp = _pending(ledger, action="Send without immutable fingerprint")
    with pytest.raises(PermissionError, match="payload_fingerprint"):
        notifier.post_approval(no_fp)

    ledger2 = TaskLedger()
    _, approval_id = _pending(ledger2)
    ApprovalService(ledger2).decide(approval_id, actor="michael", approved=False, reason="test")
    notifier2 = SlackApprovalNotifier(
        ledger2,
        SlackBotAPI("xoxb-test", lambda *_: {"ok": True, "channel": CHANNEL, "ts": "1"}),
        CHANNEL,
    )
    with pytest.raises(ValueError, match="PENDING"):
        notifier2.post_approval(approval_id)

    ledger3 = TaskLedger()
    _, pending_id = _pending(ledger3)
    wrong_channel = SlackApprovalNotifier(
        ledger3,
        SlackBotAPI("xoxb-test", lambda *_: {"ok": True, "channel": "COTHER", "ts": "1"}),
        CHANNEL,
    )
    with pytest.raises(RuntimeError, match="expected"):
        wrong_channel.post_approval(pending_id)
    no_ts = SlackApprovalNotifier(
        ledger3,
        SlackBotAPI("xoxb-test", lambda *_: {"ok": True, "channel": CHANNEL}),
        CHANNEL,
    )
    with pytest.raises(RuntimeError, match="expected"):
        no_ts.post_approval(pending_id)
    with pytest.raises(RuntimeError, match="channel ID"):
        SlackApprovalNotifier(ledger3, SlackBotAPI("xoxb-test", lambda *_: {}), "")


def test_thread_reply_resolution_and_change_request_revision() -> None:
    ledger = TaskLedger()
    task_id, approval_id = _pending(ledger)
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, payload, token))
        if method == "chat.postMessage":
            return {"ok": True, "channel": CHANNEL, "ts": "234.567"}
        return {"ok": True, "channel": CHANNEL, "ts": payload.get("ts")}

    notifier = SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", transport), CHANNEL)
    notifier.post_approval(approval_id)
    reply = notifier.post_thread_reply("234.567", "What would you like to change?")
    assert reply["message_ts"] == "234.567"
    notifier.mark_resolved(approval_id, "APPROVE")
    assert calls[-1][0] == "chat.update"
    notifier.mark_resolved("approval-unbound", "DENY")

    change_id = "change-1"
    ledger.save_record(
        CHANGE_REQUEST_KIND,
        change_id,
        {
            "change_request_id": change_id,
            "status": "PENDING_AGENT_REVISION",
            "approval_id": approval_id,
            "task_id": task_id,
            "channel_id": CHANNEL,
            "payload_fingerprint": FINGERPRINT,
        },
    )
    ledger.save_record(
        CHANGE_REQUEST_KIND,
        "change-other-channel",
        {
            "change_request_id": "change-other-channel",
            "status": "PENDING_AGENT_REVISION",
            "channel_id": "COTHER",
        },
    )
    assert [item["change_request_id"] for item in notifier.list_pending_change_requests()] == [
        change_id
    ]

    new_fp = "b" * 64
    new_approval = ApprovalService(ledger).request(
        task_id,
        "cos",
        "michael",
        AuthorityLevel.L4,
        f"Revised payload_fingerprint={new_fp}",
    )
    revised = notifier.mark_change_request_revised(change_id, new_approval.approval_id)
    assert revised["status"] == "REVISED"
    assert revised["new_payload_fingerprint"] == new_fp


def test_notifier_failure_edges_for_thread_and_change_revision() -> None:
    ledger = TaskLedger()
    task_id, approval_id = _pending(ledger)
    notifier = SlackApprovalNotifier(
        ledger,
        SlackBotAPI("xoxb-test", lambda *_: {"ok": True, "channel": CHANNEL}),
        CHANNEL,
    )
    with pytest.raises(RuntimeError, match="thread reply"):
        notifier.post_thread_reply("1", "text")

    ledger.save_record(
        THREAD_BINDING_KIND,
        "1",
        {
            "approval_id": approval_id,
            "task_id": task_id,
            "channel_id": CHANNEL,
            "thread_ts": "1",
            "payload_fingerprint": FINGERPRINT,
        },
    )
    failing = SlackApprovalNotifier(
        ledger,
        SlackBotAPI("xoxb-test", lambda *_: (_ for _ in ()).throw(RuntimeError("down"))),
        CHANNEL,
    )
    failing.mark_resolved(approval_id, "APPROVE")

    with pytest.raises(KeyError):
        notifier.mark_change_request_revised("change-missing", approval_id)
    ledger.save_record(
        CHANGE_REQUEST_KIND,
        "change-done",
        {"status": "REVISED", "task_id": task_id, "payload_fingerprint": FINGERPRINT},
    )
    with pytest.raises(ValueError, match="not pending"):
        notifier.mark_change_request_revised("change-done", approval_id)

    ledger.save_record(
        CHANGE_REQUEST_KIND,
        "change-pending",
        {
            "status": "PENDING_AGENT_REVISION",
            "task_id": task_id,
            "payload_fingerprint": FINGERPRINT,
        },
    )
    with pytest.raises(KeyError):
        notifier.mark_change_request_revised("change-pending", "approval-missing")

    other_ledger = TaskLedger()
    _, other_approval = _pending(other_ledger)
    other_record = other_ledger.get_record("approval", other_approval)
    ledger.save_record("approval", other_approval, dict(other_record))
    with pytest.raises(PermissionError, match="same task"):
        notifier.mark_change_request_revised("change-pending", other_approval)

    ApprovalService(ledger).decide(approval_id, actor="michael", approved=False, reason="old")
    with pytest.raises(ValueError, match="PENDING"):
        notifier.mark_change_request_revised("change-pending", approval_id)

    same_fp_approval = ApprovalService(ledger).request(
        task_id,
        "cos",
        "michael",
        AuthorityLevel.L4,
        f"Same payload_fingerprint={FINGERPRINT}",
    )
    with pytest.raises(ValueError, match="new payload_fingerprint"):
        notifier.mark_change_request_revised("change-pending", same_fp_approval.approval_id)
