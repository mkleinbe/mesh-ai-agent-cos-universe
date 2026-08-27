from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

CHANNEL_ID = "C0TESTAGENTOPS"
APPROVER_USER_ID = "U0TESTAPPROVER"
FINGERPRINT = "e" * 64
ROOT_TS = "1787843216.789639"


def _pending() -> tuple[TaskLedger, str, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Synthetic provider-authenticated Slack thread approval",
        expected_outcome="A manual MK thread reply decides only the bound approval",
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
    )


def _root(approval_id: str) -> dict:
    return {
        "envelope_id": "env-root-001",
        "type": "events_api",
        "payload": {
            "type": "event_callback",
            "event_id": "Ev-root-001",
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "app_id": "A0CHATGPT",
                "text": (
                    "v4.1.17 synthetic approval request\n"
                    f"Approval ID: `{approval_id}`\n"
                    "Reply in this thread with APPROVE, DENY, or CHANGE."
                ),
                "ts": ROOT_TS,
                "event_ts": ROOT_TS,
            },
        },
    }


def _reply(text: str, *, envelope_id: str = "env-reply-001", event_id: str = "Ev-reply-001") -> dict:
    return {
        "envelope_id": envelope_id,
        "type": "events_api",
        "payload": {
            "type": "event_callback",
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


def test_provider_root_event_binds_pending_approval_without_deciding() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    binding = service.handle_envelope(_root(approval_id))

    assert binding["source"] == "SLACK_SOCKET_MODE_THREAD_BINDING"
    assert binding["approval_id"] == approval_id
    assert binding["thread_ts"] == ROOT_TS
    assert binding["payload_fingerprint"] == FINGERPRINT
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


@pytest.mark.parametrize("reply", ["APPROVE", "approve", "Approve"])
def test_case_insensitive_manual_thread_approve_records_canonical_decision(reply: str) -> None:
    ledger, task_id, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))

    decision = service.handle_envelope(_reply(reply))

    assert decision["source"] == "SLACK_SOCKET_MODE_THREAD_REPLY"
    assert decision["disposition"] == "APPROVE"
    assert decision["thread_ts"] == ROOT_TS
    assert decision["payload_fingerprint"] == FINGERPRINT
    assert decision["provider_identity_verified"] is True
    assert APPROVER_USER_ID not in str(decision)
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_record("approval", approval_id)["decided_by"] == "michael"
    assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION


@pytest.mark.parametrize(
    ("reply", "disposition", "requested_change"),
    [
        ("deny", "DENY", None),
        ("DeNy", "DENY", None),
        ("change", "CHANGE", None),
        ("Change: remove recipient", "CHANGE", "remove recipient"),
    ],
)
def test_deny_and_change_are_case_insensitive_thread_decisions(
    reply: str,
    disposition: str,
    requested_change: str | None,
) -> None:
    ledger, task_id, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))

    decision = service.handle_envelope(_reply(reply))

    assert decision["disposition"] == disposition
    assert decision["requested_change"] == requested_change
    assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS


def test_app_authored_reply_cannot_impersonate_manual_human_approval() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))
    fabricated = _reply("APPROVE")
    fabricated["payload"]["event"]["app_id"] = "A0CHATGPT"

    with pytest.raises(PermissionError, match="app-authored"):
        service.handle_envelope(fabricated)
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_unbound_or_wrong_route_thread_reply_fails_closed() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    with pytest.raises(PermissionError, match="bound"):
        service.handle_envelope(_reply("APPROVE"))
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"

    service.handle_envelope(_root(approval_id))
    wrong_channel = _reply("APPROVE")
    wrong_channel["payload"]["event"]["channel"] = "C0OTHER"
    with pytest.raises(PermissionError, match="channel"):
        service.handle_envelope(wrong_channel)
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_same_provider_reply_event_is_idempotent_but_distinct_second_decision_conflicts() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))
    first = _reply("APPROVE")

    decision = service.handle_envelope(first)
    assert service.handle_envelope(first) == decision

    with pytest.raises(ValueError, match="already decided"):
        service.handle_envelope(
            _reply("DENY", envelope_id="env-reply-002", event_id="Ev-reply-002")
        )
