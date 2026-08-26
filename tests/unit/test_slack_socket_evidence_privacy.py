from __future__ import annotations

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_hitl import CHATGPT_AGENTS_SLACK_USER_ID
from mesh_cos.slack_socket_approval import (
    SlackSocketApprovalConfig,
    SlackSocketApprovalService,
)


def test_trusted_socket_decision_does_not_persist_protected_human_provider_id() -> None:
    channel_id = "C0TESTAGENTOPS"
    approver_user_id = "U0PROTECTEDAPPROVER"
    fingerprint = "9" * 64
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Synthetic approval evidence privacy test",
        expected_outcome="Protected provider identity is used for verification but not persisted",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="durable approval evidence contains canonical principal without protected provider ID",
        idempotency_key="TEST-SOCKET-EVIDENCE-PRIVACY",
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
        f"Synthetic payload_fingerprint={fingerprint}",
    )
    ledger.save_record(
        "approval_slack_binding",
        approval.approval_id,
        {
            "approval_id": approval.approval_id,
            "task_id": task.task_id,
            "channel_id": channel_id,
            "thread_ts": "1788000000.000001",
            "notice_author_user_id": CHATGPT_AGENTS_SLACK_USER_ID,
            "approver_identity_verified": True,
            "approver_principal": "michael",
            "payload_fingerprint": fingerprint,
        },
    )
    service = SlackSocketApprovalService(
        ledger,
        SlackSocketApprovalConfig(
            channel_id=channel_id,
            approver_user_id=approver_user_id,
        ),
    )
    decision = service.handle_envelope(
        {
            "envelope_id": "env-privacy",
            "type": "slash_commands",
            "payload": {
                "channel_id": channel_id,
                "user_id": approver_user_id,
                "command": "/mesh-approval",
                "text": f"APPROVE {approval.approval_id}",
                "trigger_id": "trigger-privacy",
            },
        }
    )

    binding = dict(ledger.get_record("approval_slack_binding", approval.approval_id))
    durable = dict(
        ledger.get_record("approval_slack_socket_decision", approval.approval_id)
    )
    assert binding["approver_identity_verified"] is True
    assert "approver_user_id" not in binding
    assert approver_user_id not in str(binding)
    assert decision["provider_identity_verified"] is True
    assert durable["provider_identity_verified"] is True
    assert durable["canonical_principal"] == "michael"
    assert "slack_user_id" not in durable
    assert "approver_user_id" not in durable
    assert approver_user_id not in str(durable)
