from __future__ import annotations

import json
from pathlib import Path

from mesh_cos import __version__
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "agents" / "registry.json"
WORKSPACE_AGENTS = ROOT / "chatgpt" / "workspace-agents"
ROLE_SKILL = ROOT / "chatgpt" / "skills" / "mesh-message-operations"
ROLE_CARD = ROOT / "agents" / "message-ops.md"
MCP = ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"


def _raw_registry() -> dict:
    return json.loads(REGISTRY.read_text())


def test_message_operations_is_registered_agent_principal() -> None:
    registry = load_registry(REGISTRY)
    assert len(registry) == 10
    assert "message-ops" in registry
    assert ROLE_CARD.exists()
    assert (WORKSPACE_AGENTS / "message-ops.json").exists()
    assert ROLE_SKILL.exists()
    assert registry["message-ops"]["parent_agent_id"] == "cos"
    assert registry["message-ops"]["max_delegation_depth"] == 0


def test_message_operations_contract_is_exact_and_least_privilege() -> None:
    raw = _raw_registry()
    capabilities = {item["capability"]: item for item in raw["shared_capabilities"]}
    assert "mesh-message-operations" not in capabilities
    registry = load_registry(REGISTRY)
    message = registry["message-ops"]
    assert message["display_name"] == "Message Operations"
    assert message["accountable_domain"] == "controlled approved communication execution"
    assert message["authoritative_sources"] == ["recorded approval state"]
    assert message["allowed_sources"] == ["approved outbound message artifact"]
    assert message["skills"] == ["mesh-message-operations"]
    assert set(message["permitted_actions"]) == {"prepare_execution", "execute_approved_message"}
    assert "consequential_external_send_without_approval" in message["prohibited_actions"]
    assert "fabricate_approval" in message["prohibited_actions"]
    assert "modify_approved_message_materially_without_reapproval" in message["prohibited_actions"]
    assert message["required_approvals"] == ["qualified human approval for consequential external send"]


def test_message_operations_entitlement_is_owned_only_by_message_ops_agent() -> None:
    registry = load_registry(REGISTRY)
    entitled = {agent_id for agent_id, record in registry.items() if "mesh-message-operations" in record["skills"]}
    assert entitled == {"message-ops"}
    assert "mesh-message-operations" not in registry["vp-content"]["skills"]
    assert "mesh-message-operations" not in registry["cos"]["skills"]
    assert "mesh-message-operations" not in registry["cro"]["skills"]
    assert "mesh-message-operations" not in registry["cmo"]["skills"]


def test_workspace_projection_is_ten_agents_with_message_ops_principal() -> None:
    manifests = sorted(WORKSPACE_AGENTS.glob("*.json"))
    assert len(manifests) == 10
    seen = set()
    for path in manifests:
        manifest = json.loads(path.read_text())
        seen.add(manifest["agent_id"])
        assert manifest["repository_release"] == "4.0.0"
        if manifest["agent_id"] == "message-ops":
            assert manifest["skill"] == "mesh-message-operations"
            assert manifest.get("shared_skills", []) == []
    assert "message-ops" in seen
    assert "devils-advocate" not in seen


def test_mcp_has_message_ops_principal_and_human_only_tools_remain_excluded() -> None:
    contract = json.loads(MCP.read_text())
    allowlists = contract["agent_tool_allowlists"]
    assert "message-ops" in allowlists
    assert contract["runtime_release"] == "4.0.0"
    message_allowlist = set(allowlists["message-ops"])
    assert {"approval.get", "governance.record_event", "registry.get_agent", "skills.invoke_governed", "task.complete", "task.get"} <= message_allowlist
    assert "task.verify" not in message_allowlist
    assert "approval.record_decision" not in message_allowlist
    assert "reliability.human_override" not in message_allowlist


def test_qnap_release_identity_preserves_v4_runtime() -> None:
    assert __version__ == "4.0.0"
    assert 'version = "4.0.0"' in (ROOT / "pyproject.toml").read_text()
    assert '"version": "4.0.0"' in (ROOT / "mcp" / "package.json").read_text()
    release = (ROOT / "RELEASE.md").read_text()
    assert "v4.1.8 MCP Contract Validation and Governed Skill Handoff" in release
    assert "canonical Mesh CoS Phase 1 authority/runtime contract remains **`4.0.0`**" in release
    assert "exactly 10 agents" in release
    assert "Message Operations" in release or "message-ops" in release
