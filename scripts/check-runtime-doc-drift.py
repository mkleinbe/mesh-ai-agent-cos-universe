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
RELEASE = "2.0.0"


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

shared_capabilities = {
    item["capability"]: item for item in registry_source.get("shared_capabilities", [])
}
require("mesh-devils-advocate" in shared_capabilities, "Shared Mesh Devil's Advocate capability missing")
challenge = shared_capabilities["mesh-devils-advocate"]
require(challenge.get("deployment") == "EXTERNAL_SHARED_SKILL", "Shared challenge deployment drifted")
require(challenge.get("consumers") == ["cos", "cro"], "Shared challenge consumers drifted")
require(challenge.get("authority") == "ADVISORY_ONLY", "Shared challenge authority drifted")
require(challenge.get("canonical_facts_modified") is False, "Shared challenge cannot modify canonical facts")
require(challenge.get("external_action_included") is False, "Shared challenge cannot include external action")
require(
    challenge.get("request_contract") == "mesh.devils-advocate.challenge-request.v1",
    "Shared challenge request contract drifted",
)
require(
    challenge.get("response_contract") == "mesh.devils-advocate.challenge-packet.v1",
    "Shared challenge response contract drifted",
)

registry = load_registry(ROOT / "agents" / "registry.json")
require(len(registry) == 10, "Canonical Phase 1 roster must contain 10 agents")
require("devils-advocate" not in registry, "Devil's Advocate must not remain a workforce agent principal")
require("mesh-devils-advocate" in registry["cos"].get("skills", []), "CoS shared challenge entitlement missing")
require("mesh-devils-advocate" in registry["cro"].get("skills", []), "CRO shared challenge entitlement missing")
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
require(__version__ == RELEASE, f"Expected local ChatGPT MCP release {RELEASE}")
require(f'version = "{RELEASE}"' in pyproject_text, "Package and runtime release versions drifted")

package = json.loads((ROOT / "mcp" / "package.json").read_text())
package_lock = json.loads((ROOT / "mcp" / "package-lock.json").read_text())
require(package["version"] == RELEASE, "MCP package version drifted")
require(package_lock["version"] == RELEASE, "MCP package-lock version drifted")
require(package_lock["packages"][""]["version"] == RELEASE, "MCP package-lock root package version drifted")

mcp_contract = json.loads((ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json").read_text())
require(mcp_contract["runtime_release"] == RELEASE, "MCP release drifted")
require(mcp_contract["transport"] == "LOCAL_STDIO", "ChatGPT MCP transport must remain LOCAL_STDIO")
require(mcp_contract["serialized_runtime"] == "mesh_cos.mcp_runtime.MCPRuntime", "MCP runtime binding drifted")
require("devils-advocate" not in mcp_contract["agent_tool_allowlists"], "Devil's Advocate agent MCP principal remains")
require("skills.invoke_governed" in mcp_contract["agent_tool_allowlists"]["cos"], "CoS governed Skill invocation missing")
require("skills.invoke_governed" in mcp_contract["agent_tool_allowlists"]["cro"], "CRO governed Skill invocation missing")
local_runtime = mcp_contract["local_runtime"]
require(local_runtime["command"] == "node", "Local MCP command drifted")
require(local_runtime["args"] == ["mcp/dist/index.js"], "Local MCP entry point drifted")
require(local_runtime["agent_identity_env"] == "MESH_COS_AGENT_ID", "Local agent identity binding drifted")
require(local_runtime["ledger_path_env"] == "MESH_COS_LEDGER_PATH", "Local canonical ledger binding drifted")
require(mcp_contract["deployment"]["chatgpt_runtime"] == "BUNDLED_LOCAL_STDIO", "ChatGPT runtime deployment mode drifted")
require(mcp_contract["deployment"]["managed_remote"] == "OPTIONAL_NOT_REQUIRED", "Remote MCP incorrectly became mandatory")

manifest_paths = sorted((ROOT / "chatgpt" / "workspace-agents").glob("*.json"))
require(len(manifest_paths) == 10, "Workspace Agent package must contain exactly 10 manifests")
require(not (ROOT / "chatgpt" / "workspace-agents" / "devils-advocate.json").exists(), "Devil's Advocate Workspace Agent remains")
require(not (ROOT / "chatgpt" / "skills" / "mesh-devils-advocate").exists(), "Duplicate repository-local Devil's Advocate Skill remains")
require(not (ROOT / "agents" / "devils-advocate.md").exists(), "Duplicate Devil's Advocate role card remains")

for manifest_path in manifest_paths:
    manifest = json.loads(manifest_path.read_text())
    agent_id = manifest["agent_id"]
    require(manifest["repository_release"] == RELEASE, f"{manifest_path.name}: Workspace Agent release drifted")
    expected_shared = ["mesh-devils-advocate"] if agent_id in {"cos", "cro"} else []
    require(manifest.get("shared_skills", []) == expected_shared, f"{agent_id}: shared Skill projection drifted")
    require(
        manifest["builder_configuration"].get("shared_skills", []) == expected_shared,
        f"{agent_id}: builder shared Skill projection drifted",
    )
    mcp = manifest["mcp"]
    require(mcp["transport"] == "LOCAL_STDIO", f"{agent_id}: Workspace Agent MCP transport drifted")
    require(mcp["command"] == "node", f"{agent_id}: Workspace Agent MCP command drifted")
    require(mcp["args"] == ["mcp/dist/index.js"], f"{agent_id}: Workspace Agent MCP args drifted")
    require(mcp["env"]["MESH_COS_AGENT_ID"] == agent_id, f"{agent_id}: MCP identity env drifted")
    require(mcp["env"]["MESH_COS_LEDGER_PATH"] == ".mesh-cos/task-ledger.sqlite3", f"{agent_id}: ledger path drifted")
    require("server_url_env" not in mcp, f"{agent_id}: remote MCP endpoint dependency reintroduced")


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
    skill_agent_version="drift-check-v2",
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
    skill_agent_version="drift-check-v2",
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
require("MESH_COS_AGENT_ID=cos" in env_text, "Local agent identity example missing")
require("MESH_COS_LEDGER_PATH=.mesh-cos/task-ledger.sqlite3" in env_text, "Canonical local ledger path example missing")
require("MESH_COS_PYTHON_BIN=python" in env_text, "Python bridge runtime example missing")
require("MESH_COS_MCP_SERVER_URL" not in env_text, "Remote MCP endpoint dependency reintroduced")
require("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID=C0BRL4GCL3A" in env_text, "Agent Ops Slack channel drifted")

required_docs = {
    "README.md": ["v2.0.0", "10-agent", "Mesh Devil's Advocate", "LOCAL_STDIO", "TaskLedger"],
    "AGENTS.md": ["10-agent", "Mesh Devil's Advocate", "shared Skill", "TaskLedger"],
    "SECURITY.md": ["Mesh Devil's Advocate", "advisory", "MCPRuntime", "human-only", "100% branch-aware"],
    "CONTRIBUTING.md": ["100%", "production-preflight.py"],
    "docs/architecture.md": ["v2.0.0", "10-agent", "Mesh Devil's Advocate", "LOCAL_STDIO", "TaskLedger"],
    "docs/agent-registry.md": ["Mesh Devil's Advocate", "shared capability", "advisory"],
    "docs/decision-rights.md": ["Mesh Devil's Advocate", "advisory", "canonical facts"],
    "docs/delegation-model.md": ["Mesh Devil's Advocate", "shared Skill", "not a delegated agent"],
    "docs/conflict-resolution.md": ["Mesh Devil's Advocate", "challenge", "advisory"],
    "docs/production-readiness.md": ["v2.0.0", "10", "Mesh Devil's Advocate", "LOCAL_STDIO", "100%"],
    "docs/security-governance.md": ["Mesh Devil's Advocate", "LOCAL_STDIO", "deny-by-default", "human-only"],
    "docs/testing-evaluation.md": ["v2.0.0", "shared Devil's Advocate", "100%", "check-chatgpt-packages.py"],
    "docs/runbook.md": ["v2.0.0", "10 agents", "Mesh Devil's Advocate", "MESH_COS_LEDGER_PATH", "npm run check"],
    "chatgpt/README.md": ["2.0.0", "10 Workspace Agents", "Mesh Devil's Advocate", "LOCAL_STDIO", "TaskLedger"],
    "chatgpt/mcp/README.md": ["2.0.0", "10 agent", "Mesh Devil's Advocate", "LOCAL_STDIO", "human-only"],
    "chatgpt/workspace-agent-builder-prompt.md": ["v2.0.0", "10 agents", "Mesh Devil's Advocate", "shared Skill", "Always ask"],
    "docs/release-2.0.0-shared-devils-advocate.md": ["v2.0.0", "Mesh Devil's Advocate", "Breaking", "Semantic Tag"],
    "RELEASE.md": ["v2.0.0", "Mesh Devil's Advocate", "Production activation boundary"],
}
for relative, tokens in required_docs.items():
    text = (ROOT / relative).read_text()
    for token in tokens:
        require(token in text, f"{relative}: expected documented runtime token {token!r}")

print("runtime/documentation drift check: OK")
