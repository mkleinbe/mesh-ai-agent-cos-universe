#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from mesh_cos import __version__
from mesh_cos.governance import GovernanceJournal, verify_audit_chain
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
RELEASE = "4.0.0"
EXPECTED_AGENTS = {
    "cos",
    "agentops",
    "answer-desk",
    "cro",
    "cfo",
    "coo",
    "consultant-network-steward",
    "cmo",
    "vp-content",
    "message-ops",
}
HUMAN_ONLY = {"approval.record_decision", "reliability.human_override"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


for schema_path in sorted(CONTRACTS.glob("*.schema.json")):
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    require(schema.get("additionalProperties") is False, f"{schema_path.name}: contracts must be closed")
    require("version" in schema.get("required", []), f"{schema_path.name}: version must be required")

registry_source = json.loads((ROOT / "agents" / "registry.json").read_text())
registry = load_registry(ROOT / "agents" / "registry.json")
require(set(registry) == EXPECTED_AGENTS, "Canonical Phase 1 roster must contain exactly 10 agents")
require("devils-advocate" not in registry, "Devil's Advocate must remain outside the agent roster")
require("message-ops" in registry, "Message Operations must remain the tenth registered agent")
shared = {item["capability"]: item for item in registry_source.get("shared_capabilities", [])}
require(set(shared) == {"mesh-devils-advocate"}, "Only Mesh Devil's Advocate may be an external Phase 1 shared Skill")
challenge = shared["mesh-devils-advocate"]
require(set(challenge["consumers"]) == {"cos", "cro"}, "Devil's Advocate consumers drifted")
require(challenge["authority"] == "ADVISORY_ONLY", "Devil's Advocate authority drifted")
require(challenge["canonical_facts_modified"] is False, "Devil's Advocate cannot modify canonical facts")
require(challenge["external_action_included"] is False, "Devil's Advocate cannot execute external actions")

require(__version__ == RELEASE, f"Expected runtime release {RELEASE}")
require(f'version = "{RELEASE}"' in (ROOT / "pyproject.toml").read_text(), "Package/runtime release drifted")
contract = json.loads((ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json").read_text())
require(contract["runtime_release"] == RELEASE, "MCP release drifted")
require(set(contract["agent_tool_allowlists"]) == EXPECTED_AGENTS, "MCP principal roster drifted")
require(set(contract["human_tool_allowlist"]) == HUMAN_ONLY, "Human-only tool set drifted")
for agent_id, allowlist in contract["agent_tool_allowlists"].items():
    require(HUMAN_ONLY.isdisjoint(allowlist), f"{agent_id}: human-only tool leaked to agent")
require("task.verify" in contract["agent_tool_allowlists"]["cos"], "CoS verification authority missing")
for agent_id, allowlist in contract["agent_tool_allowlists"].items():
    if agent_id != "cos":
        require("task.verify" not in allowlist, f"{agent_id}: verification authority unexpectedly expanded")

runtime = MCPRuntime(TaskLedger())
require(set(runtime.registry) == EXPECTED_AGENTS, "Serialized MCP runtime roster drifted")

# Machine-level completion versus verification certification.
task = runtime.cos.intake(
    objective="certify completion verification separation",
    expected_outcome="evidence-backed completion then independent verification",
    requested_by="michael",
    executive_sponsor="michael",
    accountable_agent="cro",
    decision_owner="michael",
    authority_level=AuthorityLevel.L2,
    acceptance_test="synthetic evidence is present",
)
for status in (TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.QA):
    runtime.cos.advance(task.task_id, status)
completed = runtime.call_agent("cro", "task.complete", {"task_id": task.task_id, "outcome": "done", "evidence_references": ["synthetic://completion"]})
require(completed["status"] == "COMPLETED", "Owner completion did not produce COMPLETED")
require(runtime.ledger.get_task(task.task_id).status == TaskStatus.COMPLETED, "Canonical task did not persist COMPLETED")
try:
    runtime.call_agent("cro", "task.verify", {"task_id": task.task_id, "passed": True, "reason": "self", "evidence_references": ["synthetic://verify"]})
except PermissionError:
    pass
else:
    raise SystemExit("CRO self-verification unexpectedly succeeded")
verified = runtime.call_agent("cos", "task.verify", {"task_id": task.task_id, "passed": True, "reason": "acceptance passed", "evidence_references": ["synthetic://verify"]})
require(verified["status"] == "VERIFIED", "Authorized verification did not produce VERIFIED")

# Governance chain certification is separate from business-state success.
journal = GovernanceJournal(runtime.ledger)
journal.record_event(
    event_type="certification.completed",
    event_category="GOVERNANCE",
    action="VERIFY",
    actor_type="SERVICE",
    actor_id="runtime-doc-drift",
    actor_role="independent certification gate",
    task_id=task.task_id,
    correlation_id="corr-v4-drift",
    authority_level=2,
    policy_rule_ids=["v4-completion-verification"],
    capability_tool="check-runtime-doc-drift.py",
    target_resource=task.task_id,
    source_system="TaskLedger",
    input_summary="Certify roster, authority and lifecycle agreement.",
    result_status="SUCCESS",
    output_summary="Runtime and documented lifecycle agree.",
    evidence_references=["synthetic://verify"],
    risk_severity="LOW",
    data_classification="INTERNAL",
    model_provider=None,
    model_id_version=None,
    skill_agent_version="4.0.0",
    environment="TEST",
    retention_class="GOVERNANCE_LONG_TERM",
)
require(verify_audit_chain(runtime.ledger.list_records("audit_event_v2")), "Governance audit chain failed")

print("runtime/documentation drift and lifecycle certification: OK")
