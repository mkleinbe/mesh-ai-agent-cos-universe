from __future__ import annotations

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService


def test_trusted_thread_decision_does_not_persist_protected_human_provider_id() -> None:
    channel_id = "C0TESTAGENTOPS"; approver_user_id = "U0PROTECTEDAPPROVER"; fingerprint = "9" * 64; root_ts = "1787843216.789639"; app_id = "A0TESTAPP"
    ledger = TaskLedger(); cos = ChiefOfStaffService(ledger)
    task = cos.intake(objective="Synthetic approval evidence privacy test", expected_outcome="Protected provider identity is used for verification but not persisted", requested_by="cos", executive_sponsor="michael", accountable_agent="cos", decision_owner="michael", authority_level=AuthorityLevel.L4, acceptance_test="durable approval evidence contains canonical principal without protected provider ID", idempotency_key="TEST-SOCKET-EVIDENCE-PRIVACY")
    for target in (TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS): cos.advance(task.task_id, target)
    approval = ApprovalService(ledger).request(task.task_id, "cos", "michael", AuthorityLevel.L4, f"Synthetic payload_fingerprint={fingerprint}")
    notifier = SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", lambda method, payload, token: {"ok": True, "channel": channel_id, "ts": root_ts}), channel_id)
    notifier.post_approval(approval.approval_id)
    service = SlackSocketApprovalService(ledger, SlackSocketApprovalConfig(channel_id=channel_id, approver_user_id=approver_user_id, app_id=app_id), notifier=notifier)
    decision = service.handle_envelope({"envelope_id": "env-reply-privacy", "type": "events_api", "payload": {"type": "event_callback", "api_app_id": app_id, "event_id": "Ev-reply-privacy", "event": {"type": "message", "channel": channel_id, "user": approver_user_id, "text": "APPROVE", "thread_ts": root_ts, "ts": "1787843300.046169", "event_ts": "1787843300.046169"}}})
    durable = dict(ledger.get_record("approval_slack_socket_decision", approval.approval_id)); durable_binding = dict(ledger.get_record("approval_slack_thread_binding", root_ts))
    assert decision["provider_identity_verified"] is True; assert durable["provider_identity_verified"] is True; assert durable["canonical_principal"] == "michael"; assert durable["payload_fingerprint"] == fingerprint; assert durable_binding["payload_fingerprint"] == fingerprint
    assert "slack_user_id" not in durable; assert "approver_user_id" not in durable; assert "slack_user_id" not in durable_binding; assert "approver_user_id" not in durable_binding; assert approver_user_id not in str(durable); assert approver_user_id not in str(durable_binding)
