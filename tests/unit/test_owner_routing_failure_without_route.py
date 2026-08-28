from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def test_owner_runtime_failure_without_persisted_route_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = MCPRuntime(TaskLedger())
    parent = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "parent",
            "expected_outcome": "delegated result",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": "cos",
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "evidence exists",
        },
    )
    child = runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": "marketing",
                    "expected_outcome": "marketing result",
                    "accountable_agent": "cmo",
                    "authority_level": 2,
                    "acceptance_test": "marketing evidence exists",
                }
            ],
        },
    )[0]
    runtime.call_agent(
        "cos",
        "delegation.create",
        {
            "delegation": {
                "delegation_id": "D-CMO-NOROUTE",
                "task_id": child["task_id"],
                "parent_task_id": parent["task_id"],
                "accountable_agent": "cmo",
                "business_objective": child["objective"],
                "expected_outcome": child["expected_outcome"],
                "deliverable": "result",
                "success_criteria": ["evidence exists"],
                "priority": "P1",
                "authority_level": 2,
                "acceptance_test": child["acceptance_test"],
                "approval_gates": [],
            },
            "parent_authority": 2,
            "depth": 1,
            "ancestry": ["cos"],
            "parent_approval_gates": [],
        },
    )
    runtime.registry["cmo"]["runtime_health"] = "WATCH"
    original_get = runtime.ledger.get_record

    def get_record(record_type: str, record_id: str):
        if record_type == "owner_execution_route":
            return None
        return original_get(record_type, record_id)

    monkeypatch.setattr(runtime.ledger, "get_record", get_record)
    with pytest.raises(RuntimeError, match="OWNER_RUNTIME_UNAVAILABLE"):
        runtime.call_agent(
            "cos",
            "delegation.execute_owner",
            {
                "delegation_id": "D-CMO-NOROUTE",
                "task_id": child["task_id"],
                "tool_name": "task.get",
                "arguments": {"task_id": child["task_id"]},
                "idempotency_key": "owner-down-no-route",
            },
        )
    failure = runtime.ledger.list_records("owner_routing_failure")[-1]
    assert failure["failure_classification"] == "OWNER_RUNTIME_UNAVAILABLE"
