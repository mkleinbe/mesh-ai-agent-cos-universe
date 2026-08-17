from __future__ import annotations

from datetime import datetime, timedelta

from mesh_cos.ledger import TaskLedger
from mesh_cos.metrics import MetricsService
from mesh_cos.models import AuthorityLevel, TaskRecord, TaskStatus


def test_metrics_summary_accepts_legacy_naive_check_timestamp() -> None:
    ledger = TaskLedger()
    task = TaskRecord(
        task_id="T-naive-metrics",
        objective="objective",
        expected_outcome="outcome",
        requested_by="michael",
        executive_sponsor="michael",
        accountable_agent="cro",
        decision_owner="michael",
        status=TaskStatus.IN_PROGRESS,
        authority_level=AuthorityLevel.L2,
        acceptance_test="accepted",
    )
    task.next_check_at = (datetime.now() - timedelta(minutes=5)).replace(microsecond=0).isoformat()
    ledger.save_task(task)

    summary = MetricsService(ledger).summary()
    assert summary["stalled_task_rate"] == 1.0
