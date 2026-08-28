from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def make_task(runtime: MCPRuntime, owner: str, *, authority_level: int, key: str) -> dict:
    return runtime.call_agent(
        "cos",
        "task.intake",
        {
            "objective": f"{owner} governed authority test",
            "expected_outcome": "canonical evidence-backed decision",
            "requested_by": "michael",
            "executive_sponsor": "michael",
            "accountable_agent": owner,
            "decision_owner": "michael",
            "authority_level": authority_level,
            "acceptance_test": "canonical approval evidence is enforced",
            "idempotency_key": key,
        },
    )


def approve(
    runtime: MCPRuntime,
    task: dict,
    *,
    requester: str,
    owner: str,
    authority_level: int,
    action: str,
) -> dict:
    approval = runtime.call_agent(
        requester,
        "approval.request",
        {
            "task_id": task["task_id"],
            "approval_owner": owner,
            "authority_level": authority_level,
            "action": action,
        },
    )
    runtime.call_human(
        owner,
        "approval.record_decision",
        {
            "approval_id": approval["approval_id"],
            "approved": True,
            "reason": "synthetic authority test approval",
        },
    )
    return runtime.call_agent("cos", "approval.get", {"approval_id": approval["approval_id"]})


def decision_payload(task: dict, **overrides):
    payload = {
        "decision_type": "OPERATING_JUDGMENT",
        "decision_title": "Commercial recommendation",
        "task_id": task["task_id"],
        "correlation_id": task["correlation_id"],
        "agent_id": "spoof",
        "agent_role": "spoof",
        "decision_owner": "cro",
        "authority_level": 2,
        "human_approval_required": False,
        "decision": "Proceed",
        "disposition": "RECOMMENDED",
        "decision_basis_summary": "Approved evidence supports the recommendation.",
        "evidence_references": ["evidence://1"],
        "source_systems": ["approved-source"],
        "alternatives_considered": ["do not proceed"],
        "selection_criteria": ["fit"],
        "confidence": "HIGH",
        "risk_level": "LOW",
        "affected_entities": ["opportunity"],
        "reversibility": "REVERSIBLE",
        "reversal_condition": "new evidence",
        "policy_rule_ids": ["test"],
        "model_provider": None,
        "model_id_version": None,
        "prompt_template_version": None,
        "skill_agent_version": "spoof",
        "data_classification": "INTERNAL",
        "outcome_validation": "pending",
        "outcome_status": "PENDING",
        "retention_class": "GOVERNANCE_LONG_TERM",
    }
    payload.update(overrides)
    return payload


def event_payload(task: dict, **overrides):
    payload = {
        "event_type": "commercial.reviewed",
        "event_category": "EXECUTION",
        "action": "REVIEW",
        "actor_type": "HUMAN",
        "actor_id": "spoof",
        "actor_role": "spoof",
        "task_id": task["task_id"],
        "correlation_id": task["correlation_id"],
        "authority_level": 2,
        "policy_rule_ids": ["test"],
        "capability_tool": "review",
        "target_resource": "opportunity",
        "source_system": "approved-source",
        "input_summary": "review",
        "result_status": "SUCCESS",
        "output_summary": "reviewed",
        "evidence_references": [],
        "risk_severity": "LOW",
        "data_classification": "INTERNAL",
        "model_provider": None,
        "model_id_version": None,
        "skill_agent_version": "spoof",
        "environment": "TEST",
        "retention_class": "GOVERNANCE_LONG_TERM",
    }
    payload.update(overrides)
    return payload


def test_agent_cannot_record_unapproved_decision_above_registry_authority() -> None:
    runtime = MCPRuntime(TaskLedger())
    task = make_task(runtime, "consultant-network-steward", authority_level=3, key="steward-l3")
    with pytest.raises(PermissionError, match="authority"):
        runtime.call_agent(
            "consultant-network-steward",
            "governance.record_decision",
            decision_payload(
                task,
                authority_level=3,
                decision_owner="consultant-network-steward",
            ),
        )


def test_l4_and_l5_decisions_fail_closed_and_l5_requires_michael() -> None:
    runtime = MCPRuntime(TaskLedger())
    task_l4 = make_task(runtime, "cro", authority_level=4, key="cro-l4")
    with pytest.raises(PermissionError, match="L4/L5"):
        runtime.call_agent(
            "cro",
            "governance.record_decision",
            decision_payload(task_l4, authority_level=4),
        )

    approved_l4_record = approve(
        runtime,
        task_l4,
        requester="cro",
        owner="qualified-human",
        authority_level=4,
        action="OPERATING_JUDGMENT",
    )
    approved_l4 = runtime.call_agent(
        "cro",
        "governance.record_decision",
        decision_payload(
            task_l4,
            authority_level=4,
            human_approval_required=True,
            approval_reference=approved_l4_record["approval_id"],
            human_approver="qualified-human",
            decision_owner="qualified-human",
        ),
    )
    assert approved_l4["authority_level"] == 4
    assert approved_l4["approval_reference"] == approved_l4_record["approval_id"]

    task_l5 = make_task(runtime, "cro", authority_level=5, key="cro-l5")
    with pytest.raises(PermissionError, match="Michael"):
        runtime.call_agent(
            "cro",
            "governance.record_decision",
            decision_payload(
                task_l5,
                authority_level=5,
                human_approval_required=True,
                approval_reference="approval-does-not-matter",
                human_approver="qualified-human",
                decision_owner="qualified-human",
            ),
        )

    approved_l5_record = approve(
        runtime,
        task_l5,
        requester="cro",
        owner="Michael",
        authority_level=5,
        action="OPERATING_JUDGMENT",
    )
    approved_l5 = runtime.call_agent(
        "cro",
        "governance.record_decision",
        decision_payload(
            task_l5,
            authority_level=5,
            human_approval_required=True,
            approval_reference=approved_l5_record["approval_id"],
            human_approver="Michael",
            decision_owner="michael",
        ),
    )
    assert approved_l5["human_approver"] == "Michael"


def test_agent_event_cannot_claim_authority_above_role_without_approval() -> None:
    runtime = MCPRuntime(TaskLedger())
    task_l3 = make_task(
        runtime,
        "consultant-network-steward",
        authority_level=3,
        key="steward-event-l3",
    )
    with pytest.raises(PermissionError, match="authority"):
        runtime.call_agent(
            "consultant-network-steward",
            "governance.record_event",
            event_payload(task_l3, authority_level=3),
        )

    task_l4 = make_task(
        runtime,
        "consultant-network-steward",
        authority_level=4,
        key="steward-event-l4",
    )
    approved_record = approve(
        runtime,
        task_l4,
        requester="cos",
        owner="qualified-human",
        authority_level=4,
        action="REVIEW",
    )
    approved = runtime.call_agent(
        "consultant-network-steward",
        "governance.record_event",
        event_payload(
            task_l4,
            authority_level=4,
            approval_reference=approved_record["approval_id"],
            human_approver="qualified-human",
        ),
    )
    assert approved["authority_level"] == 4
    assert approved["approval_reference"] == approved_record["approval_id"]

    task_l5 = make_task(
        runtime,
        "consultant-network-steward",
        authority_level=5,
        key="steward-event-l5",
    )
    with pytest.raises(PermissionError, match="owned by Michael"):
        runtime.call_agent(
            "cos",
            "approval.request",
            {
                "task_id": task_l5["task_id"],
                "approval_owner": "qualified-human",
                "authority_level": 5,
                "action": "REVIEW",
            },
        )
