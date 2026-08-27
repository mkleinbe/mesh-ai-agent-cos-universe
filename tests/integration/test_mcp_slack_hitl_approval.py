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
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI

CHANNEL_ID = "C0BRL4GCL3A"
FINGERPRINT = "c" * 64


def _runtime() -> tuple[MCPRuntime, TaskLedger, str]:
    ledger = TaskLedger(); cos = ChiefOfStaffService(ledger)
    task = cos.intake(objective="Execute one approved Gmail send", expected_outcome="Only the exact human-approved payload is actionable", requested_by="cos", executive_sponsor="michael", accountable_agent="cos", decision_owner="michael", authority_level=AuthorityLevel.L4, acceptance_test="canonical approval and provider identity evidence reconcile", idempotency_key="MCP-SLACK-HITL-001")
    for target in (TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS): cos.advance(task.task_id, target)
    approval = ApprovalService(ledger).request(task.task_id, "cos", "michael", AuthorityLevel.L4, f"Send exact Gmail draft with payload_fingerprint={FINGERPRINT}")
    api = SlackBotAPI("xoxb-test", lambda method, payload, token: {"ok": True, "channel": CHANNEL_ID, "ts": "1787843216.789639"})
    adapters = GovernedAdapterRegistry(load_registry(), GovernanceJournal(ledger), slack_notifier=SlackApprovalNotifier(ledger, api, CHANNEL_ID))
    return MCPRuntime(ledger, adapters=adapters), ledger, approval.approval_id


def _invoke(runtime: MCPRuntime, payload: dict) -> dict:
    return runtime.call_agent("cos", "skills.invoke_governed", {"capability": "slack-adapter", "payload": payload})


def test_cos_can_post_governed_slack_approval_without_creating_new_authority() -> None:
    runtime, ledger, approval_id = _runtime()
    posted = _invoke(runtime, {"operation": "post_approval", "channel_id": CHANNEL_ID, "payload": {"approval_id": approval_id}})
    assert posted["status"] == "POSTED"; assert posted["execution_mode"] == "SLACK_BOT_API"; assert posted["approval_id"] == approval_id; assert ledger.get_record("approval", approval_id)["status"] == "PENDING"; assert ledger.get_record("approval_slack_thread_binding", posted["thread_ts"])["approval_id"] == approval_id
    with pytest.raises(PermissionError, match="Unsupported governed Slack bot operation"): _invoke(runtime, {"operation": "ingest_decision", "channel_id": CHANNEL_ID, "payload": {}})
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_mcp_agent_surface_does_not_expand_human_approval_authority() -> None:
    runtime, ledger, approval_id = _runtime()
    with pytest.raises(PermissionError, match="authenticated human principal"): runtime.call_agent("cos", "approval.record_decision", {"approval_id": approval_id, "approved": True, "reason": "agent attempt"})
    with pytest.raises(PermissionError): runtime.call_agent("cro", "skills.invoke_governed", {"capability": "slack-adapter", "payload": {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "x"}}})
    with pytest.raises(PermissionError, match="canonical approval authority"): _invoke(runtime, {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "x"}, "approved": True})
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"
