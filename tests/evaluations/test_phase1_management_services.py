from datetime import datetime, timezone

import pytest

from mesh_cos.answer_desk import AnswerDeskService
from mesh_cos.conflict import ConflictService
from mesh_cos.delegation import DelegationService
from mesh_cos.ledger import TaskLedger
from mesh_cos.metrics import MetricsService
from mesh_cos.models import AuthorityLevel, Delegation, TaskRecord
from mesh_cos.reliability import ExecutionPolicy, execute_with_policy


def test_delegation_service_persists_and_inherits_approval_obligations():
    ledger = TaskLedger()
    service = DelegationService(ledger)
    delegation = Delegation(
        delegation_id="D1", task_id="T1", delegating_agent="cos", accountable_agent="cro",
        business_objective="win", expected_outcome="decision", deliverable="brief",
        success_criteria=["evidence"], priority="P1", authority_level=AuthorityLevel.L3,
        acceptance_test="accepted", permitted_actions=["research"], prohibited_actions=["pricing_approval"],
        approval_gates=["pricing"],
    )
    saved = service.create(delegation, parent_authority=3, depth=1, parent_approval_gates=["pricing"])
    assert saved["approval_gates"] == ["pricing"]
    assert ledger.get_record("delegation", "D1")["accountable_agent"] == "cro"


def test_delegation_cannot_drop_parent_approval_gate():
    ledger = TaskLedger()
    service = DelegationService(ledger)
    delegation = Delegation("D2", "T1", "cos", "cro", "o", "e", "d", ["ok"], "P1", AuthorityLevel.L2, "a")
    with pytest.raises(PermissionError):
        service.create(delegation, parent_authority=3, depth=1, parent_approval_gates=["pricing"])


def test_conflict_service_persists_decision_and_reversal_condition():
    ledger = TaskLedger()
    service = ConflictService(ledger)
    conflict = service.open("T1", "finance vs commercial", ["margin", "strategic value"])
    decision = service.decide(conflict["conflict_id"], owner="cos", disposition="protect margin", reversal_condition="client funds premium")
    assert ledger.get_record("conflict", conflict["conflict_id"])["status"] == "DECIDED"
    assert decision["reversal_condition"] == "client funds premium"


def test_answer_desk_service_records_disposition_metric():
    ledger = TaskLedger()
    service = AnswerDeskService(ledger)
    result = service.handle(
        request_id="Q1", known_fact=True, source_accessible=True, established_policy=False,
        reversible=True, requires_judgment=False, ceo_authority=False,
        requester_permissions=set(), source_class="approved",
    )
    assert result.disposition == "ANSWERED"
    assert ledger.get_record("answer_desk", "Q1")["disposition"] == "ANSWERED"


def test_reliability_policy_retries_transient_failures_without_duplicate_success():
    attempts = {"count": 0}
    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise TimeoutError("transient")
        return "ok"
    result = execute_with_policy(flaky, ExecutionPolicy(max_attempts=3, retry_exceptions=(TimeoutError,)))
    assert result == "ok"
    assert attempts["count"] == 3


def test_metrics_service_aggregates_ceo_leverage_and_outcomes():
    ledger = TaskLedger()
    t1 = TaskRecord("T1", "o", "e", "m", "m", "cro", "m", acceptance_test="a", CEO_touches=0)
    t1.outcome = "won"
    t1.status = __import__("mesh_cos.models", fromlist=["TaskStatus"]).TaskStatus.VERIFIED
    t1.ceo_time_avoided_estimate_minutes = 30
    t1.ceo_time_avoided_methodology = "calendar comparison"
    ledger.save_task(t1)
    ledger.save_record("metric_task", "T1", {"verified": True, "ceo_touches": 0, "ceo_time_avoided_estimate_minutes": 30, "methodology": "calendar comparison"})
    summary = MetricsService(ledger).summary()
    assert summary["verified_outcomes"] == 1
    assert summary["tasks_resolved_without_ceo"] == 1
    assert summary["ceo_time_avoided_minutes"] == 30
