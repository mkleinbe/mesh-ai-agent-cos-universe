from __future__ import annotations

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.approval import ApprovalService
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.slack import SlackWebClient
from mesh_cos.slack_hitl import (
    CHATGPT_AGENTS_SLACK_USER_ID,
    CHATGPT_SLACK_USER_ID,
    SlackApprovalHITLService,
    SlackHITLConfig,
)

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
THREAD_TS = "1788000000.000001"
FINGERPRINT = "c" * 64


def _runtime() -> tuple[MCPRuntime, TaskLedger, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Execute one approved Gmail send",
        expected_outcome="Only the exact human-approved payload is actionable",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="canonical approval and provider identity evidence reconcile",
        idempotency_key="MCP-SLACK-HITL-001",
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
        f"Send exact Gmail draft with payload_fingerprint={FINGERPRINT}",
    )
    messages = [
        {
            "type": "message",
            "user": CHATGPT_AGENTS_SLACK_USER_ID,
            "ts": THREAD_TS,
            "text": (
                f"HITL APPROVAL REQUIRED\n<@{APPROVER_USER_ID}>\n"
                f"Approval ID: {approval.approval_id}\n"
                f"Payload fingerprint: {FINGERPRINT}\n"
                "Approval owner: MK / Michael"
            ),
        }
    ]

    def transport(method: str, payload: dict, token: str) -> dict:
        assert method == "conversations.replies"
        assert payload == {"channel": CHANNEL_ID, "ts": THREAD_TS}
        assert token == "xoxb-read-only-verifier"
        return {"ok": True, "messages": messages}

    service = SlackApprovalHITLService(
        ledger,
        SlackWebClient("xoxb-read-only-verifier", transport=transport),
        SlackHITLConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
            approver_principal="michael",
            allowed_notice_author_ids=frozenset(
                {CHATGPT_SLACK_USER_ID, CHATGPT_AGENTS_SLACK_USER_ID}
            ),
        ),
    )
    adapters = GovernedAdapterRegistry(
        load_registry(),
        GovernanceJournal(ledger),
        slack_hitl=service,
    )
    return MCPRuntime(ledger, adapters=adapters), ledger, approval.approval_id


def _invoke(runtime: MCPRuntime, payload: dict) -> dict:
    return runtime.call_agent(
        "cos",
        "skills.invoke_governed",
        {"capability": "slack-adapter", "payload": payload},
    )


def test_cos_can_provider_verify_bot_notice_but_cannot_ingest_human_decision() -> None:
    runtime, ledger, approval_id = _runtime()

    binding = _invoke(
        runtime,
        {
            "operation": "bind_notice",
            "approval_id": approval_id,
            "thread_ts": THREAD_TS,
            "payload_fingerprint": FINGERPRINT,
        },
    )
    assert binding["notice_author_user_id"] == CHATGPT_AGENTS_SLACK_USER_ID
    assert binding["approver_user_id"] == APPROVER_USER_ID
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"

    with pytest.raises(PermissionError, match="cannot record human decisions"):
        _invoke(runtime, {"operation": "ingest_decision", "approval_id": approval_id})
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_mcp_agent_surface_does_not_expand_human_approval_authority() -> None:
    runtime, ledger, approval_id = _runtime()

    with pytest.raises(PermissionError, match="authenticated human principal"):
        runtime.call_agent(
            "cos",
            "approval.record_decision",
            {"approval_id": approval_id, "approved": True, "reason": "agent attempt"},
        )
    with pytest.raises(PermissionError):
        runtime.call_agent(
            "cro",
            "skills.invoke_governed",
            {
                "capability": "slack-adapter",
                "payload": {"operation": "bind_notice", "approval_id": approval_id},
            },
        )
    with pytest.raises(PermissionError, match="cannot record human decisions"):
        _invoke(
            runtime,
            {
                "operation": "ingest_decision",
                "approval_id": approval_id,
                "approved": True,
            },
        )
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"
