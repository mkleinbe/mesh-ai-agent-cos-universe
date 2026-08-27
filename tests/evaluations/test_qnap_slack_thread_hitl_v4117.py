from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

CHANNEL_ID = "C0TESTAGENTOPS"
APPROVER_USER_ID = "U0TESTAPPROVER"
APP_ID = "A0TESTAPP"
FINGERPRINT = "e" * 64
ROOT_TS = "1787843216.789639"


def _pending() -> tuple[TaskLedger, str, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Synthetic provider-authenticated Slack thread approval",
        expected_outcome="A manual MK interaction decides only the bot-bound approval",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="provider event, bound thread, principal, and fingerprint reconcile",
        idempotency_key="QNAP-117-SYNTHETIC",
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
        f"Synthetic acceptance only payload_fingerprint={FINGERPRINT}",
    )
    return ledger, task.task_id, approval.approval_id


def _config() -> SlackSocketApprovalConfig:
    return SlackSocketApprovalConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
        app_id=APP_ID,
    )


def _notifier(ledger: TaskLedger) -> SlackApprovalNotifier:
    counter = {"value": 0}

    def transport(method: str, payload: dict, token: str) -> dict:
        assert token == "xoxb-test"
        counter["value"] += 1
        if method == "chat.postMessage" and "thread_ts" not in payload:
            return {"ok": True, "channel": CHANNEL_ID, "ts": ROOT_TS}
        return {"ok": True, "channel": CHANNEL_ID, "ts": f"1787843300.{counter['value']:06d}"}

    return SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", transport), CHANNEL_ID)


def _reply(
    text: str,
    *,
    envelope_id: str = "env-reply-001",
    event_id: str = "Ev-reply-001",
) -> dict:
    return {
        "envelope_id": envelope_id,
        "type": "events_api",
        "payload": {
            "type": "event_callback",
            "api_app_id": APP_ID,
            "event_id": event_id,
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "text": text,
                "thread_ts": ROOT_TS,
                "ts": "1787843300.046169",
                "event_ts": "1787843300.046169",
            },
        },
    }


def _button(action_id: str, approval_id: str, *, envelope_id: str = "env-action-001") -> dict:
    return {
        "envelope_id": envelope_id,
        "type": "interactive",
        "payload": {
            "type": "block_actions",
            "api_app_id": APP_ID,
            "user": {"id": APPROVER_USER_ID},
            "channel": {"id": CHANNEL_ID},
            "container": {
                "type": "message",
                "channel_id": CHANNEL_ID,
                "message_ts": ROOT_TS,
            },
            "actions": [{"action_id": action_id, "value": approval_id}],
        },
    }


def _bound_service() -> tuple[TaskLedger, str, str, SlackSocketApprovalService]:
    ledger, task_id, approval_id = _pending()
    notifier = _notifier(ledger)
    posted = notifier.post_approval(approval_id)
    assert posted["thread_ts"] == ROOT_TS
    return ledger, task_id, approval_id, SlackSocketApprovalService(
        ledger,
        _config(),
        notifier=notifier,
    )


def test_bot_post_binds_pending_approval_without_deciding() -> None:
    ledger, _, approval_id, _ = _bound_service()
    binding = ledger.get_record("approval_slack_thread_binding", ROOT_TS)
    assert binding["source"] == "SLACK_BOT_API_CHAT_POSTMESSAGE"
    assert binding["approval_id"] == approval_id
    assert binding["thread_ts"] == ROOT_TS
    assert binding["payload_fingerprint"] == FINGERPRINT
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


@pytest.mark.parametrize("reply", ["APPROVE", "approve", "Approve"])
def test_case_insensitive_manual_thread_approve_records_canonical_decision(reply: str) -> None:
    ledger, task_id, approval_id, service = _bound_service()
    decision = service.handle_envelope(_reply(reply))
    assert decision["source"] == "SLACK_SOCKET_MODE_HUMAN_INTERACTION"
    assert decision["disposition"] == "APPROVE"
    assert decision["thread_ts"] == ROOT_TS
    assert decision["payload_fingerprint"] == FINGERPRINT
    assert decision["provider_identity_verified"] is True
    assert APPROVER_USER_ID not in str(decision)
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_record("approval", approval_id)["decided_by"] == "michael"
    assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION


@pytest.mark.parametrize(
    ("action_id", "disposition"),
    [
        ("mesh_approval_approve", "APPROVE"),
        ("mesh_approval_deny", "DENY"),
    ],
)
def test_block_kit_buttons_record_bound_decision(action_id: str, disposition: str) -> None:
    ledger, task_id, approval_id, service = _bound_service()
    decision = service.handle_envelope(_button(action_id, approval_id))
    assert decision["disposition"] == disposition
    expected_status = "APPROVED" if disposition == "APPROVE" else "REJECTED"
    assert ledger.get_record("approval", approval_id)["status"] == expected_status
    expected_task = TaskStatus.READY_FOR_ACTION if disposition == "APPROVE" else TaskStatus.IN_PROGRESS
    assert ledger.get_task(task_id).status == expected_task


def test_change_button_prompts_then_freeform_reply_becomes_governed_change_request() -> None:
    ledger, task_id, approval_id, service = _bound_service()
    session = service.handle_envelope(_button("mesh_approval_change", approval_id))
    assert session["status"] == "AWAITING_CHANGE_INPUT"
    assert session["prompt"] == "What would you like to change?"
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"

    instruction = "Rewrite the email copy and send the revised request to Slack instead of email."
    change = service.handle_envelope(
        _reply(instruction, envelope_id="env-change-text", event_id="Ev-change-text")
    )
    assert change["status"] == "PENDING_AGENT_REVISION"
    assert change["change_instruction"] == instruction
    assert change["provider_identity_verified"] is True
    assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    assert "SUPERSEDED_BY_CHANGE" in ledger.get_record("approval", approval_id)["reason"]
    assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS


def test_app_authored_reply_cannot_impersonate_manual_human_approval() -> None:
    ledger, _, approval_id, service = _bound_service()
    fabricated = _reply("APPROVE")
    fabricated["payload"]["event"]["app_id"] = APP_ID
    with pytest.raises(PermissionError, match="app-authored"):
        service.handle_envelope(fabricated)
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_unbound_wrong_route_wrong_app_and_wrong_button_value_fail_closed() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    with pytest.raises(PermissionError, match="bound"):
        service.handle_envelope(_reply("APPROVE"))

    ledger, _, approval_id, service = _bound_service()
    wrong_channel = _reply("APPROVE")
    wrong_channel["payload"]["event"]["channel"] = "C0OTHER"
    with pytest.raises(PermissionError, match="channel"):
        service.handle_envelope(wrong_channel)

    wrong_app = _reply("APPROVE")
    wrong_app["payload"]["api_app_id"] = "A0OTHER"
    with pytest.raises(PermissionError, match="app identity"):
        service.handle_envelope(wrong_app)

    with pytest.raises(PermissionError, match="value"):
        service.handle_envelope(_button("mesh_approval_approve", "approval-other"))
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_same_provider_event_is_idempotent_but_distinct_second_decision_conflicts() -> None:
    _, _, approval_id, service = _bound_service()
    first = _reply("APPROVE")
    decision = service.handle_envelope(first)
    assert service.handle_envelope(first) == decision
    with pytest.raises(ValueError, match="already decided"):
        service.handle_envelope(
            _reply("DENY", envelope_id="env-reply-002", event_id="Ev-reply-002")
        )


def test_root_events_are_non_authoritative_and_ignored() -> None:
    ledger, _, approval_id, service = _bound_service()
    root = _reply("APPROVE")
    root["payload"]["event"].pop("thread_ts")
    ignored = service.handle_envelope(root)
    assert ignored["status"] == "IGNORED"
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"
