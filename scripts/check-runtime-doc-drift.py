#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from mesh_cos.audit import AuditEvent
from mesh_cos.contracts import agent_record_contract, validate_runtime_contract
from mesh_cos.governance import GovernanceJournal, verify_audit_chain
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, Delegation, TaskRecord
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


for schema_path in sorted(CONTRACTS.glob("*.schema.json")):
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    require(schema.get("additionalProperties") is False, f"{schema_path.name}: contracts must be closed")
    require("version" in schema.get("required", []), f"{schema_path.name}: version must be required")

registry = load_registry(ROOT / "agents" / "registry.json")
for agent_id, record in registry.items():
    validate_runtime_contract("agent-record", agent_record_contract(record), CONTRACTS)
    require("governance-journal" in record.get("tools", []), f"{agent_id}: governance journal missing")
    require("decision.v2" in record.get("output_contracts", []), f"{agent_id}: decision.v2 missing")
    require("agent-event.v2" in record.get("output_contracts", []), f"{agent_id}: agent-event.v2 missing")
    governance_policy = record.get("governance_policy", {})
    require(governance_policy.get("audit_logging") == "REQUIRED", f"{agent_id}: audit policy drifted")
    require(
        governance_policy.get("decision_logging") == "REQUIRED_WHEN_DECIDING_OR_RECOMMENDING",
        f"{agent_id}: decision policy drifted",
    )

task = TaskRecord("T-drift", "objective", "outcome", "michael", "michael", "cro", "michael", acceptance_test="accepted")
validate_runtime_contract("task", task.to_dict(), CONTRACTS)

delegation = Delegation(
    "D-drift", "T-drift", "cos", "cro", "objective", "outcome", "brief", ["accepted"], "P1", AuthorityLevel.L2, "accepted"
)
validate_runtime_contract("delegation", delegation.to_dict(), CONTRACTS)
validate_runtime_contract("agent-event", AuditEvent("drift_check", "cos", "T-drift", "corr-drift", 2, "ok").to_dict(), CONTRACTS)

ledger = TaskLedger()
governance = GovernanceJournal(ledger)
decision = governance.record_decision(
    decision_id="decision-drift",
    decision_type="OPERATING_JUDGMENT",
    decision_title="Runtime governance drift check",
    task_id="T-drift",
    correlation_id="corr-drift",
    agent_id="cos",
    agent_role="AI Chief of Staff",
    decision_owner="cos",
    authority_level=2,
    human_approval_required=False,
    decision="Preserve governed runtime contract",
    disposition="APPROVED",
    decision_basis_summary="The runtime governance contract must remain aligned with documented policy and configured mirrors.",
    evidence_references=["config:governance-policy.v1", "config:governance-logs.v1"],
    source_systems=["repository"],
    alternatives_considered=["allow drift", "fail CI on drift"],
    selection_criteria=["auditability", "contract integrity"],
    confidence="HIGH",
    risk_level="LOW",
    affected_entities=["all-registered-agents"],
    reversibility="REVERSIBLE",
    reversal_condition="A versioned governance policy explicitly supersedes this contract.",
    policy_rule_ids=["governance-policy-v1"],
    model_provider=None,
    model_id_version=None,
    prompt_template_version=None,
    skill_agent_version="drift-check-v1",
    data_classification="INTERNAL",
    outcome_validation="CI validates contracts, policy, configuration and documentation tokens.",
    outcome_status="VALIDATED",
    retention_class="GOVERNANCE_LONG_TERM",
)
validate_runtime_contract("decision-v2", decision, CONTRACTS)
event = governance.record_event(
    event_id="event-drift",
    event_type="governance.drift_checked",
    event_category="GOVERNANCE",
    action="VALIDATE",
    actor_type="SERVICE",
    actor_id="drift-check",
    actor_role="CI governance drift gate",
    task_id="T-drift",
    correlation_id="corr-drift",
    decision_id=decision["decision_id"],
    authority_level=2,
    policy_rule_ids=["governance-policy-v1"],
    capability_tool="check-runtime-doc-drift.py",
    target_resource="repository governance contracts",
    source_system="repository",
    input_summary="Validate runtime governance policy against contracts, configuration and documentation.",
    result_status="SUCCESS",
    output_summary="Governance runtime and documentation agree.",
    evidence_references=[decision["canonical_record_ref"]],
    risk_severity="LOW",
    data_classification="INTERNAL",
    model_provider=None,
    model_id_version=None,
    skill_agent_version="drift-check-v1",
    environment="CI",
    retention_class="GOVERNANCE_LONG_TERM",
)
validate_runtime_contract("agent-event-v2", event, CONTRACTS)
require(verify_audit_chain(ledger.list_records("audit_event_v2")), "Governance audit hash chain failed")

governance_logs = json.loads((ROOT / "config" / "governance-logs.v1.json").read_text())
require(governance_logs.get("canonical_state") == "TaskLedger", "Governance canonical state drifted")
require(governance_logs.get("write_order") == "CANONICAL_FIRST", "Governance write order drifted")
require(
    governance_logs["audit_log"]["spreadsheet_id"] == "1T8vKx4gaUJdeG8kSc18MsBbXpY4EbDF3exZ0RGpvND0",
    "CoS Audit Log ID drifted",
)
require(
    governance_logs["decision_log"]["spreadsheet_id"] == "1IJcwPuulqsNAa1lCW2MsmNgH6Vm5INPqTlcH4NR0xpw",
    "CoS Decision Log ID drifted",
)

env_text = (ROOT / ".env.example").read_text()
require("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID=C0BRL4GCL3A" in env_text, "Agent Ops Slack channel drifted")

required_docs = {
    "README.md": ["#mesh-agent-ops", "C0BRL4GCL3A", "TaskLedger", "ChiefOfStaffService"],
    "docs/architecture.md": ["GovernanceJournal", "decision.v2", "agent-event.v2", "TaskLedger"],
    "docs/decision-rights.md": ["decision.v2", "L4", "L5", "chain-of-thought"],
    "docs/explainable-decisions-audit.md": ["CoS Decision Log", "CoS Audit Log", "TaskLedger", "tamper-evident"],
    "docs/observability.md": ["decision.v2", "agent-event.v2", "verify_audit_chain"],
    "docs/phase-1-operating-contract.md": ["L4", "L5", "VERIFIED"],
    "docs/testing-evaluation.md": ["test_governance.py", "decision.v2", "agent-event.v2"],
}
for relative, tokens in required_docs.items():
    text = (ROOT / relative).read_text()
    for token in tokens:
        require(token in text, f"{relative}: expected documented runtime token {token!r}")

print("runtime/documentation drift check: OK")
