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
    "devils-advocate": ("Devil's Advocate", "cos", "mesh-devils-advocate"),
    "message-ops": ("Message Operations", "cos", "mesh-message-operations"),
}


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
require(__version__ == "0.2.0", "Workspace Agent release must be 0.2.0")
require(f'version = "{__version__}"' in (ROOT / "pyproject.toml").read_text(), "Runtime/package version drifted")

contract = json.loads(MCP.read_text())
require(contract["runtime_release"] == __version__, "MCP contract release drifted")
policy = WorkspaceAgentMCPPolicy.from_file(MCP)
require(policy.validate_runtime_bindings() == [], "MCP runtime binding is unresolved")
contract_allowlists = contract["agent_tool_allowlists"]

for agent_id, (display_name, parent_id, skill_name) in EXPECTED.items():
    record = registry[agent_id]
    skill_dir = SKILLS / skill_name
    for relative in ("SKILL.md", "agents/openai.yaml", "references/role-contract.md"):
        require((skill_dir / relative).is_file(), f"{agent_id}: missing Skill resource {relative}")
    frontmatter = parse_frontmatter((skill_dir / "SKILL.md").read_text())
    require(frontmatter.get("name") == skill_name, f"{agent_id}: Skill name drifted")
    require(len(frontmatter.get("description", "")) >= 80, f"{agent_id}: Skill description too thin")
    metadata = (skill_dir / "agents" / "openai.yaml").read_text()
    require(f'display_name: "{display_name}"' in metadata, f"{agent_id}: Skill UI metadata drifted")

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
    require(config["mcp"]["server_url_env"] == "MESH_COS_MCP_SERVER_URL", f"{agent_id}: MCP endpoint configuration drifted")
    require(config["mcp"]["allowed_tools"] == contract_allowlists[agent_id], f"{agent_id}: MCP allowlist drifted")
    builder = config["builder_configuration"]
    require(builder["name"] == display_name, f"{agent_id}: builder name drifted")
    require(builder["skill"] == skill_name, f"{agent_id}: builder Skill drifted")
    require(builder["custom_mcp"] == "mesh-cos-mcp", f"{agent_id}: builder MCP drifted")
    require(builder["mcp_allowed_tools"] == config["mcp"]["allowed_tools"], f"{agent_id}: builder MCP tools drifted")
    require(builder["write_action_approval"] == "Always ask", f"{agent_id}: builder write approval weakened")
    require(builder["connector_action_constraints"] == config["connector_action_constraints"], f"{agent_id}: connector constraints drifted")
    require(not re.search(r"\bv\d+(?:\.\d+)*\b", display_name, re.I), f"{agent_id}: version embedded in stable role name")

require("task.reassign" in contract_allowlists["cos"], "CoS reassignment capability missing")
for agent_id, allowed in contract_allowlists.items():
    if agent_id != "cos":
        require("task.reassign" not in allowed, f"{agent_id}: unauthorized task reassignment")
require("approval.get" in contract_allowlists["message-ops"], "Message Operations approval read missing")
require("approval.record_decision" not in contract_allowlists["message-ops"], "Message Operations cannot decide approval")

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
for token in ("11 agents", "mesh-cos-mcp", "MESH_COS_MCP_SERVER_URL", "Always ask", "negative authority test", "missing-evidence test"):
    require(token in prompt, f"Workspace Agent builder prompt missing {token!r}")

env_text = (ROOT / ".env.example").read_text()
require("MESH_COS_MCP_SERVER_URL=" in env_text, "MCP server URL environment placeholder missing")

print("ChatGPT Workspace Agent package drift check: OK")
