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
RELEASE = "3.0.0"

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
}
SHARED_CHALLENGE_CONSUMERS = {"cos", "cro"}
SHARED_MESSAGE_CONSUMERS = {"cos", "cro", "cmo"}

REQUIRED_MCP_TOOLS = {
    "registry.get_agent", "registry.list_agents", "task.intake", "task.get", "task.list",
    "task.decompose", "task.transition", "task.check_in", "task.complete", "task.reassign", "task.remediate_stall",
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


def _raw_registry_source() -> dict:
    return json.loads((ROOT / "agents" / "registry.json").read_text())


def _raw_registry() -> dict[str, dict]:
    return {record["agent_id"]: record for record in _raw_registry_source()["agents"]}


def _expected_shared(agent_id: str) -> list[str]:
    result: list[str] = []
    if agent_id in SHARED_CHALLENGE_CONSUMERS:
        result.append("mesh-devils-advocate")
    if agent_id in SHARED_MESSAGE_CONSUMERS:
        result.append("mesh-message-operations")
    return result


def test_all_phase1_agents_have_chatgpt_skill_and_builder_config() -> None:
    registry = load_registry()
    assert set(EXPECTED) == set(registry)
    assert len(registry) == 9
    assert "devils-advocate" not in registry
    assert "message-ops" not in registry
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

    for removed in ("devils-advocate", "message-ops"):
        assert not (AGENTS / f"{removed}.json").exists()
        assert not (ROOT / "agents" / f"{removed}.md").exists()
    assert not (SKILLS / "mesh-devils-advocate").exists()
    assert not (SKILLS / "mesh-message-operations").exists()


def test_shared_capabilities_are_external_and_bounded() -> None:
    capabilities = {item["capability"]: item for item in _raw_registry_source()["shared_capabilities"]}
    challenge = capabilities["mesh-devils-advocate"]
    assert challenge["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert set(challenge["consumers"]) == SHARED_CHALLENGE_CONSUMERS
    assert challenge["authority"] == "ADVISORY_ONLY"
    assert challenge["canonical_facts_modified"] is False
    assert challenge["external_action_included"] is False

    message = capabilities["mesh-message-operations"]
    assert message["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert set(message["consumers"]) == SHARED_MESSAGE_CONSUMERS
    assert message["authority"] == "APPROVAL_BOUND_EXECUTION_ONLY"
    assert message["creates_strategy_or_copy"] is False
    assert message["approval_may_be_inferred_or_broadened"] is False
    assert message["preview_is_approval"] is False
    assert message["canonical_commercial_state_modified"] is False
    assert message["canonical_consent_or_legal_state_modified"] is False
    assert message["requires_per_message_approval"] is True
    assert message["requires_documented_connector_action"] is True
    assert message["requires_idempotency"] is True
    assert message["requires_post_send_verification"] is True

    registry = _raw_registry()
    for agent_id, record in registry.items():
        assert ("mesh-devils-advocate" in record.get("skills", [])) is (agent_id in SHARED_CHALLENGE_CONSUMERS)
        assert ("mesh-message-operations" in record.get("skills", [])) is (agent_id in SHARED_MESSAGE_CONSUMERS)


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


def test_every_agent_config_preserves_registry_authority_governance_and_shared_projection() -> None:
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
        assert config["repository_release"] == RELEASE
        assert config.get("shared_skills", []) == _expected_shared(agent_id)
        assert config["builder_configuration"].get("shared_skills", []) == _expected_shared(agent_id)
        assert config["mcp"]["transport"] == "LOCAL_STDIO"
        assert config["mcp"]["command"] == "node"
        assert config["mcp"]["args"] == ["mcp/dist/index.js"]
        assert config["mcp"]["env"]["MESH_COS_AGENT_ID"] == agent_id
        assert config["mcp"]["env"]["MESH_COS_LEDGER_PATH"]
        assert "server_url_env" not in config["mcp"]


def test_builder_configs_have_least_privilege_tool_allowlists() -> None:
    contract = json.loads(MCP.read_text())
    contract_allowlists = contract["agent_tool_allowlists"]
    assert set(contract_allowlists) == set(EXPECTED)
    assert "devils-advocate" not in contract_allowlists
    assert "message-ops" not in contract_allowlists
    for agent_id in EXPECTED:
        config = _config(agent_id)
        allowlist = config["mcp"]["allowed_tools"]
        assert allowlist
        assert len(allowlist) == len(set(allowlist))
        assert set(allowlist) <= REQUIRED_MCP_TOOLS
        assert allowlist == contract_allowlists[agent_id]
        assert config["builder_configuration"]["mcp_allowed_tools"] == allowlist
        assert "registry.get_agent" in allowlist
        assert "governance.record_event" in allowlist
        if agent_id == "cos":
            assert {"task.decompose", "task.reassign", "conflict.decide", "agentops.recommend", "task.complete"} <= set(allowlist)
        else:
            assert "task.reassign" not in allowlist
        if agent_id in SHARED_CHALLENGE_CONSUMERS | SHARED_MESSAGE_CONSUMERS:
            assert "skills.invoke_governed" in allowlist
    assert "approval.record_decision" not in contract_allowlists["cos"]
    assert "reliability.human_override" not in contract_allowlists["cos"]
    assert set(contract["human_tool_allowlist"]) == {"approval.record_decision", "reliability.human_override"}


def test_mcp_contract_and_server_side_policy_fail_closed() -> None:
    contract = json.loads(MCP.read_text())
    assert contract["runtime_release"] == RELEASE
    assert contract["transport"] == "LOCAL_STDIO"
    assert contract["serialized_runtime"] == "mesh_cos.mcp_runtime.MCPRuntime"
    assert contract["security"]["deny_by_default"] is True
    assert contract["security"]["approval_fail_closed"] is True
    assert contract["security"]["server_derived_agent_identity"] is True
    assert contract["security"]["human_principal_required_for_human_tools"] is True
    assert contract["security"]["client_supplied_code_execution"] is False
    assert contract["governance"]["canonical_first_write_order"] is True
    tools = {tool["name"]: tool for tool in contract["tools"]}
    assert REQUIRED_MCP_TOOLS <= set(tools)
    for name, tool in tools.items():
        assert tool["authority_enforced"] is True, name
        assert tool["runtime_binding"], name
        if not tool["read_only"]:
            assert tool["audit_required"] is True, name

    policy = WorkspaceAgentMCPPolicy.from_file(MCP)
    assert policy.authorize("cos", "task.reassign")["name"] == "task.reassign"
    assert policy.authorize_human("approval.record_decision")["read_only"] is False
    for denied in (
        ("cro", "task.reassign"),
        ("message-ops", "approval.get"),
        ("devils-advocate", "task.get"),
        ("unknown-agent", "task.get"),
        ("cos", "unknown.tool"),
        ("cos", "approval.record_decision"),
    ):
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
        assert config["channels"]["api"]["enabled"] is True
        assert not re.search(r"\bv\d+(?:\.\d+)*\b", config["display_name"], re.I)


def test_risky_app_and_message_execution_boundaries_remain_fail_closed() -> None:
    cmo = _config("cmo")
    cro = _config("cro")
    cos = _config("cos")
    vp = _config("vp-content")
    assert any("no autonomous public posting" in rule for rule in cmo["connector_action_constraints"])
    assert any("public publishing remains human-gated" in rule for rule in vp["connector_action_constraints"])
    assert any("research/enrichment only" in rule for rule in cro["connector_action_constraints"])
    assert vp.get("shared_skills", []) == []
    for config in (cos, cro, cmo):
        assert any("Mesh Message Operations" in rule for rule in config["connector_action_constraints"])
        assert config["write_action_policy"]["default"] == "ALWAYS_ASK"
    answer_desk = _config("answer-desk")
    assert answer_desk["channels"]["slack"]["enabled"] is False
    assert answer_desk["channels"]["slack"]["channel_id"] is None


def test_workspace_agent_builder_handoff_prompt_is_exact_and_complete() -> None:
    text = BUILDER_PROMPT.read_text()
    for token in (
        "Workspace Agent Builder", "9 agents", "v3.0.0", "Mesh Devil's Advocate", "Mesh Message Operations",
        "shared Skill", "mesh-cos-mcp", "local stdio", "mcp/dist/index.js", "MESH_COS_AGENT_ID",
        "MESH_COS_LEDGER_PATH", "TaskLedger", "L4", "L5", "Always ask", "Connector Action Constraints",
        "Chief of Staff", "AgentOps Controller", "Answer & Decision Desk", "Consultant Network Steward",
        "negative authority test", "missing-evidence test", "human-approval spoofing test",
        "completion-versus-verification test", "replay-safety test",
    ):
        assert token in text
    assert "MESH_COS_MCP_SERVER_URL" not in text
    roster = text.split("Create exactly these", 1)[-1].split("For each agent", 1)[0]
    assert "Message Operations" not in roster


def test_no_workspace_agent_config_embeds_release_versions_in_role_names() -> None:
    for path in AGENTS.glob("*.json"):
        config = json.loads(path.read_text())
        assert not re.search(r"\bv\d+(?:\.\d+)*\b", config["display_name"], re.IGNORECASE)
