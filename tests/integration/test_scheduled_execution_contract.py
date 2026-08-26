from __future__ import annotations

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def _intake_payload(key: str) -> dict:
    return {
        "objective": f"Execute scheduled occurrence {key}",
        "expected_outcome": "The occurrence is evaluated exactly once",
        "requested_by": "cos",
        "executive_sponsor": "michael",
        "accountable_agent": "cos",
        "decision_owner": "michael",
        "authority_level": 1,
        "acceptance_test": "canonical lifecycle and evidence prove exact-once evaluation",
        "idempotency_key": key,
    }


def test_scheduled_occurrence_is_idempotent_and_completes_only_through_valid_lifecycle() -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    key = "COM-HLTH-DLY-001:2026-08-26T08:00:00-04:00"

    first = runtime.call_agent("cos", "task.intake", _intake_payload(key))
    repeated = runtime.call_agent("cos", "task.intake", _intake_payload(key))
    assert first["task_id"] == repeated["task_id"]

    task_id = first["task_id"]
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        current = runtime.call_agent(
            "cos", "task.transition", {"task_id": task_id, "target": target}
        )
        assert current["status"] == target

    completed = runtime.call_agent(
        "cos",
        "task.complete",
        {
            "task_id": task_id,
            "outcome": "Scheduled health occurrence evaluated; no consequential action required.",
            "evidence": ["provider://synthetic-health-readback"],
        },
    )
    assert completed["status"] == "COMPLETED"

    verified = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": task_id,
            "passed": True,
            "reason": "Exact execution key, provider evidence, and lifecycle reconcile.",
            "evidence_references": ["provider://synthetic-health-readback"],
        },
    )
    assert verified["status"] == "VERIFIED"
    assert len(ledger.list_tasks()) == 1
