from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from mesh_cos.governance import GovernanceJournal, GovernanceMirror, verify_audit_chain
from mesh_cos.ledger import TaskLedger
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]


class CaptureMirror(GovernanceMirror):
    def __init__(self) -> None:
        self.decisions: list[dict] = []
        self.events: list[dict] = []

    def mirror_decision(self, record: dict) -> None:
        self.decisions.append(record)

    def mirror_event(self, record: dict) -> None:
        self.events.append(record)


def decision_payload() -> dict:
    return {
        "decision_type": "OPERATING_JUDGMENT",
        "decision_title": "Select governed routing option",
        "task_id": "T-gov",
        "correlation_id": "corr-gov",
        "agent_id": "cos",
        "agent_role": "AI Chief of Staff / Agent Workforce Manager",
        "decision_owner": "Michael / CEO",
        "authority_level": 3,
        "human_approval_required": False,
        "decision": "Route work to CRO",
        "disposition": "APPROVED",
        "decision_basis_summary": "CRO owns commercial interpretation and the evidence is within its authoritative scope.",
        "evidence_references": ["registry:cro", "task:T-gov"],
        "source_systems": ["TaskLedger", "Agent Registry"],
        "alternatives_considered": ["CFO", "COO", "CRO"],
        "selection_criteria": ["functional truth owner", "delegated authority", "source permission"],
        "confidence": 0.95,
        "risk_level": "LOW",
        "affected_entities": ["cro"],
        "reversibility": "REVERSIBLE",
        "reversal_condition": "New evidence changes functional ownership or authority.",
        "policy_rule_ids": ["mesh-l3", "functional-truth-boundary"],
        "model_provider": "OpenAI",
        "model_id_version": "test-model",
        "prompt_template_version": "test-template-v1",
        "skill_agent_version": "cos-test-v1",
        "data_classification": "INTERNAL",
        "outcome_validation": "Assigned owner acknowledges and produces evidence.",
        "outcome_status": "IN_PROGRESS",
        "retention_class": "GOVERNANCE_LONG_TERM",
    }


def test_v2_contracts_are_closed_and_reject_private_reasoning_fields():
    for name in ("decision.v2.schema.json", "agent-event.v2.schema.json"):
        schema = json.loads((ROOT / "contracts" / name).read_text())
        assert schema["additionalProperties"] is False
    journal = GovernanceJournal(TaskLedger())
    record = journal.record_decision(**decision_payload())
    schema = json.loads((ROOT / "contracts" / "decision.v2.schema.json").read_text())
    Draft202012Validator(schema).validate(record)
    bad = dict(record)
    bad["chain_of_thought"] = "must never be persisted"
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(bad)


def test_governance_journal_persists_decision_and_tamper_evident_audit_chain():
    ledger = TaskLedger()
    mirror = CaptureMirror()
    journal = GovernanceJournal(ledger, mirror=mirror)
    decision = journal.record_decision(**decision_payload())
    event1 = journal.record_event(
        event_type="decision.recorded",
        event_category="GOVERNANCE",
        action="RECORD",
        actor_type="AGENT",
        actor_id="cos",
        actor_role="AI Chief of Staff / Agent Workforce Manager",
        task_id="T-gov",
        correlation_id="corr-gov",
        decision_id=decision["decision_id"],
        authority_level=3,
        policy_rule_ids=["mesh-l3"],
        capability_tool="governance-journal",
        target_resource=decision["decision_id"],
        source_system="TaskLedger",
        input_summary="Material operating decision.",
        result_status="SUCCESS",
        output_summary="Explainable decision record persisted.",
        evidence_references=["task:T-gov"],
        risk_severity="LOW",
        data_classification="INTERNAL",
        model_provider="OpenAI",
        model_id_version="test-model",
        skill_agent_version="cos-test-v1",
        environment="TEST",
        retention_class="GOVERNANCE_LONG_TERM",
    )
    event2 = journal.record_event(
        event_type="task.routed",
        event_category="EXECUTION",
        action="ROUTE",
        actor_type="AGENT",
        actor_id="cos",
        actor_role="AI Chief of Staff / Agent Workforce Manager",
        task_id="T-gov",
        correlation_id="corr-gov",
        decision_id=decision["decision_id"],
        authority_level=3,
        policy_rule_ids=["functional-truth-boundary"],
        capability_tool="task-ledger",
        target_resource="cro",
        source_system="TaskLedger",
        input_summary="Decision approved routing to CRO.",
        result_status="SUCCESS",
        output_summary="CRO assigned.",
        evidence_references=[decision["canonical_record_ref"]],
        risk_severity="LOW",
        data_classification="INTERNAL",
        model_provider="OpenAI",
        model_id_version="test-model",
        skill_agent_version="cos-test-v1",
        environment="TEST",
        retention_class="GOVERNANCE_LONG_TERM",
    )
    assert ledger.get_record("decision_v2", decision["decision_id"]) == decision
    assert ledger.get_record("audit_event_v2", event2["event_id"]) == event2
    assert event1["previous_event_hash"] == "GENESIS"
    assert event2["previous_event_hash"] == event1["event_hash"]
    assert verify_audit_chain(ledger.list_records("audit_event_v2"))
    tampered = [dict(x) for x in ledger.list_records("audit_event_v2")]
    tampered[0]["output_summary"] = "changed"
    assert not verify_audit_chain(tampered)
    assert mirror.decisions[0]["decision_id"] == decision["decision_id"]
    assert mirror.events[-1]["event_id"] == event2["event_id"]


def test_all_registered_agents_require_governance_journal_and_v2_outputs():
    registry = load_registry(ROOT / "agents" / "registry.json")
    assert len(registry) >= 11
    for agent_id, record in registry.items():
        assert "governance-journal" in record["tools"], agent_id
        assert "agent-event.v2" in record["output_contracts"], agent_id
        assert record["governance_policy"]["audit_logging"] == "REQUIRED", agent_id
        assert record["governance_policy"]["decision_logging"] == "REQUIRED_WHEN_DECIDING_OR_RECOMMENDING", agent_id


def test_sheet_mirror_config_is_non_secret_and_matches_initialized_registers():
    config = json.loads((ROOT / "config" / "governance-logs.v1.json").read_text())
    assert config["audit_log"]["spreadsheet_id"] == "1T8vKx4gaUJdeG8kSc18MsBbXpY4EbDF3exZ0RGpvND0"
    assert config["decision_log"]["spreadsheet_id"] == "1IJcwPuulqsNAa1lCW2MsmNgH6Vm5INPqTlcH4NR0xpw"
    serialized = json.dumps(config).lower()
    assert "credential" not in serialized
    assert "token" not in serialized
    assert config["canonical_state"] == "TaskLedger"
    assert config["mirror_mode"] == "HUMAN_READABLE_OPERATIONAL_MIRROR"
