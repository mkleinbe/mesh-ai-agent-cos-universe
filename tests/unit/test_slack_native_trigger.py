from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_native_trigger import SlackNativeTriggerApprovalService
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig

CHANNEL = "C0BRL4GCL3A"
USER = "U01KG3CNYHK"
APP = "A0B49RNF4K0"
ROOT = "1787843216.789639"
MESSAGE = "1787843300.046169"
FINGERPRINT = "e" * 64


def _ledger() -> tuple[TaskLedger, str, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Execute one exact approved communication",
        expected_outcome="Native Slack trigger wakes provider reconciliation",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="Slack provider state is independently reconciled",
        idempotency_key="NATIVE-SLACK-001",
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
        f"Execute exact payload_fingerprint={FINGERPRINT}",
    )
    return ledger, task.task_id, approval.approval_id


def _service(
    text: str = "APPROVE",
    *,
    user: str = USER,
    edited: bool = False,
    app_authored: bool = False,
    provider_messages: object | None = None,
) -> tuple[TaskLedger, str, str, SlackNativeTriggerApprovalService, list[tuple[str, dict, str]]]:
    ledger, task_id, approval_id = _ledger()
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, payload, token))
        if method == "chat.postMessage":
            return {"ok": True, "channel": CHANNEL, "ts": ROOT}
        if method == "chat.update":
            return {"ok": True, "channel": CHANNEL, "ts": ROOT}
        if method == "conversations.replies":
            if provider_messages is not None:
                return {"ok": True, "messages": provider_messages}
            message: dict = {
                "type": "message",
                "channel": CHANNEL,
                "thread_ts": ROOT,
                "ts": MESSAGE,
                "user": user,
                "text": text,
            }
            if edited:
                message["edited"] = {"user": user, "ts": "1787843400.000001"}
            if app_authored:
                message["bot_id"] = "B0123456789"
            return {"ok": True, "messages": [message]}
        raise AssertionError(method)

    notifier = SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", transport), CHANNEL)
    notifier.post_approval(approval_id)
    config = SlackSocketApprovalConfig(CHANNEL, USER, "michael", APP)
    return ledger, task_id, approval_id, SlackNativeTriggerApprovalService(ledger, config, notifier), calls


def test_native_trigger_is_locator_only_and_approve_is_provider_reconciled() -> None:
    ledger, task_id, approval_id, service, calls = _service("approve")
    result = service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
    assert result["version"] == "mesh.cos.slack-human-decision.v6"
    assert result["source"] == "CHATGPT_NATIVE_SLACK_EVENT_TRIGGER_RECONCILIATION"
    assert result["trigger_is_authority"] is False
    assert result["provider_reconciled"] is True
    assert result["disposition"] == "APPROVE"
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION
    method, payload, token = next(call for call in calls if call[0] == "conversations.replies")
    assert method == "conversations.replies"
    assert token == "xoxb-test"
    assert payload == {
        "channel": CHANNEL,
        "ts": ROOT,
        "oldest": MESSAGE,
        "latest": MESSAGE,
        "inclusive": True,
        "limit": 1,
    }


def test_native_trigger_accepts_provider_rendered_bold_approve_incident_shape() -> None:
    ledger, task_id, approval_id, service, _ = _service("*APPROVE*")
    result = service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
    assert result["version"] == "mesh.cos.slack-human-decision.v6"
    assert result["source"] == "CHATGPT_NATIVE_SLACK_EVENT_TRIGGER_RECONCILIATION"
    assert result["trigger_is_authority"] is False
    assert result["provider_reconciled"] is True
    assert result["disposition"] == "APPROVE"
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION


def test_native_trigger_replay_is_idempotent() -> None:
    _, _, _, service, _ = _service("APPROVE")
    first = service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
    second = service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
    assert first == second


def test_native_trigger_falls_back_to_nonfinal_result_if_compat_record_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, _, approval_id, service, _ = _service("APPROVE")
    monkeypatch.setattr(
        service.compat,
        "handle_envelope",
        lambda envelope: {"approval_id": approval_id, "disposition": "APPROVE"},
    )
    result = service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
    assert result == {
        "approval_id": approval_id,
        "disposition": "APPROVE",
        "trigger_is_authority": False,
        "provider_reconciled": True,
    }


def test_native_trigger_change_and_change_input_remain_non_authoritative() -> None:
    ledger, task_id, approval_id, service, _ = _service("CHANGE")
    start = service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
    assert start["status"] == "AWAITING_CHANGE_INPUT"
    assert start["trigger_is_authority"] is False
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"

    service.notifier.api.transport = lambda method, payload, token: (
        {"ok": True, "channel": CHANNEL, "ts": ROOT}
        if method in {"chat.postMessage", "chat.update"}
        else {
            "ok": True,
            "messages": [
                {
                    "type": "message",
                    "channel": CHANNEL,
                    "thread_ts": ROOT,
                    "ts": "1787843500.000002",
                    "user": USER,
                    "text": "remove the second recipient",
                }
            ],
        }
    )
    captured = service.reconcile(thread_ts=ROOT, message_ts="1787843500.000002")
    assert captured["status"] == "PENDING_AGENT_REVISION"
    assert captured["change_instruction"] == "remove the second recipient"
    assert captured["provider_reconciled"] is True
    assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS


@pytest.mark.parametrize(
    ("thread_ts", "message_ts", "error"),
    [
        ("", MESSAGE, "requires thread"),
        (ROOT, "", "requires thread"),
        (ROOT, ROOT, "must be replies"),
    ],
)
def test_native_trigger_rejects_invalid_locators(thread_ts: str, message_ts: str, error: str) -> None:
    _, _, _, service, _ = _service()
    with pytest.raises(PermissionError, match=error):
        service.reconcile(thread_ts=thread_ts, message_ts=message_ts)


@pytest.mark.parametrize(
    ("provider_messages", "error"),
    [
        ("invalid", "message collection"),
        ([], "reconciled exactly"),
        ([{"ts": MESSAGE, "thread_ts": ROOT}, {"ts": MESSAGE, "thread_ts": ROOT}], "reconciled exactly"),
    ],
)
def test_native_trigger_requires_one_exact_provider_message(provider_messages: object, error: str) -> None:
    _, _, _, service, _ = _service(provider_messages=provider_messages)
    exception = TypeError if error == "message collection" else PermissionError
    with pytest.raises(exception, match=error):
        service.reconcile(thread_ts=ROOT, message_ts=MESSAGE)


def test_native_trigger_rejects_edited_app_authored_wrong_user_and_wrong_thread() -> None:
    _, _, _, edited, _ = _service(edited=True)
    with pytest.raises(PermissionError, match="Edited"):
        edited.reconcile(thread_ts=ROOT, message_ts=MESSAGE)

    _, _, _, bot, _ = _service(app_authored=True)
    with pytest.raises(PermissionError, match="app-authored"):
        bot.reconcile(thread_ts=ROOT, message_ts=MESSAGE)

    _, _, _, wrong_user, _ = _service(user="U0OTHER")
    with pytest.raises(PermissionError, match="configured approver"):
        wrong_user.reconcile(thread_ts=ROOT, message_ts=MESSAGE)

    _, _, _, wrong_thread, _ = _service(
        provider_messages=[
            {
                "type": "message",
                "channel": CHANNEL,
                "thread_ts": "999.000",
                "ts": MESSAGE,
                "user": USER,
                "text": "APPROVE",
            }
        ]
    )
    with pytest.raises(PermissionError, match="thread does not match"):
        wrong_thread.reconcile(thread_ts=ROOT, message_ts=MESSAGE)
