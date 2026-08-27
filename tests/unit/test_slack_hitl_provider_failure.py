from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
FINGERPRINT = "d" * 64


def test_non_socket_provider_payload_never_becomes_approval_evidence() -> None:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Synthetic Slack provider failure acceptance",
        expected_outcome="Non-authenticated Slack input cannot authorize action",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="non-Socket input fails closed",
        idempotency_key="SLACK-PROVIDER-FAILURE-001",
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
        f"Synthetic no-op payload_fingerprint={FINGERPRINT}",
    )
    service = SlackSocketApprovalService(
        ledger,
        SlackSocketApprovalConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
        ),
    )

    with pytest.raises(PermissionError, match="slash_commands"):
        service.handle_envelope(
            {
                "envelope_id": "env-provider-down",
                "type": "events_api",
                "payload": {
                    "event": {
                        "type": "message",
                        "channel": CHANNEL_ID,
                        "user": APPROVER_USER_ID,
                        "text": f"APPROVE {approval.approval_id}",
                    }
                },
            }
        )

    assert ledger.get_record("approval", approval.approval_id)["status"] == "PENDING"
    assert ledger.get_record("approval_slack_socket_decision", approval.approval_id) is None
