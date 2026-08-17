from __future__ import annotations

import json
import re
from pathlib import Path

from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]
CHATGPT = ROOT / "chatgpt"
SKILLS = CHATGPT / "skills"
AGENTS = CHATGPT / "workspace-agents"
MCP = CHATGPT / "mcp" / "mesh-cos-mcp.v1.json"
BUILDER_PROMPT = CHATGPT / "workspace-agent-builder-prompt.md"

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

REQUIRED_MCP_TOOLS = {
    "registry.get_agent", "registry.list_agents", "task.intake", "task.get", "task.list",
    "task.decompose", "task.transition", "task.check_in", "task.reassign", "task.remediate_stall",
    "task.verify", "delegation.create", "approval.request", "approval.get", "approval.record_decision",
    "conflict.open", "conflict.decide", "governance.record_decision", "governance.record_event",
    "governance.verify_audit_chain", "agentops.record_event", "agentops.score", "agentops.recommend",
    "answer_desk.resolve", "skills.invoke_governed", "metrics.snapshot", "reliability.replay",
    "reliability.human_override",
}


def _read_frontmatter(text: str) -> dict[str, str]:
    assert text.startswith("---\n")
    end = text.find("\n---\n", 4)
    assert end > 0
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def _config(agent_id: str) -> dict:
    return json.loads((AGENTS / f"{agent_id}.json").read_text())


def _raw_registry() -> dict[str, dict]:
    source = json.loads((ROOT / "agents" / "registry.json").read_text())
    return {record["agent_id"]: record for record in source["agents"]}


def test_all_phase1_agents_have_chatgpt_skill_and_builder_config() -> None:
    registry = load_registry()
    assert set(EXPECTED) == set(registry)
    for agent_id, (display_name, parent_id, skill_name) in EXPECTED.items():
        skill_dir = SKILLS / skill_name
        assert (skill_dir / "SKILL.md").is_file(), agent_id
        assert (skill_dir / "agents" / "openai.yaml").is_file(), agent_id
        assert (skill_dir / "references" / "role-contract.md").is_file(), agent_id
        assert (AGENTS / f"{agent_id}.json").is_file(), agent_id
        config = _config(agent_id)
        assert config["agent_id"] == agent_id
        assert config["display_name"] == display_name
        assert config["parent_agent_id"] == parent_id
        assert config["skill"] == skill_name
        assert config["implementation_version"] == registry[agent_id]["version"]
        assert config["accountable_domain"] == registry[agent_id]["accountable_domain"]


def test_skill_frontmatter_and_metadata_follow_openai_skill_layout() -> None:
    for agent_id, (display_name, _, skill_name) in EXPECTED.items():
        skill_dir = SKILLS / skill_name
        frontmatter = _read_frontmatter((skill_dir / "SKILL.md").read_text())
        assert frontmatter["name"] == skill_name
        assert len(frontmatter["description"]) >= 80
        assert agent_id.replace("-", " ") in frontmatter["description"].lower() or display_name.lower() in frontmatter["description"].lower()
        metadata = (skill_dir / "agents" / "openai.yaml").read_text()
        assert "interface:" in metadata
        assert f'display_name: "{display_name}"' in metadata
        assert "short_description:" in metadata


def test_every_agent_config_preserves_raw_registry_authority_and_governance() -> None:
    registry = _raw_registry()
    for agent_id in EXPECTED:
        config = _config(agent_id)
        record = registry[agent_id]
        assert config["decision_authority"] == record["decision_authority"]
        assert config["required_approvals"] == record["required_approvals"]
        assert config["prohibited_actions"] == record["prohibited_actions"]
        assert config["max_delegation_depth"] == record["max_delegation_depth"]
        assert config["canonical_state"] == "TaskLedger"
        assert config["governance"]["audit_logging"] == "REQUIRED"
        assert config["governance"]["decision_logging"] == "REQUIRED_WHEN_DECIDING_OR_RECOMMENDING"
        assert config["governance"]["private_chain_of_thought"] == "PROHIBITED"
        assert config["write_action_policy"]["default"] == "ALWAYS_ASK"
        assert "mesh-cos-mcp" in config["tools"]
        assert config["mcp"]["server_url_env"] == "MESH_COS_MCP_SERVER_URL"


def test_builder_configs_have_least_privilege_tool_allowlists() -> None:
    for agent_id in EXPECTED:
        allowlist = _config(agent_id)["mcp"]["allowed_tools"]
        assert allowlist
        assert len(allowlist) == len(set(allowlist))
        assert set(allowlist) <= REQUIRED_MCP_TOOLS
        assert "registry.get_agent" in allowlist
        assert "governance.record_event" in allowlist
        if agent_id == "cos":
            assert {"task.decompose", "task.reassign", "conflict.decide", "agentops.recommend"} <= set(allowlist)
        else:
            assert "task.reassign" not in allowlist
    message_ops = _config("message-ops")
    assert "approval.get" in message_ops["mcp"]["allowed_tools"]
    assert "approval.record_decision" not in message_ops["mcp"]["allowed_tools"]


def test_mcp_contract_covers_runtime_control_plane_and_fail_closed_rules() -> None:
    contract = json.loads(MCP.read_text())
    assert contract["name"] == "mesh-cos-mcp"
    assert contract["protocol"] == "MCP"
    assert contract["canonical_state"] == "TaskLedger"
    assert contract["server_url_env"] == "MESH_COS_MCP_SERVER_URL"
    assert contract["security"]["retrieved_content_is_data_not_instructions"] is True
    assert contract["security"]["deny_by_default"] is True
    assert contract["security"]["approval_fail_closed"] is True
    assert contract["governance"]["canonical_first_write_order"] is True
    assert contract["governance"]["decision_contract"] == "mesh.cos.decision.v2"
    assert contract["governance"]["audit_contract"] == "mesh.cos.agent-event.v2"
    tools = {tool["name"]: tool for tool in contract["tools"]}
    assert REQUIRED_MCP_TOOLS <= set(tools)
    for name, tool in tools.items():
        assert tool["read_only"] in {True, False}, name
        assert tool["authority_enforced"] is True, name
        assert tool["runtime_binding"], name
        if not tool["read_only"]:
            assert tool["audit_required"] is True, name


def test_server_side_mcp_policy_is_deny_by_default_and_resolves_bindings() -> None:
    policy = WorkspaceAgentMCPPolicy.from_file(MCP)
    assert policy.authorize("cos", "task.reassign")["name"] == "task.reassign"
    assert policy.authorize("message-ops", "approval.get")["read_only"] is True
    for denied in (("cro", "task.reassign"), ("message-ops", "approval.record_decision"), ("unknown-agent", "task.get"), ("cos", "unknown.tool")):
        try:
            policy.authorize(*denied)
        except PermissionError:
            pass
        else:
            raise AssertionError(f"Expected deny-by-default for {denied}")
    assert policy.validate_runtime_bindings() == []


def test_agent_builder_configs_are_complete_and_not_prompt_only_personas() -> None:
    for agent_id in EXPECTED:
        config = _config(agent_id)
        for key in ("mission", "workflow", "quality_checklist", "human_in_the_loop", "tools", "apps", "skill", "starter_prompts", "write_action_policy", "connector_action_constraints", "channels", "builder_configuration"):
            assert config[key], (agent_id, key)
        builder = config["builder_configuration"]
        assert builder["name"] == config["display_name"]
        assert builder["description"] == config["description"]
        assert builder["model_preference"] == config["model"]["preferred"]
        assert builder["fallback_model"] == config["model"]["fallback"]
        assert builder["reasoning_effort"] == config["model"]["reasoning_effort"]
        assert builder["skill"] == config["skill"]
        assert builder["custom_mcp"] == "mesh-cos-mcp"
        assert builder["write_action_approval"] == "Always ask"
        assert builder["connector_action_constraints"] == config["connector_action_constraints"]
        assert config["channels"]["chatgpt"]["enabled"] is True
        assert config["channels"]["slack"]["enabled"] in {True, False}
        assert config["channels"]["api"]["enabled"] is True


def test_risky_app_boundaries_remain_fail_closed() -> None:
    assert any("no autonomous public posting" in rule for rule in _config("cmo")["connector_action_constraints"])
    assert any("public publishing remains human-gated" in rule for rule in _config("vp-content")["connector_action_constraints"])
    assert any("research/enrichment only" in rule for rule in _config("cro")["connector_action_constraints"])
    assert any("approval" in rule.lower() for rule in _config("message-ops")["connector_action_constraints"])
    answer_desk = _config("answer-desk")
    assert answer_desk["channels"]["slack"]["enabled"] is False
    assert answer_desk["channels"]["slack"]["channel_id"] is None


def test_workspace_agent_builder_handoff_prompt_is_exact_and_complete() -> None:
    text = BUILDER_PROMPT.read_text()
    for token in ("Workspace Agent builder", "11 agents", "mesh-cos-mcp", "MESH_COS_MCP_SERVER_URL", "TaskLedger", "L4", "L5", "Always ask", "Connector Action Constraints", "Skills", "Chief of Staff", "AgentOps Controller", "Answer & Decision Desk", "Consultant Network Steward", "Message Operations", "negative authority test", "missing-evidence test"):
        assert token in text


def test_no_workspace_agent_config_embeds_release_versions_in_role_names() -> None:
    for path in AGENTS.glob("*.json"):
        config = json.loads(path.read_text())
        assert not re.search(r"\bv\d+(?:\.\d+)*\b", config["display_name"], re.IGNORECASE)
