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

CHANNEL_ID = "C0BRL4GCL3A"
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
    adapters = GovernedAdapterRegistry(load_registry(), GovernanceJournal(ledger))
    return MCPRuntime(ledger, adapters=adapters), ledger, approval.approval_id


def _invoke(runtime: MCPRuntime, payload: dict) -> dict:
    return runtime.call_agent(
        "cos",
        "skills.invoke_governed",
        {"capability": "slack-adapter", "payload": payload},
    )


def test_cos_can_request_connected_slack_collaboration_without_creating_approval() -> None:
    runtime, ledger, approval_id = _runtime()

    handoff = _invoke(
        runtime,
        {
            "operation": "handoff",
            "channel_id": CHANNEL_ID,
            "payload": {
                "intent": "post approval request",
                "approval_id": approval_id,
                "payload_fingerprint": FINGERPRINT,
            },
        },
    )
    assert handoff["execution_mode"] == "CHATGPT_CONNECTOR_HANDOFF"
    assert handoff["connector"] == "Slack"
    assert handoff["authority"] == "COLLABORATION_ONLY"
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"

    with pytest.raises(PermissionError, match="collaboration-only"):
        _invoke(runtime, {"operation": "ingest_decision", "channel_id": CHANNEL_ID})
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
                "payload": {"operation": "handoff", "channel_id": CHANNEL_ID, "payload": {}},
            },
        )
    with pytest.raises(PermissionError, match="canonical approval authority"):
        _invoke(
            runtime,
            {
                "operation": "handoff",
                "channel_id": CHANNEL_ID,
                "payload": {},
                "approved": True,
            },
        )
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"
