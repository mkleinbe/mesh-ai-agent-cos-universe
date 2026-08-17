from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

import pytest

from mesh_cos.agentops_service import AgentOpsService, PerformancePolicy
from mesh_cos.answer_desk_service import AnswerDeskService, SourceResult
from mesh_cos.authority import classify
from mesh_cos.execution_service import AgentExecutionService
from mesh_cos.functional_runtime import FunctionalRuntime
from mesh_cos.governance import GovernanceService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import CoSService
from mesh_cos.registry import AgentRegistry
from mesh_cos.slack_adapter import SlackAdapter, SlackEventReceiver
from mesh_cos.staffing import readiness
from mesh_cos.verification import VerificationResult


class FakeSlack:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def post_message(self, *, channel: str, text: str, thread_ts: str | None = None) -> dict:
        ts = thread_ts or f"{len(self.calls) + 1}.000"
        self.calls.append({"channel": channel, "text": text, "thread_ts": thread_ts, "ts": ts})
        return {"ok": True, "ts": ts}


def services(tmp_path, invokers=None):
    ledger = TaskLedger(tmp_path / "phase1.sqlite")
    registry = AgentRegistry.from_file("agents/registry.json")
    cos = CoSService(ledger=ledger, registry=registry)
    runtime = FunctionalRuntime(registry, invokers or {})
    execution = AgentExecutionService(cos=cos, runtime=runtime, ledger=ledger)
    return ledger, registry, cos, execution


def fake_result(tool: str, source: str | None, payload: dict) -> dict:
    return {"tool": tool, "source": source, "payload": payload, "evidence": f"evidence://{tool}"}


def test_pursuit_proposal_orchestrates_cross_functional_contributors(tmp_path):
    invokers = {agent: fake_result for agent in ("cro", "cfo", "coo", "devils-advocate")}
    ledger, _, cos, execute = services(tmp_path, invokers)
    task = cos.intake(
        objective="Qualify pursuit and prepare recommendation",
        expected_outcome="Decision-ready pursuit recommendation",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        contributors=["cfo", "coo", "devils-advocate"],
        decision_owner="michael",
        authority_level=AuthorityLevel.L3,
        acceptance_test="commercial evidence, economics, feasibility and challenge are present",
    )
    cos.plan(task.task_id)
    cos.assign(task.task_id)
    cos.start(task.task_id)
    revenue = execute.execute(task_id=task.task_id, agent_id="cro", tool="mesh-revenue-intelligence", payload={"pursuit": "Fulton"})
    economics = execute.execute(task_id=task.task_id, agent_id="cfo", tool="financial-modeling", payload={"scenario": "base"})
    feasibility = execute.execute(task_id=task.task_id, agent_id="coo", tool="staffing-readiness", payload={"need": "strategy pod"})
    challenge = execute.execute(task_id=task.task_id, agent_id="devils-advocate", tool="mesh-devils-advocate", payload={"decision": "pursue"})
    cos.qa(task.task_id)
    cos.complete(task.task_id, outcome="recommendation ready", evidence=[revenue["evidence"], economics["evidence"], feasibility["evidence"], challenge["evidence"]])
    cos.verify(task.task_id, lambda _: VerificationResult(True, ["verification://pursuit"], "all required evidence present"))
    closed = cos.close(task.task_id)
    assert closed.status == TaskStatus.CLOSED
    actors = {event["actor_agent"] for event in ledger.list_events(task.task_id)}
    assert {"cro", "cfo", "coo", "devils-advocate"}.issubset(actors)


def test_engagement_economics_requires_recorded_human_approval(tmp_path):
    ledger, _, cos, _ = services(tmp_path)
    task = cos.intake(
        objective="Select pricing scenario",
        expected_outcome="Approved engagement economics",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cfo",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="approved economics are recorded",
    )
    cos.plan(task.task_id)
    cos.assign(task.task_id)
    cos.start(task.task_id)
    cos.qa(task.task_id)
    cos.ready_for_decision(task.task_id)
    approval = cos.request_human_approval(task.task_id, requested_by="cos", approval_owner="michael", authority_level=AuthorityLevel.L4, action="pricing")
    cos.decide_human_approval(approval.approval_id, actor="michael", approved=True, reason="economics acceptable")
    decision = GovernanceService(ledger).record_decision(
        task_id=task.task_id,
        decision_owner="michael",
        decision="approve base scenario",
        rationale="margin and strategic value acceptable",
        authority_level=AuthorityLevel.L4,
        approval_reference=approval.approval_id,
    )
    assert decision["approval_reference"] == approval.approval_id
    cos.complete(task.task_id, outcome="pricing scenario approved", evidence=[f"approval://{approval.approval_id}"])
    cos.verify(task.task_id, lambda _: VerificationResult(True, ["verification://economics"], "approval and decision recorded"))
    assert cos.close(task.task_id).status == TaskStatus.CLOSED


def test_consultant_staffing_stale_availability_blocks_commitment(tmp_path):
    def staffing_invoker(tool: str, source: str | None, payload: dict) -> str:
        return readiness(**payload)

    _, _, cos, execute = services(tmp_path, {"coo": staffing_invoker})
    task = cos.intake(
        objective="Confirm staffing readiness",
        expected_outcome="Evidence-backed staffing status",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="coo",
        decision_owner="michael",
        acceptance_test="availability is fresh and readiness is confirmed",
    )
    cos.plan(task.task_id)
    cos.assign(task.task_id)
    cos.start(task.task_id)
    old = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    result = execute.execute(
        task_id=task.task_id,
        agent_id="coo",
        tool="staffing-readiness",
        payload={
            "capability_match": True,
            "availability_checked_at": old,
            "max_age_days": 30,
            "rate_valid": True,
            "contracting_ready": True,
            "availability_confirmed": True,
        },
    )
    assert result == "REQUIRES_REFRESH"
    assert cos.block(task.task_id, "consultant availability requires refresh").status == TaskStatus.BLOCKED


def test_marketing_publication_remains_l4_gated(tmp_path):
    decision = classify("public_publish")
    assert decision.required_level == AuthorityLevel.L4
    assert decision.human_approval_required
    ledger, _, cos, _ = services(tmp_path)
    task = cos.intake(
        objective="Prepare thought leadership",
        expected_outcome="Publication-ready approved content",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cmo",
        contributors=["vp-content"],
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="content is approved for publication",
    )
    cos.plan(task.task_id)
    cos.assign(task.task_id)
    cos.start(task.task_id)
    approval = cos.request_human_approval(task.task_id, requested_by="cmo", approval_owner="michael", authority_level=AuthorityLevel.L4, action="public_publish")
    assert ledger.get_approval(approval.approval_id)["status"] == "PENDING"
    assert ledger.get_task(task.task_id).status == TaskStatus.AWAITING_APPROVAL


def test_answer_desk_permission_routing_and_approval_dispositions(tmp_path):
    ledger, registry, _, _ = services(tmp_path)

    def retriever(question: str) -> SourceResult:
        if "private" in question:
            return SourceResult(True, "secret", "mesh://private", "private_dm", "cro")
        return SourceResult(True, "known status", "mesh://status", "approved", "cro")

    desk = AnswerDeskService(registry=registry, retriever=retriever, ledger=ledger)
    assert desk.handle("status?", requester="team", requester_permissions=set()).disposition == "ANSWERED"
    assert desk.handle("private status?", requester="team", requester_permissions=set()).disposition == "BLOCKED_BY_ACCESS"
    assert desk.handle("approve this?", requester="team", requester_permissions=set(), approval_required=True).disposition == "APPROVAL_REQUIRED"


def test_agent_performance_failure_and_slack_security_controls(tmp_path):
    ledger, _, _, _ = services(tmp_path)
    policy = PerformancePolicy.from_file("config/performance-policy.v1.json")
    agentops = AgentOpsService(ledger=ledger, policy=policy)
    agentops.record(agent_id="cro", task_id="T1", category="evidence_governance", score=0.0, severity="CRITICAL", reason="fabricated material evidence")
    assert agentops.portfolio_recommendation(agent_id="cro") == "QUARANTINE"

    slack = FakeSlack()
    adapter = SlackAdapter(ledger=ledger, transport=slack, agent_ops_channel_id="C0BRL4GCL3A")
    receiver = SlackEventReceiver(signing_secret="secret", adapter=adapter)
    payload = {"type": "event_callback", "event_id": "EV1", "event": {"type": "app_mention", "text": "status"}}
    body = json.dumps(payload, separators=(",", ":"))
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signature = SlackAdapter.signature_for_test("secret", timestamp, body)
    headers = {"X-Slack-Request-Timestamp": timestamp, "X-Slack-Signature": signature}
    assert receiver.process(headers, body)["accepted"] is True
    assert receiver.process(headers, body) is None
    with pytest.raises(PermissionError):
        receiver.process({**headers, "X-Slack-Signature": "v0=bad"}, body)
