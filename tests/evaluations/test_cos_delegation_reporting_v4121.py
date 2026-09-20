from __future__ import annotations

import json

import pytest

from mesh_cos import mcp_stdio_bridge as bridge
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.mcp_validation import load_input_schemas
from mesh_cos.models import TaskStatus


def _parent(runtime: MCPRuntime) -> dict:
    return runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": "Internal delegation/reporting canary",
            "expected_outcome": "CRO-owned work returns governed result to CoS",
            "requested_by": "cos",
            "executive_sponsor": "Michael D. Kleinberg",
            "accountable_agent": "cos",
            "decision_owner": "cos",
            "authority_level": 2,
            "acceptance_test": "Owner attribution, result return, separate verification, no external action",
        },
    )


def _child(runtime: MCPRuntime, parent: dict) -> dict:
    return runtime.call_agent(
        "cos",
        "task.decompose",
        {
            "parent_task_id": parent["task_id"],
            "work_packages": [
                {
                    "objective": "Run internal CRO lifecycle",
                    "expected_outcome": "Internal CRO result",
                    "accountable_agent": "cro",
                    "decision_owner": "cro",
                    "authority_level": 2,
                    "acceptance_test": "CRO executes and returns evidence without external action",
                }
            ],
        },
    )[0]


def _delegation(child: dict) -> dict:
    return {
        "delegation_id": "D-CDR-001",
        "task_id": child["task_id"],
        "parent_task_id": child["parent_task_id"],
        "accountable_agent": "cro",
        "business_objective": child["objective"],
        "expected_outcome": child["expected_outcome"],
        "deliverable": "Internal canary result",
        "success_criteria": ["CRO attribution", "No external action"],
        "priority": "P1",
        "authority_level": 2,
        "acceptance_test": child["acceptance_test"],
        "constraints": ["internal only"],
        "prohibited_actions": ["unilateral_external_send", "contractual_commitment"],
    }


def _execute(runtime: MCPRuntime, task_id: str, tool_name: str, arguments: dict, key: str) -> dict:
    return runtime.call_agent(
        "cos",
        "delegation.execute_owner",
        {
            "protocol_version": "mesh.cos.owner-execution.v2",
            "delegation_id": "D-CDR-001",
            "task_id": task_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "approval_references": [],
            "idempotency_key": key,
        },
    )


def test_delegation_public_contract_treats_server_derived_assertions_as_optional() -> None:
    schema = load_input_schemas()["delegation.create"]
    assert "parent_authority" not in schema["required"]
    assert "depth" not in schema["required"]
    for name in ("parent_authority", "depth", "active_owner", "ancestry"):
        assert name in schema["properties"]


@pytest.mark.parametrize(
    ("exc", "reason"),
    [
        (PermissionError("Delegation target must be a registered direct child of the delegating agent"), "recipient-not-delegable"),
        (PermissionError("Delegation owner must match the canonical child task owner"), "ownership-conflict"),
        (PermissionError("Caller-supplied delegation depth does not match canonical registry"), "invalid-delegation-contract"),
        (PermissionError("Caller-supplied parent authority does not match canonical parent task"), "invalid-delegation-contract"),
        (PermissionError("Delegation cannot widen authority"), "authority-exceeded"),
        (PermissionError("approval required"), "approval-required"),
    ],
)
def test_delegation_errors_return_stable_safe_reason_codes(exc: BaseException, reason: str) -> None:
    payload = bridge._safe_error(exc)
    assert payload["reason_code"] == reason
    assert "canonical child task owner" not in json.dumps(payload)


def test_agent_principal_is_not_a_skill_capability() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(ValueError, match="agent principal") as caught:
        runtime.call_agent(
            "cos",
            "skills.invoke_governed",
            {"capability": "mesh-cro", "payload": {}},
        )
    payload = bridge._safe_error(caught.value)
    assert payload["error"] == "invalid_request"
    assert payload["reason_code"] == "unsupported-capability-type"


def test_complete_cos_cro_cos_round_trip_preserves_identity_and_verification_separation() -> None:
    runtime = MCPRuntime(TaskLedger())
    parent = _parent(runtime)
    child = _child(runtime, parent)

    delegated = runtime.call_agent(
        "cos",
        "delegation.create",
        {"delegation": _delegation(child)},
    )
    assert delegated["accountable_agent"] == "cro"

    for target, key in (
        ("TRIAGED", "triage"),
        ("PLANNED", "plan"),
        ("ASSIGNED", "assign"),
        ("IN_PROGRESS", "start"),
    ):
        result = _execute(
            runtime,
            child["task_id"],
            "task.transition",
            {"task_id": child["task_id"], "target": target},
            key,
        )
        assert result["executing_principal"] == "cro"
        assert result["orchestrating_agent"] == "cos"

    checkin = _execute(
        runtime,
        child["task_id"],
        "task.check_in",
        {
            "task_id": child["task_id"],
            "note": "Internal canary in progress; no external action.",
            "evidence": ["synthetic://delegation", "synthetic://no-external-action"],
        },
        "checkin",
    )
    assert checkin["result"]["agent_id"] == "cro"

    decision = _execute(
        runtime,
        child["task_id"],
        "governance.record_decision",
        {
            "decision_type": "COMMERCIAL_RECOMMENDATION",
            "decision_title": "Internal canary recommendation",
            "task_id": child["task_id"],
            "correlation_id": "corr-cdr-roundtrip",
            "agent_id": "cos",
            "agent_role": "Chief of Staff",
            "decision_owner": "cro",
            "authority_level": 2,
            "human_approval_required": False,
            "decision": "Continue internal evidence review; do not take external action.",
            "disposition": "RECOMMENDED",
            "decision_basis_summary": "Synthetic internal canary evidence supports bounded internal continuation only.",
            "evidence_references": ["synthetic://delegation", "synthetic://checkin"],
            "source_systems": ["TaskLedger"],
            "alternatives_considered": ["continue internal review", "stop canary"],
            "selection_criteria": ["owner attribution", "no external action"],
            "confidence": 1.0,
            "risk_level": "LOW",
            "affected_entities": [child["task_id"]],
            "reversibility": "REVERSIBLE",
            "reversal_condition": "Any authority or approval mismatch",
            "policy_rule_ids": ["bounded-delegation", "no-impersonation"],
            "model_provider": None,
            "model_id_version": None,
            "prompt_template_version": None,
            "skill_agent_version": "synthetic",
            "data_classification": "INTERNAL",
            "outcome_validation": "Decision remains within L2 and causes no external action",
            "outcome_status": "PENDING",
            "retention_class": "GOVERNANCE_LONG_TERM",
        },
        "decision",
    )
    assert decision["result"]["agent_id"] == "cro"
    assert decision["result"]["decision_owner"] == "cro"
    assert decision["result"]["authority_level"] == 2

    _execute(
        runtime,
        child["task_id"],
        "task.transition",
        {"task_id": child["task_id"], "target": "QA"},
        "qa",
    )
    completed = _execute(
        runtime,
        child["task_id"],
        "task.complete",
        {
            "task_id": child["task_id"],
            "outcome": "Internal owner round trip completed",
            "evidence": ["synthetic://delegation", "synthetic://checkin", "synthetic://owner-cro"],
        },
        "complete",
    )
    assert completed["accountable_owner"] == "cro"
    assert completed["result"]["status"] == TaskStatus.COMPLETED.value
    assert completed["result"]["verified_at"] is None

    reconciliation = runtime.call_agent(
        "cos",
        "task.check_in",
        {
            "task_id": parent["task_id"],
            "note": f"Reconciled child {child['task_id']} completion from CRO owner execution.",
            "evidence": [f"task:{child['task_id']}", "synthetic://owner-cro"],
        },
    )
    assert reconciliation["agent_id"] == "cos"
    observed_parent = runtime.call_agent("cos", "task.get", {"task_id": parent["task_id"]})
    assert observed_parent["status"] == TaskStatus.INTAKE.value

    verified = runtime.call_agent(
        "cos",
        "task.verify",
        {
            "task_id": child["task_id"],
            "passed": True,
            "reason": "Independent acceptance evidence passed",
            "evidence_references": ["synthetic://verification"],
        },
    )
    assert verified["status"] == TaskStatus.VERIFIED.value
    audit = runtime.call_agent("cos", "governance.verify_audit_chain", {})
    assert audit["valid"] is True
