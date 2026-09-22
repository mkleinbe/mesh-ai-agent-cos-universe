from __future__ import annotations

import pytest

from mesh_cos import mcp_stdio_bridge as bridge
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.models import TaskStatus


def _parent(runtime: MCPRuntime) -> dict:
    parent = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "Scheduled Marketing Authority routing canary",
            "expected_outcome": "AgentOps-owned child executes without duplicate work",
            "requested_by": "LOOP-MKT-001",
            "executive_sponsor": "Michael D. Kleinberg",
            "accountable_agent": "cos",
            "decision_owner": "cos",
            "authority_level": 2,
            "acceptance_test": "Canonical work graph is reused and no external action occurs",
        },
    )
    for target in ("TRIAGED", "PLANNED", "ASSIGNED", "IN_PROGRESS", "BLOCKED"):
        runtime.call_agent(
            "cos",
            "task.transition",
            {"task_id": parent["task_id"], "target": target},
        )
    return runtime.call_agent("cos", "task.get", {"task_id": parent["task_id"]})


def _child(runtime: MCPRuntime, parent: dict, owner: str = "agentops") -> dict:
    return runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": "Evaluate bounded scheduler health",
                    "expected_outcome": "Internal health evidence",
                    "accountable_agent": owner,
                    "decision_owner": owner,
                    "priority": "P1",
                    "authority_level": 2,
                    "acceptance_test": "Owner executes through canonical delegated transport with no provider side effect",
                }
            ],
        },
    )[0]


def _delegation(child: dict, owner: str = "agentops") -> dict:
    return {
        "delegation_id": "D-MKT-RECOVERY-001",
        "task_id": child["task_id"],
        "parent_task_id": child["parent_task_id"],
        "accountable_agent": owner,
        "business_objective": child["objective"],
        "expected_outcome": child["expected_outcome"],
        "deliverable": "Internal scheduler-health result",
        "success_criteria": ["Canonical owner attribution", "No duplicate work", "No provider side effect"],
        "priority": "P1",
        "authority_level": 2,
        "acceptance_test": child["acceptance_test"],
        "constraints": ["internal only"],
    }


def test_cdr_012_scheduled_recovery_strips_only_compatibility_assertions_and_reuses_work_graph() -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    parent = _parent(runtime)
    child = _child(runtime, parent)
    delegation = _delegation(child)

    with pytest.raises(PermissionError, match="active owner") as caught:
        runtime.call_agent(
            "cos",
            "delegation.create",
            {"delegation": delegation, "active_owner": "cos"},
        )

    safe = bridge._safe_error(caught.value)
    assert safe["reason_code"] == "ownership-conflict"
    assert ledger.get_record("delegation", delegation["delegation_id"]) is None
    assert ledger.get_task(parent["task_id"]).status == TaskStatus.BLOCKED
    assert ledger.get_task(child["task_id"]).status == TaskStatus.INTAKE

    created = runtime.call_agent(
        "cos",
        "delegation.create",
        {"delegation": delegation},
    )
    assert created["accountable_agent"] == "agentops"

    resumed = runtime.call_agent(
        "cos",
        "task.transition",
        {"task_id": parent["task_id"], "target": "IN_PROGRESS"},
    )
    assert resumed["status"] == TaskStatus.IN_PROGRESS

    owner_result = runtime.call_agent(
        "cos",
        "delegation.execute_owner",
        {
            "protocol_version": "mesh.cos.owner-execution.v2",
            "delegation_id": delegation["delegation_id"],
            "task_id": child["task_id"],
            "tool_name": "task.transition",
            "arguments": {"task_id": child["task_id"], "target": "TRIAGED"},
            "idempotency_key": "mkt-recovery-triage",
        },
    )
    assert owner_result["executing_principal"] == "agentops"
    assert owner_result["orchestrating_agent"] == "cos"
    assert ledger.get_task(child["task_id"]).status == TaskStatus.TRIAGED

    repeated = runtime.call_agent(
        "cos",
        "delegation.create",
        {"delegation": delegation},
    )
    assert repeated["delegation_id"] == delegation["delegation_id"]

    children = [task for task in ledger.list_tasks() if task.parent_task_id == parent["task_id"]]
    assert len(children) == 1
    assert children[0].task_id == child["task_id"]


def test_cdr_013_canonical_owner_mismatch_is_not_auto_repaired() -> None:
    ledger = TaskLedger()
    runtime = MCPRuntime(ledger)
    parent = _parent(runtime)
    child = _child(runtime, parent, owner="agentops")
    mismatched = _delegation(child, owner="cmo")
    mismatched["delegation_id"] = "D-MKT-OWNER-MISMATCH-001"

    with pytest.raises(PermissionError, match="canonical child task owner") as caught:
        runtime.call_agent(
            "cos",
            "delegation.create",
            {"delegation": mismatched},
        )

    safe = bridge._safe_error(caught.value)
    assert safe["reason_code"] == "ownership-conflict"
    assert ledger.get_record("delegation", mismatched["delegation_id"]) is None
    assert ledger.get_task(child["task_id"]).accountable_agent == "agentops"
