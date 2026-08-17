#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from mesh_cos import __version__
from mesh_cos.audit import AuditEvent
from mesh_cos.contracts import agent_record_contract, validate_runtime_contract
from mesh_cos.governance import GovernanceJournal, verify_audit_chain
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, Delegation, TaskRecord
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
RELEASE = "1.0.0"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


for schema_path in sorted(CONTRACTS.glob("*.schema.json")):
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    require(schema.get("additionalProperties") is False, f"{schema_path.name}: contracts must be closed")
    require("version" in schema.get("required", []), f"{schema_path.name}: version must be required")

registry_source = json.loads((ROOT / "agents" / "registry.json").read_text())
identity_policy = registry_source.get("role_identity_policy", {})
require(identity_policy.get("display_names_are_stable") is True, "Role identity policy drifted")
require(identity_policy.get("implementation_version_field") == "version", "Role implementation-version policy drifted")

registry = load_registry(ROOT / "agents" / "registry.json")
require(len(registry) == 11, "Canonical Phase 1 roster must contain 11 agents")
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

canonical_role_names = {
    "cro": "CRO",
    "cfo": "CFO",
    "coo": "COO",
    "consultant-network-steward": "Consultant Network Steward",
    "cmo": "CMO",
    "vp-content": "VP Content",
}
required_role_actions = {
    "cro": {
        "commercial_analysis", "opportunity_qualification", "pipeline_health_analysis", "pursuit_prioritization",
        "proposal_strategy", "next_best_commercial_action", "expansion_strategy", "commercial_risk_framing",
        "request_cfo_economics", "request_coo_feasibility", "request_devils_advocate_review",
    },
    "cfo": {
        "engagement_economics", "pricing_scenarios", "cost_to_serve_analysis", "contribution_economics",
        "margin_analysis", "margin_leakage_detection", "working_capital_implications", "economic_scenario_comparison",
        "assumption_management", "financial_risk_analysis", "forecast_vs_actual",
    },
    "coo": {
        "delivery_feasibility", "delivery_configuration", "capacity_analysis", "pod_resource_composition",
        "dependency_readiness_analysis", "delivery_risk_sensing", "partner_capacity_analysis",
        "operational_constraint_management", "staffing_recommendation", "delegate_network_steward",
    },
    "consultant-network-steward": {
        "candidate_identification", "candidate_matching", "candidate_fit_check", "availability_freshness_check",
        "validation_timestamp_check", "rate_validity_check", "contracting_readiness_check", "readiness_gap_analysis",
        "refresh_workflow", "mark_requires_refresh", "establish_staffing_ready_status",
    },
    "cmo": {
        "marketing_strategy", "audience_icp_strategy", "category_positioning", "campaign_strategy",
        "demand_campaign_architecture", "distribution_strategy", "campaign_performance_optimization",
        "marketing_commercial_feedback", "brand_governance", "editorial_priority", "content_review", "delegate_vp_content",
    },
    "vp-content": {
        "editorial_planning", "editorial_calendar_management", "source_evidence_assembly", "draft_content",
        "channel_adaptation", "derivative_content_production", "repurpose_content", "ip_reuse",
        "content_inventory_management", "editorial_qa", "performance_feedback", "prepare_for_cmo_review",
    },
}
for agent_id, display_name in canonical_role_names.items():
    record = registry[agent_id]
    require(record["display_name"] == display_name, f"{agent_id}: canonical role name drifted")
    require(required_role_actions[agent_id] <= set(record.get("permitted_actions", [])), f"{agent_id}: capability surface drifted")

require(registry["cfo"]["accountable_domain"] == "engagement finance and FP&A", "CFO domain drifted")
require(registry["coo"]["accountable_domain"] == "delivery feasibility, capacity, and resource readiness", "COO domain drifted")
require(registry["consultant-network-steward"]["parent_agent_id"] == "coo", "Network Steward hierarchy drifted")

pyproject_text = (ROOT / "pyproject.toml").read_text()
require(__version__ == RELEASE, f"Expected production-readiness release {RELEASE}")
require(f'version = "{RELEASE}"' in pyproject_text, "Package and runtime release versions drifted")

mcp_contract = json.loads((ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json").read_text())
require(mcp_contract["runtime_release"] == RELEASE, "MCP release drifted")
for manifest_path in sorted((ROOT / "chatgpt" / "workspace-agents").glob("*.json")):
    manifest = json.loads(manifest_path.read_text())
    require(manifest["repository_release"] == RELEASE, f"{manifest_path.name}: Workspace Agent release drifted")

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
    agent_role="Chief of Staff",
    decision_owner="cos",
    authority_level=2,
    human_approval_required=False,
    decision="Preserve governed runtime contract",
    disposition="APPROVED",
    decision_basis_summary="Runtime governance must remain aligned with documented policy and deployment packages.",
    evidence_references=["config:governance-policy.v1", "config:governance-logs.v1", "chatgpt:mcp-contract"],
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
    outcome_validation="CI validates contracts, policy, deployment packages and documentation tokens.",
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
    input_summary="Validate runtime governance policy against contracts, configuration, Workspace Agent packages and documentation.",
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
require(governance_logs["audit_log"]["spreadsheet_id"] == "1T8vKx4gaUJdeG8kSc18MsBbXpY4EbDF3exZ0RGpvND0", "CoS Audit Log ID drifted")
require(governance_logs["decision_log"]["spreadsheet_id"] == "1IJcwPuulqsNAa1lCW2MsmNgH6Vm5INPqTlcH4NR0xpw", "CoS Decision Log ID drifted")

env_text = (ROOT / ".env.example").read_text()
require("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID=C0BRL4GCL3A" in env_text, "Agent Ops Slack channel drifted")
require("MESH_COS_MCP_SERVER_URL=" in env_text, "Workspace Agent MCP endpoint placeholder missing")

required_docs = {
    "README.md": ["v1.0.0 Production Readiness", "#mesh-agent-ops", "C0BRL4GCL3A", "TaskLedger", "MCPRuntime", "Workspace Agents"],
    "AGENTS.md": ["v1.0.0 Production Readiness", "human-only", "task.complete", "task.verify", "Production activation"],
    "SECURITY.md": ["v1.0.0 Production Readiness", "MCPRuntime", "human-only", "replay", "100% branch-aware"],
    "CONTRIBUTING.md": ["v1.0.0 Production Readiness", "100%", "production-preflight.py"],
    "docs/agent-registry.md": ["Role identity policy", "CFO", "COO", "permitted_actions", "Workspace Agent"],
    "docs/architecture.md": ["v1.0.0", "MCPRuntime", "decision.v2", "agent-event.v2", "TaskLedger"],
    "docs/decision-rights.md": ["decision.v2", "L4", "L5", "chain-of-thought", "Always ask"],
    "docs/explainable-decisions-audit.md": ["CoS Decision Log", "CoS Audit Log", "TaskLedger", "tamper-evident", "agent_role", "skill_agent_version"],
    "docs/observability.md": ["decision.v2", "agent-event.v2", "verify_audit_chain"],
    "docs/phase-1-operating-contract.md": ["L4", "L5", "VERIFIED", "Stable role identity"],
    "docs/production-readiness.md": ["v1.0.0 Production Readiness", "100%", "ProductionPreflight", "task.complete", "task.verify"],
    "docs/release-1.0.0-production-readiness.md": ["v1.0.0", "100%", "Semantic Tag", "Production Activation"],
    "docs/security-governance.md": ["v1.0.0", "MCPRuntime", "deny-by-default", "replay", "human-only"],
    "docs/testing-evaluation.md": ["v1.0.0", "100%", "check-chatgpt-packages.py", "MCPRuntime"],
    "docs/runbook.md": ["v1.0.0", "MESH_COS_MCP_SERVER_URL", "production-preflight.py", "task.complete"],
    "chatgpt/README.md": ["1.0.0", "Workspace Agent", "TaskLedger", "MCPRuntime"],
    "chatgpt/mcp/README.md": ["1.0.0", "MCPRuntime", "human-only", "replay"],
    "chatgpt/workspace-agent-builder-prompt.md": ["v1.0.0", "11 agents", "Always ask", "negative authority test", "replay-safety test"],
    "RELEASE.md": ["v1.0.0 Production Readiness", "100%", "Production activation boundary"],
}
for relative, tokens in required_docs.items():
    text = (ROOT / relative).read_text()
    for token in tokens:
        require(token in text, f"{relative}: expected documented runtime token {token!r}")

print("runtime/documentation drift check: OK")
