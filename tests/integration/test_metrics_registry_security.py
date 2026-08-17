from __future__ import annotations

from mesh_cos.ledger import TaskLedger
from mesh_cos.metrics import MetricsService
from mesh_cos.models import TaskRecord, TaskStatus
from mesh_cos.registry import AgentRegistry
from mesh_cos.registry_service import RegistryControlPlane


def test_registry_health_change_is_durable_and_audited(tmp_path):
    ledger = TaskLedger(tmp_path / "db.sqlite")
    registry = AgentRegistry.from_file("agents/registry.json")
    control = RegistryControlPlane(registry=registry, ledger=ledger)
    changed = control.set_health("cro", "WATCH", actor="cos", reason="elevated rework")
    assert changed["runtime_health"] == "WATCH"
    assert ledger.list_registry_changes("cro")[-1]["to_health"] == "WATCH"
    assert any(e["event_type"] == "registry_health_changed" for e in ledger.list_events())

    reloaded = AgentRegistry.from_file("agents/registry.json")
    RegistryControlPlane(registry=reloaded, ledger=ledger).apply_persisted_overrides()
    assert reloaded.get("cro")["runtime_health"] == "WATCH"


def test_phase1_success_metrics_are_derived_not_fabricated(tmp_path):
    ledger = TaskLedger(tmp_path / "db.sqlite")
    task = TaskRecord(
        task_id="T1", objective="o", expected_outcome="e", requested_by="m", executive_sponsor="m",
        accountable_agent="cro", decision_owner="m", acceptance_test="a", status=TaskStatus.CLOSED,
        contributors=["cfo", "coo"], CEO_touches=0, rework_count=0,
    )
    task.outcome_evidence = ["verification://1"]
    ledger.save_task(task)
    ledger.record_metric({"metric_id":"M1","metric_name":"answer_desk_disposition","task_id":None,"agent_id":"answer-desk","timestamp":task.created_at,"value":1.0,"disposition":"ANSWERED"})
    metrics = MetricsService(ledger).snapshot()
    assert metrics["verified_outcome_rate"] == 1.0
    assert metrics["work_resolved_without_michael"] == 1.0
    assert metrics["questions_deflected_from_michael"] == 1
    assert metrics["average_contributors_per_task"] == 2.0
    assert metrics["cost_per_verified_outcome"] is None
