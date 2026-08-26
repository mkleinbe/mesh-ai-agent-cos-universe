from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack import SlackWebClient
from mesh_cos.slack_hitl import (
    CHATGPT_AGENTS_SLACK_USER_ID,
    SlackApprovalHITLService,
    SlackHITLConfig,
)

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
THREAD_TS = "1788000000.000001"
FINGERPRINT = "d" * 64


def test_provider_api_failure_never_becomes_approval_evidence() -> None:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Synthetic Slack provider failure acceptance",
        expected_outcome="Provider failure cannot authorize action",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="Slack provider failure fails closed",
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

    def transport(method: str, payload: dict, token: str) -> dict:
        assert method == "conversations.replies"
        assert payload == {"channel": CHANNEL_ID, "ts": THREAD_TS}
        assert token == "xoxb-test-verifier"
        return {
            "ok": False,
            "error": "invalid_auth",
            "messages": [
                {
                    "user": CHATGPT_AGENTS_SLACK_USER_ID,
                    "ts": THREAD_TS,
                    "text": (
                        f"<@{APPROVER_USER_ID}> Approval owner: MK / Michael "
                        f"Approval ID: {approval.approval_id} Payload fingerprint: {FINGERPRINT}"
                    ),
                }
            ],
        }

    service = SlackApprovalHITLService(
        ledger,
        SlackWebClient("xoxb-test-verifier", transport=transport),
        SlackHITLConfig(channel_id=CHANNEL_ID, approver_user_id=APPROVER_USER_ID),
    )

    with pytest.raises(RuntimeError, match="provider thread read failed"):
        service.bind_notice(
            approval.approval_id,
            channel_id=CHANNEL_ID,
            thread_ts=THREAD_TS,
            payload_fingerprint=FINGERPRINT,
        )

    assert ledger.get_record("approval_slack_binding", approval.approval_id) is None
    assert ledger.get_record("approval", approval.approval_id)["status"] == "PENDING"
