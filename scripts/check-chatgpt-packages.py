#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

from mesh_cos import __version__
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy

ROOT = Path(__file__).resolve().parents[1]
CHATGPT = ROOT / "chatgpt"
SKILLS = CHATGPT / "skills"
AGENTS = CHATGPT / "workspace-agents"
MCP = CHATGPT / "mcp" / "mesh-cos-mcp.v1.json"
MCP_PACKAGE = ROOT / "mcp"

EXPECTED = {
    "cos": ("Chief of Staff", None, "mesh-chief-of-staff"),
    "agentops": ("AgentOps Controller", "cos", "mesh-agentops-controller"),
    "answer-desk": ("Answer & Decision Desk", "cos", "mesh-answer-decision-desk"),
    "cro": ("CRO", "cos", "mesh-cro"),
    "cfo": ("CFO", "cos", "mesh-cfo"),
    "coo": ("COO", "cos", "mesh-coo"),
    "consultant-network-steward": ("Consultant Network Steward", "coo", "mesh-consultant-network-steward"),
    "cmo": ("CMO", "cos", "mesh-cmo"),
    "vp-content": ("VP Content", "cmo", "mesh-vp-content"),
    "message-ops": ("Message Operations", "cos", "mesh-message-operations"),
}
SHARED_CHALLENGE_CONSUMERS = {"cos", "cro"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def parse_frontmatter(text: str) -> dict[str, str]:
    require(text.startswith("---\n"), "SKILL.md frontmatter missing")
    end = text.find("\n---\n", 4)
    require(end > 0, "SKILL.md frontmatter not closed")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


registry_source = json.loads((ROOT / "agents" / "registry.json").read_text())
registry = {record["agent_id"]: record for record in registry_source["agents"]}
require(set(registry) == set(EXPECTED), "Workspace Agent roster drifted from canonical registry")
require(__version__ == "2.0.0", "Workspace Agent release must be 2.0.0")
require(f'version = "{__version__}"' in (ROOT / "pyproject.toml").read_text(), "Runtime/package version drifted")

shared = {item["capability"]: item for item in registry_source.get("shared_capabilities", [])}
challenge = shared.get("mesh-devils-advocate")
require(challenge is not None, "Shared Mesh Devil's Advocate capability missing")
require(challenge["deployment"] == "EXTERNAL_SHARED_SKILL", "Shared challenge deployment drifted")
require(set(challenge["consumers"]) == SHARED_CHALLENGE_CONSUMERS, "Shared challenge consumer set drifted")
require(challenge["authority"] == "ADVISORY_ONLY", "Shared challenge authority drifted")
require(challenge["canonical_facts_modified"] is False, "Shared challenge cannot modify canonical facts")
require(challenge["external_action_included"] is False, "Shared challenge cannot execute external actions")
require(not (ROOT / "agents" / "devils-advocate.md").exists(), "Duplicate Devil's Advocate role card remains")
require(not (AGENTS / "devils-advocate.json").exists(), "Duplicate Devil's Advocate Workspace Agent remains")
require(not (SKILLS / "mesh-devils-advocate").exists(), "Duplicate repository-local Mesh Devil's Advocate Skill remains")

contract = json.loads(MCP.read_text())
require(contract["runtime_release"] == __version__, "MCP contract release drifted")
require(contract["transport"] == "LOCAL_STDIO", "Bundled local stdio must be the primary MCP transport")
require(contract["local_runtime"]["command"] == "node", "Local MCP command drifted")
require(contract["local_runtime"]["args"] == ["mcp/dist/index.js"], "Local MCP entrypoint drifted")
require(contract["local_runtime"]["agent_identity_env"] == "MESH_COS_AGENT_ID", "Local MCP agent binding drifted")
require(contract["local_runtime"]["ledger_path_env"] == "MESH_COS_LEDGER_PATH", "Local MCP ledger binding drifted")
require("server_url_env" not in contract, "Remote MCP URL must not be required for ChatGPT")
require(contract["deployment"]["chatgpt_runtime"] == "BUNDLED_LOCAL_STDIO", "ChatGPT MCP deployment drifted")
require(contract["deployment"]["managed_remote"] == "OPTIONAL_NOT_REQUIRED", "Managed remote transport must remain optional")
policy = WorkspaceAgentMCPPolicy.from_file(MCP)
require(policy.validate_runtime_bindings() == [], "MCP runtime binding is unresolved")
contract_allowlists = contract["agent_tool_allowlists"]
require(set(contract_allowlists) == set(EXPECTED), "MCP agent principal roster drifted")
require("devils-advocate" not in contract_allowlists, "Devil's Advocate must not be an MCP agent principal")

for relative in (
    "README.md",
    "package.json",
    "package-lock.json",
    "tsconfig.json",
    "src/index.ts",
    "src/server.ts",
    "src/python-bridge.ts",
    "scripts/smoke-test.mjs",
):
    require((MCP_PACKAGE / relative).is_file(), f"Local MCP package missing {relative}")
package = json.loads((MCP_PACKAGE / "package.json").read_text())
package_lock = json.loads((MCP_PACKAGE / "package-lock.json").read_text())
require(package["name"] == "@meshdigitalio/mesh-cos-mcp", "Local MCP package name drifted")
require(package["version"] == __version__, "Local MCP package version drifted")
require(package_lock["version"] == __version__, "Local MCP package-lock version drifted")
require(package_lock["packages"][""]["version"] == __version__, "Local MCP root lock package version drifted")
require(package["dependencies"].get("@modelcontextprotocol/sdk") == "1.30.0", "Official MCP SDK dependency drifted")

for agent_id, (display_name, parent_id, skill_name) in EXPECTED.items():
    record = registry[agent_id]
    skill_dir = SKILLS / skill_name
    for relative in (
        "SKILL.md",
        "agents/openai.yaml",
        "references/role-contract.md",
        "references/production-readiness.md",
    ):
        require((skill_dir / relative).is_file(), f"{agent_id}: missing Skill resource {relative}")
    frontmatter = parse_frontmatter((skill_dir / "SKILL.md").read_text())
    require(frontmatter.get("name") == skill_name, f"{agent_id}: Skill name drifted")
    require(len(frontmatter.get("description", "")) >= 80, f"{agent_id}: Skill description too thin")
    metadata = (skill_dir / "agents" / "openai.yaml").read_text()
    require(f'display_name: "{display_name}"' in metadata, f"{agent_id}: Skill UI metadata drifted")
    readiness = (skill_dir / "references" / "production-readiness.md").read_text()
    require("local stdio" in readiness.lower(), f"{agent_id}: Skill local MCP readiness missing")
    require("MESH_COS_MCP_SERVER_URL" not in readiness, f"{agent_id}: Skill still requires remote MCP URL")

    config_path = AGENTS / f"{agent_id}.json"
    require(config_path.is_file(), f"{agent_id}: Workspace Agent manifest missing")
    config = json.loads(config_path.read_text())
    require(config["display_name"] == display_name, f"{agent_id}: display name drifted")
    require(config["parent_agent_id"] == parent_id, f"{agent_id}: parent drifted")
    require(config["implementation_version"] == record["version"], f"{agent_id}: implementation version drifted")
    require(config["repository_release"] == __version__, f"{agent_id}: repository release drifted")
    require(config["accountable_domain"] == record["accountable_domain"], f"{agent_id}: accountable domain drifted")
    require(config["decision_authority"] == record["decision_authority"], f"{agent_id}: decision authority drifted")
    require(config["required_approvals"] == record["required_approvals"], f"{agent_id}: approvals drifted")
    require(config["prohibited_actions"] == record["prohibited_actions"], f"{agent_id}: prohibited actions drifted")
    require(config["max_delegation_depth"] == record["max_delegation_depth"], f"{agent_id}: delegation depth drifted")
    require(config["skill"] == skill_name, f"{agent_id}: Skill attachment drifted")
    require(config["canonical_state"] == "TaskLedger", f"{agent_id}: canonical state drifted")
    require(config["write_action_policy"]["default"] == "ALWAYS_ASK", f"{agent_id}: write approval weakened")
    require(config["governance"]["audit_logging"] == "REQUIRED", f"{agent_id}: audit policy weakened")
    require(config["governance"]["decision_logging"] == "REQUIRED_WHEN_DECIDING_OR_RECOMMENDING", f"{agent_id}: decision logging weakened")
    require(config["governance"]["private_chain_of_thought"] == "PROHIBITED", f"{agent_id}: reasoning persistence drifted")
    expected_shared = ["mesh-devils-advocate"] if agent_id in SHARED_CHALLENGE_CONSUMERS else []
    require(config.get("shared_skills", []) == expected_shared, f"{agent_id}: shared Skill projection drifted")
    require(config["builder_configuration"].get("shared_skills", []) == expected_shared, f"{agent_id}: builder shared Skill projection drifted")
    if agent_id in SHARED_CHALLENGE_CONSUMERS:
        require("mesh-devils-advocate" in record.get("skills", []), f"{agent_id}: registry shared Skill entitlement missing")
        require("skills.invoke_governed" in contract_allowlists[agent_id], f"{agent_id}: governed Skill invocation missing")
    else:
        require("mesh-devils-advocate" not in record.get("skills", []), f"{agent_id}: unauthorized shared challenge entitlement")

    mcp = config["mcp"]
    require(mcp["transport"] == "LOCAL_STDIO", f"{agent_id}: MCP transport drifted")
    require(mcp["command"] == "node" and mcp["args"] == ["mcp/dist/index.js"], f"{agent_id}: local MCP launch drifted")
    require(mcp["env"]["MESH_COS_AGENT_ID"] == agent_id, f"{agent_id}: MCP agent binding drifted")
    require(bool(mcp["env"]["MESH_COS_LEDGER_PATH"]), f"{agent_id}: canonical ledger path missing")
    require("server_url_env" not in mcp, f"{agent_id}: remote MCP URL dependency remains")
    require(mcp["allowed_tools"] == contract_allowlists[agent_id], f"{agent_id}: MCP allowlist drifted")
    builder = config["builder_configuration"]
    require(builder["name"] == display_name, f"{agent_id}: builder name drifted")
    require(builder["skill"] == skill_name, f"{agent_id}: builder Skill drifted")
    require(builder["custom_mcp"] == "mesh-cos-mcp", f"{agent_id}: builder MCP drifted")
    require(builder["mcp_transport"] == "LOCAL_STDIO", f"{agent_id}: builder MCP transport drifted")
    require(builder["mcp_command"] == "node", f"{agent_id}: builder MCP command drifted")
    require(builder["mcp_args"] == ["mcp/dist/index.js"], f"{agent_id}: builder MCP args drifted")
    require(builder["mcp_environment"]["MESH_COS_AGENT_ID"] == agent_id, f"{agent_id}: builder agent binding drifted")
    require(builder["mcp_allowed_tools"] == mcp["allowed_tools"], f"{agent_id}: builder MCP tools drifted")
    require(builder["write_action_approval"] == "Always ask", f"{agent_id}: builder write approval weakened")
    require(builder["connector_action_constraints"] == config["connector_action_constraints"], f"{agent_id}: connector constraints drifted")
    require(not re.search(r"\bv\d+(?:\.\d+)*\b", display_name, re.I), f"{agent_id}: version embedded in stable role name")

require("task.reassign" in contract_allowlists["cos"], "CoS reassignment capability missing")
for agent_id, allowed in contract_allowlists.items():
    if agent_id != "cos":
        require("task.reassign" not in allowed, f"{agent_id}: unauthorized task reassignment")
require("approval.get" in contract_allowlists["message-ops"], "Message Operations approval read missing")
require("approval.record_decision" not in contract_allowlists["message-ops"], "Message Operations cannot decide approval")
require("approval.record_decision" not in contract_allowlists["cos"], "Agent allowlists cannot include human approval decisions")
require("reliability.human_override" not in contract_allowlists["cos"], "Agent allowlists cannot include human reliability override")
require(set(contract["human_tool_allowlist"]) == {"approval.record_decision", "reliability.human_override"}, "Human-only MCP allowlist drifted")

answer_desk = json.loads((AGENTS / "answer-desk.json").read_text())
require(answer_desk["channels"]["slack"]["enabled"] is False, "Answer Desk Slack cannot be enabled without channel ID")
require(answer_desk["channels"]["slack"]["channel_id"] is None, "Answer Desk Slack channel ID must remain unset until configured")

cmo = json.loads((AGENTS / "cmo.json").read_text())
vp_content = json.loads((AGENTS / "vp-content.json").read_text())
cro = json.loads((AGENTS / "cro.json").read_text())
message_ops = json.loads((AGENTS / "message-ops.json").read_text())
require(any("no autonomous public posting" in rule for rule in cmo["connector_action_constraints"]), "CMO LinkedIn constraint missing")
require(any("public publishing remains human-gated" in rule for rule in vp_content["connector_action_constraints"]), "VP Content publishing constraint missing")
require(any("research/enrichment only" in rule for rule in cro["connector_action_constraints"]), "CRO Apollo research-only constraint missing")
require(any("approval" in rule.lower() for rule in message_ops["connector_action_constraints"]), "Message Operations approval constraint missing")

prompt = (CHATGPT / "workspace-agent-builder-prompt.md").read_text()
for token in (
    "10 agents",
    "v2.0.0",
    "Mesh Devil's Advocate",
    "shared Skill",
    "mesh-cos-mcp",
    "local stdio",
    "mcp/dist/index.js",
    "MESH_COS_AGENT_ID",
    "MESH_COS_LEDGER_PATH",
    "Always ask",
    "negative authority test",
    "missing-evidence test",
    "human-approval spoofing test",
    "completion-versus-verification test",
    "replay-safety test",
):
    require(token in prompt, f"Workspace Agent builder prompt missing {token!r}")
require("MESH_COS_MCP_SERVER_URL" not in prompt, "Builder prompt still requires remote MCP URL")

env_text = (ROOT / ".env.example").read_text()
require("MESH_COS_LEDGER_PATH=" in env_text, "Local MCP canonical ledger environment placeholder missing")
require("MESH_COS_AGENT_ID=" in env_text, "Local MCP agent binding environment placeholder missing")
require("MESH_COS_MCP_SERVER_URL=" not in env_text, "Remote MCP URL placeholder must be removed")

print("ChatGPT Workspace Agent package drift check: OK")
