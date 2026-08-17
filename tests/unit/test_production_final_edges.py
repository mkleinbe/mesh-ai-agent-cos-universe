from __future__ import annotations

import pytest

from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def base_decision(**overrides):
    payload = {
        "decision_type": "OPERATING_JUDGMENT",
        "decision_title": "Decision",
        "task_id": "T1",
        "correlation_id": "corr-1",
        "decision_owner": "michael",
        "authority_level": 5,
        "human_approval_required": True,
        "approval_reference": "approval://1",
        "human_approver": "michael",
        "decision": "Proceed",
        "disposition": "APPROVED",
        "decision_basis_summary": "Supported by evidence.",
        "evidence_references": ["evidence://1"],
        "source_systems": ["source"],
        "alternatives_considered": ["stop"],
        "selection_criteria": ["value"],
        "confidence": "HIGH",
        "risk_level": "LOW",
        "affected_entities": ["firm"],
        "reversibility": "REVERSIBLE",
        "reversal_condition": "new evidence",
        "policy_rule_ids": ["test"],
        "model_provider": None,
        "model_id_version": None,
        "prompt_template_version": None,
        "data_classification": "INTERNAL",
        "outcome_validation": "pending",
        "outcome_status": "PENDING",
        "retention_class": "GOVERNANCE_LONG_TERM",
    }
    payload.update(overrides)
    return payload


def test_l5_decision_requires_michael_as_owner_even_with_michael_approval() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="decision owner"):
        runtime.call_agent(
            "cro",
            "governance.record_decision",
            base_decision(decision_owner="qualified-human"),
        )


def test_l4_decision_requires_actual_approval_reference_and_approver() -> None:
    runtime = MCPRuntime(TaskLedger())
    with pytest.raises(PermissionError, match="approval reference"):
        runtime.call_agent(
            "cro",
            "governance.record_decision",
            base_decision(
                authority_level=4,
                decision_owner="qualified-human",
                approval_reference=None,
                human_approver=None,
            ),
        )


def test_human_only_handler_is_fail_closed_when_called_directly() -> None:
    with pytest.raises(PermissionError, match="authenticated human"):
        MCPRuntime(TaskLedger())._human_only("cos", {})


def test_governance_duplicate_idempotency_key_with_different_event_id_fails_closed() -> None:
    ledger = TaskLedger()
    journal = GovernanceJournal(ledger)
    common = {
        "event_type": "test.event",
        "event_category": "TEST",
        "action": "TEST",
        "actor_type": "SERVICE",
        "actor_id": "test",
        "actor_role": "test",
        "task_id": None,
        "correlation_id": "corr",
        "authority_level": 0,
        "policy_rule_ids": ["test"],
        "capability_tool": "test",
        "target_resource": "test",
        "source_system": "test",
        "input_summary": "test",
        "result_status": "SUCCESS",
        "output_summary": "test",
        "evidence_references": [],
        "risk_severity": "LOW",
        "data_classification": "INTERNAL",
        "model_provider": None,
        "model_id_version": None,
        "skill_agent_version": "1.0.0",
        "environment": "TEST",
        "retention_class": "GOVERNANCE_LONG_TERM",
        "idempotency_key": "same-key",
    }
    journal.record_event(event_id="event-1", **common)
    with pytest.raises(ValueError, match="Duplicate governance"):
        journal.record_event(event_id="event-2", **common)
