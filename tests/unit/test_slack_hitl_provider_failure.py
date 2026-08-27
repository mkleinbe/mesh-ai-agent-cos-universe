from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
APP_ID = "A0TESTAPP"
FINGERPRINT = "d" * 64
ROOT_TS = "1787843216.789639"


def _setup(*, bound: bool = False) -> tuple[TaskLedger, SlackSocketApprovalService, str]:
    ledger = TaskLedger(); cos = ChiefOfStaffService(ledger)
    task = cos.intake(objective="Synthetic Slack provider failure acceptance", expected_outcome="Unbound or app-authored Slack input cannot authorize action", requested_by="cos", executive_sponsor="michael", accountable_agent="cos", decision_owner="michael", authority_level=AuthorityLevel.L4, acceptance_test="provider event must be a manual human reply in the bound approval thread", idempotency_key="SLACK-PROVIDER-FAILURE-001")
    for target in (TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS): cos.advance(task.task_id, target)
    approval = ApprovalService(ledger).request(task.task_id, "cos", "michael", AuthorityLevel.L4, f"Synthetic no-op payload_fingerprint={FINGERPRINT}")
    notifier = SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", lambda method, payload, token: {"ok": True, "channel": CHANNEL_ID, "ts": ROOT_TS}), CHANNEL_ID)
    if bound: notifier.post_approval(approval.approval_id)
    service = SlackSocketApprovalService(ledger, SlackSocketApprovalConfig(channel_id=CHANNEL_ID, approver_user_id=APPROVER_USER_ID, app_id=APP_ID), notifier=notifier)
    return ledger, service, approval.approval_id


def _event(text: str, *, thread_ts: str | None = None, app_id: str | None = None) -> dict:
    event = {"type": "message", "channel": CHANNEL_ID, "user": APPROVER_USER_ID, "text": text, "ts": "1787843300.046169", "event_ts": "1787843300.046169"}
    if thread_ts is not None: event["thread_ts"] = thread_ts
    if app_id is not None: event["app_id"] = app_id
    return {"envelope_id": "env-provider", "type": "events_api", "payload": {"type": "event_callback", "api_app_id": APP_ID, "event_id": "Ev-provider", "event": event}}


def test_unbound_provider_message_never_becomes_approval_evidence() -> None:
    ledger, service, approval_id = _setup()
    with pytest.raises(PermissionError, match="bound"): service.handle_envelope(_event("APPROVE", thread_ts=ROOT_TS))
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"; assert ledger.get_record("approval_slack_socket_decision", approval_id) is None


def test_app_authored_provider_message_never_becomes_human_approval_evidence() -> None:
    ledger, service, approval_id = _setup(bound=True)
    with pytest.raises(PermissionError, match="app-authored"): service.handle_envelope(_event("APPROVE", thread_ts=ROOT_TS, app_id="A0CHATGPT"))
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"; assert ledger.get_record("approval_slack_socket_decision", approval_id) is None
