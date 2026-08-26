from __future__ import annotations

from collections.abc import Callable

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack import SlackWebClient
from mesh_cos.slack_hitl import (
    CHATGPT_AGENTS_SLACK_USER_ID,
    CHATGPT_SLACK_USER_ID,
    SlackApprovalHITLService,
    SlackHITLConfig,
)

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
FINGERPRINT = "a" * 64
THREAD_TS = "1788000000.000001"


def _pending_approval() -> tuple[TaskLedger, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Send one governed Gmail draft after human approval",
        expected_outcome="One exact approved payload may be sent",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="provider receipts and approval evidence reconcile",
        idempotency_key="TEST-SLACK-HITL-NOTICE",
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
        f"Send Gmail draft with payload_fingerprint={FINGERPRINT}",
    )
    return ledger, approval.approval_id


def _config() -> SlackHITLConfig:
    return SlackHITLConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
        allowed_notice_author_ids=frozenset(
            {CHATGPT_SLACK_USER_ID, CHATGPT_AGENTS_SLACK_USER_ID}
        ),
    )


def _client(messages: list[dict], callback: Callable[[str, dict, str], dict] | None = None) -> SlackWebClient:
    def transport(method: str, payload: dict, token: str) -> dict:
        if callback is not None:
            return callback(method, payload, token)
        assert method == "conversations.replies"
        assert payload == {"channel": CHANNEL_ID, "ts": THREAD_TS}
        assert token == "xoxb-provider-verifier"
        return {"ok": True, "messages": messages}

    return SlackWebClient("xoxb-provider-verifier", transport=transport)


def _parent(approval_id: str, *, user: str = CHATGPT_AGENTS_SLACK_USER_ID) -> dict:
    return {
        "type": "message",
        "user": user,
        "ts": THREAD_TS,
        "text": (
            f"HITL APPROVAL REQUIRED\n<@{APPROVER_USER_ID}>\n"
            f"Approval ID: {approval_id}\n"
            f"Payload fingerprint: {FINGERPRINT}\n"
            "Approval owner: MK / Michael"
        ),
    }


def test_bind_notice_requires_real_openai_bot_and_configured_approver_identity() -> None:
    ledger, approval_id = _pending_approval()
    service = SlackApprovalHITLService(ledger, _client([_parent(approval_id)]), _config())

    binding = service.bind_notice(
        approval_id,
        channel_id=CHANNEL_ID,
        thread_ts=THREAD_TS,
        payload_fingerprint=FINGERPRINT,
    )

    assert binding["approval_id"] == approval_id
    assert binding["notice_author_user_id"] == CHATGPT_AGENTS_SLACK_USER_ID
    assert binding["approver_user_id"] == APPROVER_USER_ID
    assert binding["approver_principal"] == "michael"
    assert ledger.get_record("approval_slack_binding", approval_id) == binding
    assert not hasattr(service, "ingest_decision")


@pytest.mark.parametrize(
    "author",
    [APPROVER_USER_ID, "U0FAKECHATGPT", "U0000000000"],
)
def test_bind_notice_rejects_human_or_impostor_parent(author: str) -> None:
    ledger, approval_id = _pending_approval()
    service = SlackApprovalHITLService(
        ledger,
        _client([_parent(approval_id, user=author)]),
        _config(),
    )

    with pytest.raises(PermissionError, match="OpenAI Slack bot"):
        service.bind_notice(
            approval_id,
            channel_id=CHANNEL_ID,
            thread_ts=THREAD_TS,
            payload_fingerprint=FINGERPRINT,
        )


def test_bind_notice_rejects_fingerprint_not_in_canonical_approval_action() -> None:
    ledger, approval_id = _pending_approval()
    service = SlackApprovalHITLService(ledger, _client([_parent(approval_id)]), _config())

    with pytest.raises(PermissionError, match="fingerprint"):
        service.bind_notice(
            approval_id,
            channel_id=CHANNEL_ID,
            thread_ts=THREAD_TS,
            payload_fingerprint="b" * 64,
        )


def test_config_from_env_requires_runtime_approver_identity() -> None:
    config = SlackHITLConfig.from_env(
        {
            "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
            "MESH_COS_SLACK_APPROVER_USER_ID": APPROVER_USER_ID,
            "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
            "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS": (
                f"{CHATGPT_SLACK_USER_ID},{CHATGPT_AGENTS_SLACK_USER_ID}"
            ),
        }
    )
    assert config == _config()

    with pytest.raises(RuntimeError, match="approver user ID is required"):
        SlackHITLConfig.from_env(
            {
                "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
                "MESH_COS_SLACK_APPROVER_USER_ID": "",
                "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
            }
        )
