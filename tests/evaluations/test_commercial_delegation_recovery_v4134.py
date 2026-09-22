from __future__ import annotations

import pytest

from mesh_cos import mcp_stdio_bridge as bridge
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def _commercial_pair(runtime: MCPRuntime) -> tuple[dict, dict]:
    parent = runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "Evaluate one internal commercial event",
            "expected_outcome": "Canonical commercial qualification with no external action",
            "requested_by": "commercial-regression",
            "executive_sponsor": "Michael D. Kleinberg",
            "accountable_agent": "cos",
            "decision_owner": "Michael D. Kleinberg",
            "authority_level": 2,
            "acceptance_test": "CRO route is canonical and external action remains prohibited",
        },
    )
    child = runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": "Qualify the bounded commercial event",
                    "expected_outcome": "Revenue Intelligence and GTM handoffs are authorized for CRO",
                    "accountable_agent": "cro",
                    "decision_owner": "Michael D. Kleinberg",
                    "authority_level": 2,
                    "acceptance_test": "CRO executes through server-derived owner routing",
                }
            ],
        },
    )[0]
    return parent, child


def _delegation(parent: dict, child: dict) -> dict:
    return {
        "delegation_id": "D-COM-DEL-REGRESSION",
        "task_id": child["task_id"],
        "parent_task_id": parent["task_id"],
        "accountable_agent": "cro",
        "business_objective": child["objective"],
        "expected_outcome": child["expected_outcome"],
        "deliverable": "Internal commercial qualification only",
        "success_criteria": ["CRO owner attribution", "No external action"],
        "priority": "P1",
        "authority_level": 2,
        "acceptance_test": child["acceptance_test"],
        "constraints": ["internal only"],
        "permitted_capabilities": ["mesh-revenue-intelligence", "mesh-gtm-orchestrator"],
        "prohibited_actions": ["contractual_commitment", "unilateral_external_send"],
    }


def test_commercial_delegation_rejects_active_owner_cos_then_recovers_canonically() -> None:
    runtime = MCPRuntime(TaskLedger())
    parent, child = _commercial_pair(runtime)
    delegation = _delegation(parent, child)

    with pytest.raises(PermissionError, match="active owner") as caught:
        runtime.call_agent(
            "cos",
            "delegation.create",
            {"delegation": delegation, "active_owner": "cos"},
        )

    safe = bridge._safe_error(caught.value)
    assert safe["reason_code"] == "ownership-conflict"
    assert runtime.ledger.get_record("delegation", delegation["delegation_id"]) is None
    assert runtime.ledger.get_task(child["task_id"]).accountable_agent == "cro"

    created = runtime.call_agent(
        "cos",
        "delegation.create",
        {"delegation": delegation},
    )

    assert created["accountable_agent"] == "cro"
    assert created["delegating_agent"] == "cos"
    assert created["task_id"] == child["task_id"]
    assert created["parent_task_id"] == parent["task_id"]
    assert created["permitted_capabilities"] == [
        "mesh-gtm-orchestrator",
        "mesh-revenue-intelligence",
    ]


def test_commercial_cro_handoffs_execute_as_cro_and_require_provenance() -> None:
    runtime = MCPRuntime(TaskLedger())
    parent, child = _commercial_pair(runtime)
    delegation = _delegation(parent, child)
    runtime.call_agent("cos", "delegation.create", {"delegation": delegation})

    for capability in ("mesh-revenue-intelligence", "mesh-gtm-orchestrator"):
        result = runtime.call_agent(
            "cos",
            "delegation.execute_owner",
            {
                "protocol_version": "mesh.cos.owner-execution.v2",
                "delegation_id": delegation["delegation_id"],
                "task_id": child["task_id"],
                "tool_name": "skills.invoke_governed",
                "arguments": {
                    "capability": capability,
                    "payload": {
                        "task_id": child["task_id"],
                        "correlation_id": "corr-commercial-regression",
                    },
                },
                "approval_references": [],
                "idempotency_key": f"commercial-regression-{capability}",
            },
        )

        assert result["executing_principal"] == "cro"
        assert result["orchestrating_agent"] == "cos"
        assert result["result"]["status"] == "AUTHORIZED"
        assert result["result"]["execution_mode"] == "CHATGPT_SKILL_HANDOFF"
        assert result["result"]["result_provenance_required"] is True


def test_commercial_operating_reference_requires_server_derived_owner_assertions() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    reference = (
        root
        / "chatgpt"
        / "skills"
        / "mesh-chief-of-staff"
        / "references"
        / "commercial-growth-operating-cadence.md"
    ).read_text()

    for marker in (
        "parent_authority",
        "depth",
        "ancestry",
        "active_owner",
        "delegation.execute_owner",
        "ownership-conflict",
        "BLOCKED -> IN_PROGRESS",
    ):
        assert marker in reference
    assert "never send `active_owner=cos` for a CRO-owned child" in reference
