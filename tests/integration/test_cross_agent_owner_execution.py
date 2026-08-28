from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def intake(runtime: MCPRuntime, owner: str = "cos", *, key: str = "root") -> dict:
    return runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": f"{owner} governed work",
            "expected_outcome": "evidence-backed result",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": owner,
            "decision_owner": "michael",
            "authority_level": 2,
            "acceptance_test": "result is supported by evidence",
            "idempotency_key": key,
        },
    )


def child(runtime: MCPRuntime, parent: dict, owner: str) -> dict:
    return runtime.call_agent(
        parent["accountable_agent"],
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": f"{owner} child work",
                    "expected_outcome": f"{owner} evidence",
                    "accountable_agent": owner,
                    "authority_level": 2,
                    "acceptance_test": f"{owner} evidence is present",
                }
            ],
        },
    )[0]


def delegate(runtime: MCPRuntime, parent_owner: str, task: dict, delegation_id: str, *, depth: int) -> dict:
    return runtime.call_agent(
        parent_owner,
        "delegation.create",
        {
            "delegation": {
                "delegation_id": delegation_id,
                "task_id": task["task_id"],
                "parent_task_id": task["parent_task_id"],
                "accountable_agent": task["accountable_agent"],
                "business_objective": task["objective"],
                "expected_outcome": task["expected_outcome"],
                "deliverable": "governed result",
                "success_criteria": ["evidence supplied"],
                "priority": "P1",
                "authority_level": 2,
                "acceptance_test": task["acceptance_test"],
                "approval_gates": [],
            },
            "parent_authority": 2,
            "depth": depth,
            "ancestry": ["cos"] if depth == 1 else ["cos", parent_owner],
            "parent_approval_gates": [],
        },
    )


def execute_owner(runtime: MCPRuntime, caller: str, delegation_id: str, task_id: str, tool_name: str, arguments: dict, key: str) -> dict:
    return runtime.call_agent(
        caller,
        "delegation.execute_owner",
        {
            "delegation_id": delegation_id,
            "task_id": task_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "idempotency_key": key,
        },
    )


def test_pf057_cos_bound_runtime_routes_direct_report_lifecycle_without_impersonation() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    delegate(runtime, "cos", delegated, "D-CMO", depth=1)

    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"), start=1):
        result = execute_owner(
            runtime,
            "cos",
            "D-CMO",
            delegated["task_id"],
            "task.transition",
            {"task_id": delegated["task_id"], "target": target},
            f"D-CMO-transition-{index}",
        )
        assert result["executing_principal"] == "cmo"
        assert result["orchestrating_agent"] == "cos"
        assert result["result"]["status"] == target

    completed = execute_owner(
        runtime,
        "cos",
        "D-CMO",
        delegated["task_id"],
        "task.complete",
        {
            "task_id": delegated["task_id"],
            "outcome": "CMO completed delegated work",
            "evidence": ["synthetic://cmo/evidence"],
        },
        "D-CMO-complete",
    )
    assert completed["executing_principal"] == "cmo"
    assert completed["result"]["status"] == "COMPLETED"
    events = runtime.ledger.list_events()
    assert any(event["event_type"] == "task_complete" and event["actor_agent"] == "cmo" for event in events)


def test_parent_direct_completion_of_child_is_rejected() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cmo")
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"):
        runtime.call_agent("cmo", "task.transition", {"task_id": delegated["task_id"], "target": target})
    with pytest.raises(PermissionError, match="accountable owner"):
        runtime.call_agent(
            "cos",
            "task.complete",
            {
                "task_id": delegated["task_id"],
                "outcome": "false parent completion",
                "evidence": ["synthetic://invalid"],
            },
        )


def test_owner_lifecycle_audit_uses_authenticated_owner_identity() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    delegated = child(runtime, root, "cfo")
    runtime.call_agent("cfo", "task.transition", {"task_id": delegated["task_id"], "target": "TRIAGED"})
    event = runtime.ledger.list_events()[-1]
    assert event["event_type"] == "task_transition"
    assert event["actor_agent"] == "cfo"


def test_registry_driven_owner_readiness_requires_owner_lifecycle_transport() -> None:
    runtime = MCPRuntime(TaskLedger())
    for agent_id, record in runtime.registry.items():
        parent_id = record.get("parent_agent_id")
        if not parent_id:
            continue
        parent = runtime.registry[parent_id]
        if int(parent.get("max_delegation_depth", 0)) <= 0:
            continue
        allowed = set(runtime.policy.allowed_tools(agent_id))
        assert {"task.get", "task.transition", "task.check_in", "task.complete"}.issubset(allowed), agent_id


def test_nested_owner_execution_routes_cmo_to_vp_content_and_respects_depth_zero() -> None:
    runtime = MCPRuntime(TaskLedger())
    root = intake(runtime)
    cmo_task = child(runtime, root, "cmo")
    delegate(runtime, "cos", cmo_task, "D-CMO", depth=1)

    vp = execute_owner(
        runtime,
        "cos",
        "D-CMO",
        cmo_task["task_id"],
        "task.decompose",
        {
            "parent_task_id": cmo_task["task_id"],
            "work_packages": [
                {
                    "objective": "produce content",
                    "expected_outcome": "content artifact",
                    "accountable_agent": "vp-content",
                    "authority_level": 2,
                    "acceptance_test": "content evidence is present",
                }
            ],
        },
        "D-CMO-decompose-vp",
    )["result"][0]

    execute_owner(
        runtime,
        "cos",
        "D-CMO",
        cmo_task["task_id"],
        "delegation.create",
        {
            "delegation": {
                "delegation_id": "D-VP",
                "task_id": vp["task_id"],
                "parent_task_id": cmo_task["task_id"],
                "accountable_agent": "vp-content",
                "business_objective": "produce content",
                "expected_outcome": "content artifact",
                "deliverable": "content artifact",
                "success_criteria": ["evidence supplied"],
                "priority": "P1",
                "authority_level": 2,
                "acceptance_test": "content evidence is present",
                "approval_gates": [],
            },
            "parent_authority": 2,
            "depth": 2,
            "ancestry": ["cos", "cmo"],
            "parent_approval_gates": [],
        },
        "D-CMO-create-vp",
    )

    for index, target in enumerate(("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "QA"), start=1):
        nested = execute_owner(
            runtime,
            "cos",
            "D-CMO",
            cmo_task["task_id"],
            "delegation.execute_owner",
            {
                "delegation_id": "D-VP",
                "task_id": vp["task_id"],
                "tool_name": "task.transition",
                "arguments": {"task_id": vp["task_id"], "target": target},
                "idempotency_key": f"D-VP-transition-{index}",
            },
            f"D-CMO-route-vp-{index}",
        )
        assert nested["result"]["executing_principal"] == "vp-content"

    with pytest.raises(PermissionError):
        runtime.call_agent(
            "vp-content",
            "delegation.create",
            {
                "delegation": {
                    "delegation_id": "D-ILLEGAL",
                    "task_id": "illegal",
                    "accountable_agent": "message-ops",
                    "business_objective": "illegal",
                    "expected_outcome": "illegal",
                    "deliverable": "illegal",
                    "success_criteria": ["illegal"],
                    "priority": "P1",
                    "authority_level": 1,
                    "acceptance_test": "illegal",
                },
                "parent_authority": 2,
                "depth": 3,
            },
        )
