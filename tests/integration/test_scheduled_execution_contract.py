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


def test_scheduled_cos_trigger_routes_delegated_owner_and_resumes_idempotently() -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    key = "LI-NET-REENTRY:2026-08-26T08:00:00-04:00"
    parent = runtime.call_agent("cos", "task.intake", _intake_payload(key))
    repeated = runtime.call_agent("cos", "task.intake", _intake_payload(key))
    assert repeated["task_id"] == parent["task_id"]

    child = runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": "Evaluate the scheduled marketing occurrence",
                    "expected_outcome": "Evidence-backed CMO outcome",
                    "accountable_agent": "cmo",
                    "authority_level": 1,
                    "acceptance_test": "CMO evidence is recorded without external action",
                }
            ],
        },
    )[0]
    delegation = runtime.call_agent(
        "cos",
        "delegation.create",
        {
            "delegation": {
                "delegation_id": "D-SCHEDULED-CMO",
                "task_id": child["task_id"],
                "parent_task_id": parent["task_id"],
                "accountable_agent": "cmo",
                "business_objective": child["objective"],
                "expected_outcome": child["expected_outcome"],
                "deliverable": "scheduled occurrence result",
                "success_criteria": ["CMO evidence recorded"],
                "priority": "P1",
                "authority_level": 1,
                "acceptance_test": child["acceptance_test"],
                "approval_gates": [],
            },
            "parent_authority": 1,
            "depth": 1,
            "ancestry": ["cos"],
            "parent_approval_gates": [],
        },
    )
    assert delegation["accountable_agent"] == "cmo"

    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"), start=1):
        response = runtime.call_agent(
            "cos",
            "delegation.execute_owner",
            {
                "delegation_id": "D-SCHEDULED-CMO",
                "task_id": child["task_id"],
                "tool_name": "task.transition",
                "arguments": {"task_id": child["task_id"], "target": target},
                "idempotency_key": f"scheduled-cmo-transition-{index}",
            },
        )
        assert response["executing_principal"] == "cmo"
        assert response["result"]["status"] == target

    completion_request = {
        "delegation_id": "D-SCHEDULED-CMO",
        "task_id": child["task_id"],
        "tool_name": "task.complete",
        "arguments": {
            "task_id": child["task_id"],
            "outcome": "Scheduled CMO occurrence evaluated; no consequential action required.",
            "evidence": ["provider://synthetic-cmo-readback"],
        },
        "idempotency_key": "scheduled-cmo-complete",
    }
    completed = runtime.call_agent("cos", "delegation.execute_owner", completion_request)
    retried = runtime.call_agent("cos", "delegation.execute_owner", completion_request)
    assert retried == completed
    assert completed["executing_principal"] == "cmo"
    assert completed["result"]["status"] == "COMPLETED"
    assert runtime.call_agent("cos", "task.get", {"task_id": child["task_id"]})["status"] == "COMPLETED"

    verified = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": child["task_id"],
            "passed": True,
            "reason": "Owner identity, provider evidence, and scheduled idempotency reconcile.",
            "evidence_references": ["provider://synthetic-cmo-readback"],
        },
    )
    assert verified["status"] == "VERIFIED"
    assert len([task for task in ledger.list_tasks() if task.parent_task_id == parent["task_id"]]) == 1
