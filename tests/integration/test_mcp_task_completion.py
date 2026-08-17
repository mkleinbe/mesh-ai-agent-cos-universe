from __future__ import annotations

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def test_remote_worker_can_complete_with_outcome_evidence_and_cos_can_verify() -> None:
    runtime = MCPRuntime(TaskLedger())
    created = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "Produce commercial recommendation",
            "expected_outcome": "Evidence-backed recommendation",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cro",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "Recommendation cites approved evidence",
            "idempotency_key": "mcp-complete-1",
        },
    )
    task_id = created["task_id"]
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        runtime.call_agent("cro", "task.transition", {"task_id": task_id, "target": target})

    completed = runtime.call_agent(
        "cro",
        "task.complete",
        {
            "task_id": task_id,
            "outcome": "Recommend pursuit",
            "evidence": ["evidence://commercial/1"],
        },
    )
    assert completed["status"] == "COMPLETED"
    assert completed["outcome_evidence"] == ["evidence://commercial/1"]

    verified = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": task_id,
            "passed": True,
            "reason": "Acceptance test passed",
            "evidence_references": ["evidence://commercial/1"],
        },
    )
    assert verified["status"] == "VERIFIED"


def test_non_owner_cannot_complete_task() -> None:
    runtime = MCPRuntime(TaskLedger())
    created = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "Finance work",
            "expected_outcome": "Economics",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cfo",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "Economics supported",
        },
    )
    task_id = created["task_id"]
    import pytest

    with pytest.raises(PermissionError, match="accountable owner"):
        runtime.call_agent(
            "cro",
            "task.complete",
            {"task_id": task_id, "outcome": "spoof", "evidence": ["evidence://bad"]},
        )
