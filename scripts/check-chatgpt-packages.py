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
RELEASE = "4.0.0"
HUMAN_ONLY = {"approval.record_decision", "reliability.human_override"}
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
DA_CONSUMERS = {"cos", "cro"}
CURRENT_DOCS = [
    ROOT / "README.md",
    ROOT / "AGENTS.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "agent-registry.md",
    ROOT / "docs" / "decision-rights.md",
    ROOT / "docs" / "delegation-model.md",
    ROOT / "docs" / "phase-1-operating-contract.md",
    ROOT / "docs" / "production-readiness.md",
    ROOT / "docs" / "runbook.md",
    ROOT / "docs" / "security-governance.md",
    ROOT / "docs" / "testing-evaluation.md",
    ROOT / "chatgpt" / "README.md",
    ROOT / "chatgpt" / "mcp" / "README.md",
    ROOT / "mcp" / "README.md",
    ROOT / "chatgpt" / "workspace-agent-builder-prompt.md",
]


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


def role_allowlist(text: str) -> set[str]:
    require("## MCP allowlist" in text, "role contract missing MCP allowlist")
    section = text.split("## MCP allowlist", 1)[1]
    section = section.split("\n## ", 1)[0]
    return {token for token in re.findall(r"`([^`]+)`", section) if "." in token}


registry_source = json.loads((ROOT / "agents" / "registry.json").read_text())
registry = {record["agent_id"]: record for record in registry_source["agents"]}
require(set(registry) == set(EXPECTED), "Workspace Agent roster drifted from canonical 10-agent registry")
require("devils-advocate" not in registry, "Devil's Advocate must remain a shared Skill, not an agent")
require("message-ops" in registry, "Message Operations must remain the tenth registered agent")
require(__version__ == RELEASE, f"Workspace Agent release must be {RELEASE}")
require(f'version = "{RELEASE}"' in (ROOT / "pyproject.toml").read_text(), "Runtime/package version drifted")

shared = {item["capability"]: item for item in registry_source.get("shared_capabilities", [])}
require(set(shared) == {"mesh-devils-advocate"}, "Only Mesh Devil's Advocate is a Phase 1 external shared Skill")
challenge = shared["mesh-devils-advocate"]
require(challenge["deployment"] == "EXTERNAL_SHARED_SKILL", "Shared challenge deployment drifted")
require(set(challenge["consumers"]) == DA_CONSUMERS, "Shared challenge consumers drifted")
require(challenge["authority"] == "ADVISORY_ONLY", "Shared challenge authority drifted")
require(challenge["canonical_facts_modified"] is False, "Shared challenge cannot modify canonical facts")
require(challenge["external_action_included"] is False, "Shared challenge cannot execute external actions")
require(not (ROOT / "agents" / "devils-advocate.md").exists(), "Duplicate Devil's Advocate role card remains")
require(not (AGENTS / "devils-advocate.json").exists(), "Duplicate Devil's Advocate Workspace Agent remains")
require(not (SKILLS / "mesh-devils-advocate").exists(), "Duplicate local Devil's Advocate Skill remains")

contract = json.loads(MCP.read_text())
policy = WorkspaceAgentMCPPolicy.from_file(MCP)
require(contract["runtime_release"] == RELEASE, "MCP release drifted")
require(contract["transport"] == "LOCAL_STDIO", "MCP transport drifted")
require(policy.validate_runtime_bindings() == [], "MCP runtime binding is unresolved")
allowlists = contract["agent_tool_allowlists"]
require(set(allowlists) == set(EXPECTED), "MCP principal roster drifted")
require(set(contract["human_tool_allowlist"]) == HUMAN_ONLY, "Human-only MCP allowlist drifted")
for agent_id, allowed in allowlists.items():
    require(HUMAN_ONLY.isdisjoint(allowed), f"{agent_id}: human-only tool leaked into agent catalog")
require("task.verify" in allowlists["cos"], "CoS verifier operation missing")
for agent_id, allowed in allowlists.items():
    if agent_id != "cos":
        require("task.verify" not in allowed, f"{agent_id}: unauthorized verifier capability")

skill_dirs = {path.name for path in SKILLS.iterdir() if path.is_dir()}
require(skill_dirs == {item[2] for item in EXPECTED.values()}, "Repository-local role Skill roster drifted")
manifest_paths = sorted(AGENTS.glob("*.json"))
require(len(manifest_paths) == 10, "Workspace Agent package must contain exactly 10 manifests")

for agent_id, (display_name, parent_id, skill_name) in EXPECTED.items():
    record = registry[agent_id]
    skill_dir = SKILLS / skill_name
    for relative in ("SKILL.md", "agents/openai.yaml", "references/role-contract.md", "references/production-readiness.md"):
        require((skill_dir / relative).is_file(), f"{agent_id}: missing Skill resource {relative}")
    frontmatter = parse_frontmatter((skill_dir / "SKILL.md").read_text())
    require(frontmatter.get("name") == skill_name, f"{agent_id}: Skill name drifted")
    require(len(frontmatter.get("description", "")) >= 80, f"{agent_id}: Skill description too thin")
    readiness = (skill_dir / "references" / "production-readiness.md").read_text()
    require("10 Workspace Agents" in readiness, f"{agent_id}: production-readiness roster drifted")
    require("all 11 Workspace Agents" not in readiness, f"{agent_id}: superseded 11-agent wording remains current")
    require("task.complete" in readiness and "task.verify" in readiness, f"{agent_id}: completion/verification contract missing")
    require("MESH_COS_MCP_SERVER_URL" not in readiness, f"{agent_id}: remote MCP dependency reintroduced")

    role = (skill_dir / "references" / "role-contract.md").read_text()
    require(f"Repository release:** `{RELEASE}`" in role, f"{agent_id}: role-contract release drifted")
    require(role_allowlist(role) == set(allowlists[agent_id]), f"{agent_id}: role-contract MCP allowlist drifted")
    require(HUMAN_ONLY.isdisjoint(role_allowlist(role)), f"{agent_id}: human-only operation in role contract")

    manifest_path = AGENTS / f"{agent_id}.json"
    require(manifest_path.is_file(), f"{agent_id}: Workspace Agent manifest missing")
    manifest = json.loads(manifest_path.read_text())
    require(manifest["display_name"] == display_name, f"{agent_id}: display name drifted")
    require(manifest["parent_agent_id"] == parent_id, f"{agent_id}: parent drifted")
    require(manifest["repository_release"] == RELEASE, f"{agent_id}: repository release drifted")
    require(manifest["implementation_version"] == record["version"], f"{agent_id}: implementation version drifted")
    require(manifest["mcp"]["env"]["MESH_COS_AGENT_ID"] == agent_id, f"{agent_id}: immutable MCP identity binding drifted")
    require(manifest["mcp"]["allowed_tools"] == allowlists[agent_id], f"{agent_id}: manifest MCP allowlist drifted")
    require(manifest["builder_configuration"]["mcp_allowed_tools"] == allowlists[agent_id], f"{agent_id}: builder MCP allowlist drifted")
    require(manifest["write_action_policy"]["default"] == "ALWAYS_ASK", f"{agent_id}: write approval weakened")
    expected_shared = ["mesh-devils-advocate"] if agent_id in DA_CONSUMERS else []
    require(manifest.get("shared_skills", []) == expected_shared, f"{agent_id}: shared Skill projection drifted")
    require(manifest["builder_configuration"].get("shared_skills", []) == expected_shared, f"{agent_id}: builder shared Skill projection drifted")
    require(("mesh-devils-advocate" in record.get("skills", [])) is (agent_id in DA_CONSUMERS), f"{agent_id}: Devil's Advocate entitlement drifted")

package = json.loads((ROOT / "mcp" / "package.json").read_text())
package_lock = json.loads((ROOT / "mcp" / "package-lock.json").read_text())
require(package["version"] == RELEASE, "MCP package version drifted")
require(package_lock["version"] == RELEASE, "MCP package-lock version drifted")
require(package_lock["packages"][""]["version"] == RELEASE, "MCP lock root version drifted")

for path in CURRENT_DOCS:
    text = path.read_text()
    lower = text.lower()
    require("all 11 workspace agents" not in lower, f"{path.relative_to(ROOT)}: stale 11-agent current-state wording")
    require("9-agent roster" not in lower and "exactly 9" not in lower, f"{path.relative_to(ROOT)}: stale 9-agent current-state wording")

print("ChatGPT Workspace Agent package, authority, roster, lifecycle, and documentation drift check: OK")
