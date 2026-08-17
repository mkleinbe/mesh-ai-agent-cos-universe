from __future__ import annotations

from datetime import datetime, timezone
import json

import pytest

from mesh_cos.adapters import AdapterRegistry, AuthorizationGateway, FunctionalAgentAdapter
from mesh_cos.agentops_service import AgentOpsService, PerformancePolicy
from mesh_cos.answer_desk_service import AnswerDeskService, SourceResult
from mesh_cos.governance import GovernanceService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, Delegation, TaskStatus
from mesh_cos.orchestration import CoSService
from mesh_cos.registry import AgentRegistry
from mesh_cos.reliability import ExecutionPolicy, execute_with_policy
from mesh_cos.slack_adapter import SlackAdapter, verify_request_signature
from mesh_cos.verification import VerificationResult


class FakeSlack:
    def __init__(self):
        self.calls: list[dict] = []

    def post_message(self, *, channel: str, text: str, thread_ts: str | None = None) -> dict:
        ts = thread_ts or f"{len(self.calls) + 1}.000"
        self.calls.append({"channel": channel, "text": text, "thread_ts": thread_ts, "ts": ts})
        return {"ok": True, "ts": ts}


def build_service(tmp_path):
    ledger = TaskLedger(tmp_path / "mesh.db")
    registry = AgentRegistry.from_file("agents/registry.json")
    return CoSService(ledger=ledger, registry=registry), ledger, registry


def test_cos_executes_outcome_through_verified_closure(tmp_path):
    service, ledger, registry = build_service(tmp_path)
    task = service.intake(
        objective="Prepare pursuit recommendation",
        expected_outcome="Decision-ready pursuit recommendation",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        authority_level=AuthorityLevel.L3,
        acceptance_test="decision_ready",
        idempotency_key="intake-1",
    )
    service.plan(task.task_id)
    delegation = Delegation(
        delegation_id="D1",
        task_id=task.task_id,
        delegating_agent="cos",
        accountable_agent="cro",
        business_objective=task.objective,
        expected_outcome=task.expected_outcome,
        deliverable="recommendation",
        success_criteria=["evidence cited", "tradeoff explicit"],
        priority="P1",
        authority_level=AuthorityLevel.L3,
        acceptance_test="decision_ready",
        permitted_actions=["commercial_analysis"],
        prohibited_actions=["pricing_approval"],
    )
    service.delegate(task.task_id, delegation)
    service.start(task.task_id)
    service.qa(task.task_id)
    service.complete(task.task_id, outcome="Pursuit recommendation ready", evidence=["evidence://revenue", "evidence://staffing"])
    verified = service.verify(
        task.task_id,
        lambda _: VerificationResult(True, ["verification://decision-brief"], "acceptance test passed"),
    )
    assert verified.status == TaskStatus.VERIFIED
    closed = service.close(task.task_id)
    assert closed.status == TaskStatus.CLOSED
    assert ledger.get_delegation("D1")["accountable_agent"] == "cro"
    assert ledger.list_events(task.task_id)
    assert registry.get("cro")["decision_authority"] == 3


def test_failed_acceptance_returns_to_rework(tmp_path):
    service, _, _ = build_service(tmp_path)
    task = service.intake(
        objective="Create content",
        expected_outcome="Approved content",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cmo",
        decision_owner="michael",
        acceptance_test="approved_content",
    )
    service.plan(task.task_id)
    service.assign(task.task_id)
    service.start(task.task_id)
    service.qa(task.task_id)
    service.complete(task.task_id, outcome="draft", evidence=["artifact://draft"])
    result = service.verify(task.task_id, lambda _: VerificationResult(False, ["qa://fail"], "approval absent"))
    assert result.status == TaskStatus.REWORK
    assert result.rework_count == 1


def test_slack_signature_thread_mapping_and_durable_dedupe(tmp_path):
    _, ledger, _ = build_service(tmp_path)
    slack = FakeSlack()
    adapter = SlackAdapter(ledger=ledger, transport=slack, agent_ops_channel_id="C0BRL4GCL3A")
    task = {"task_id": "T-SLACK", "objective": "Coordinate", "priority": "P1", "accountable_agent": "cro", "status": "ASSIGNED"}
    ts1 = adapter.ensure_task_thread(task)
    ts2 = adapter.ensure_task_thread(task)
    assert ts1 == ts2
    assert len(slack.calls) == 1
    assert ledger.get_thread_mapping("T-SLACK")["channel_id"] == "C0BRL4GCL3A"
    assert adapter.accept_event("evt-1") is True
    assert adapter.accept_event("evt-1") is False

    body = json.dumps({"type": "event_callback"}, separators=(",", ":"))
    timestamp = str(int(datetime.now(timezone.utc).timestamp()))
    signature = SlackAdapter.signature_for_test("secret", timestamp, body)
    assert verify_request_signature("secret", timestamp, body, signature)
    assert not verify_request_signature("wrong", timestamp, body, signature)


def test_authorization_gateway_and_functional_adapter(tmp_path):
    _, _, registry = build_service(tmp_path)
    gateway = AuthorizationGateway(registry)
    seen: list[tuple[str, str]] = []

    def invoke(tool: str, source: str | None, payload: dict) -> dict:
        seen.append((tool, source or ""))
        return {"ok": True, "payload": payload}

    adapter = FunctionalAgentAdapter("cro", gateway=gateway, invoker=invoke)
    result = adapter.execute(tool="mesh-revenue-intelligence", source=None, payload={"opportunity": "X"})
    assert result["ok"] is True
    assert seen
    with pytest.raises(PermissionError):
        adapter.execute(tool="unauthorized-tool", source=None, payload={})

    adapters = AdapterRegistry([adapter])
    assert adapters.get("cro") is adapter


def test_governance_answerdesk_agentops_metrics_and_reliability(tmp_path):
    service, ledger, registry = build_service(tmp_path)
    governance = GovernanceService(ledger)
    conflict = governance.create_conflict(
        task_id="T1",
        created_by="cos",
        uncontested_facts=["staffing feasible"],
        disputed_facts=["margin acceptable"],
        source_authority={"margin": "cfo"},
        options=["A", "B"],
        positions={"cfo": "A", "cro": "B"},
        confidence={"cfo": 0.9, "cro": 0.7},
        reversibility="reversible",
        decision_owner="michael",
    )
    decision = governance.record_decision(
        task_id="T1",
        decision_owner="michael",
        decision="A",
        rationale="preserve economics",
        authority_level=AuthorityLevel.L4,
        approval_reference="APR-1",
    )
    assert ledger.get_conflict(conflict["conflict_id"])["decision_owner"] == "michael"
    assert ledger.get_decision(decision["decision_id"])["decision"] == "A"

    def retriever(question: str) -> SourceResult:
        return SourceResult(found=True, value="known", source_ref="mesh://source", source_class="approved", owner="cro")

    desk = AnswerDeskService(registry=registry, retriever=retriever, ledger=ledger)
    answer = desk.handle("What is the status?", requester="team", requester_permissions=set())
    assert answer.disposition == "ANSWERED"

    policy = PerformancePolicy.from_file("config/performance-policy.v1.json")
    agentops = AgentOpsService(ledger=ledger, policy=policy)
    agentops.record(agent_id="cro", task_id="T1", category="outcome_achievement", score=1.0)
    agentops.record(agent_id="cro", task_id="T1", category="first_pass_quality", score=0.8)
    scorecard = agentops.scorecard("cro", window_start="2026-08-01T00:00:00+00:00", window_end="2026-09-01T00:00:00+00:00")
    assert scorecard["weights_version"] == policy.version
    assert 0 <= scorecard["weighted_score"] <= 1

    calls = {"n": 0}
    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("temporary")
        return "ok"
    assert execute_with_policy(flaky, ExecutionPolicy(max_attempts=2, timeout_seconds=1)) == "ok"


def test_intake_idempotency_prevents_duplicate_task(tmp_path):
    service, ledger, _ = build_service(tmp_path)
    first = service.intake(
        objective="One",
        expected_outcome="Done",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        acceptance_test="done",
        idempotency_key="same-request",
    )
    second = service.intake(
        objective="One",
        expected_outcome="Done",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        acceptance_test="done",
        idempotency_key="same-request",
    )
    assert first.task_id == second.task_id
    assert len(ledger.list_tasks()) == 1
