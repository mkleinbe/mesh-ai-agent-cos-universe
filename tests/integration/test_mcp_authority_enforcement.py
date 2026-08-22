from __future__ import annotations

import pytest

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def decision_payload(**overrides):
    payload = {
        "decision_type": "OPERATING_JUDGMENT",
        "decision_title": "Commercial recommendation",
        "task_id": "T1",
        "correlation_id": "corr-1",
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


def event_payload(**overrides):
    payload = {
        "event_type": "commercial.reviewed",
        "event_category": "EXECUTION",
        "action": "REVIEW",
        "actor_type": "HUMAN",
        "actor_id": "spoof",
        "actor_role": "spoof",
        "task_id": None,
        "correlation_id": "corr-1",
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
    with pytest.raises(PermissionError, match="authority"):
        runtime.call_agent(
            "consultant-network-steward",
            "governance.record_decision",
            decision_payload(authority_level=3, decision_owner="consultant-network-steward"),
        )


def test_l4_and_l5_decisions_fail_closed_and_l5_requires_michael() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="L4/L5"):
        runtime.call_agent("cro", "governance.record_decision", decision_payload(authority_level=4))

    approved_l4 = runtime.call_agent(
        "cro",
        "governance.record_decision",
        decision_payload(
            authority_level=4,
            human_approval_required=True,
            approval_reference="approval://A1",
            human_approver="qualified-human",
            decision_owner="qualified-human",
        ),
    )
    assert approved_l4["authority_level"] == 4

    with pytest.raises(PermissionError, match="Michael"):
        runtime.call_agent(
            "cro",
            "governance.record_decision",
            decision_payload(
                authority_level=5,
                human_approval_required=True,
                approval_reference="approval://A2",
                human_approver="qualified-human",
                decision_owner="qualified-human",
            ),
        )

    approved_l5 = runtime.call_agent(
        "cro",
        "governance.record_decision",
        decision_payload(
            authority_level=5,
            human_approval_required=True,
            approval_reference="approval://A3",
            human_approver="michael",
            decision_owner="michael",
        ),
    )
    assert approved_l5["human_approver"] == "michael"


def test_agent_event_cannot_claim_authority_above_role_without_approval() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="authority"):
        runtime.call_agent("consultant-network-steward", "governance.record_event", event_payload(authority_level=3))

    approved = runtime.call_agent(
        "consultant-network-steward",
        "governance.record_event",
        event_payload(
            authority_level=4,
            approval_reference="approval://A1",
            human_approver="qualified-human",
        ),
    )
    assert approved["authority_level"] == 4

    with pytest.raises(PermissionError, match="Michael"):
        runtime.call_agent(
            "consultant-network-steward",
            "governance.record_event",
            event_payload(
                authority_level=5,
                approval_reference="approval://A2",
                human_approver="qualified-human",
            ),
        )
