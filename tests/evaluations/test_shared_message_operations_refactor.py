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


def test_message_operations_is_shared_capability_not_agent_principal() -> None:
    registry = load_registry(REGISTRY)
    assert len(registry) == 9
    assert "message-ops" not in registry
    assert not ROLE_CARD.exists()
    assert not (WORKSPACE_AGENTS / "message-ops.json").exists()
    assert not ROLE_SKILL.exists()


def test_shared_message_operations_contract_is_exact_and_least_privilege() -> None:
    raw = _raw_registry()
    capabilities = {item["capability"]: item for item in raw["shared_capabilities"]}
    capability = capabilities["mesh-message-operations"]
    assert capability["display_name"] == "Mesh Message Operations"
    assert capability["type"] == "shared_skill"
    assert capability["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert capability["consumers"] == ["cos", "cro", "cmo"]
    assert capability["authority"] == "APPROVAL_BOUND_EXECUTION_ONLY"
    assert capability["creates_strategy_or_copy"] is False
    assert capability["approval_may_be_inferred_or_broadened"] is False
    assert capability["preview_is_approval"] is False
    assert capability["canonical_commercial_state_modified"] is False
    assert capability["canonical_consent_or_legal_state_modified"] is False
    assert capability["requires_per_message_approval"] is True
    assert capability["requires_documented_connector_action"] is True
    assert capability["requires_idempotency"] is True
    assert capability["requires_post_send_verification"] is True
    assert capability["request_contract"] == "mesh.messaging.execution-request.v1"
    assert capability["response_contract"] == "mesh.messaging.execution-receipt.v1"


def test_only_cos_cro_cmo_receive_shared_message_operations_entitlement() -> None:
    registry = load_registry(REGISTRY)
    entitled = {agent_id for agent_id, record in registry.items() if "mesh-message-operations" in record["skills"]}
    assert entitled == {"cos", "cro", "cmo"}
    assert "mesh-message-operations" not in registry["vp-content"]["skills"]


def test_workspace_projection_is_nine_agents_and_shared_skill_attached_only_to_consumers() -> None:
    manifests = sorted(WORKSPACE_AGENTS.glob("*.json"))
    assert len(manifests) == 9
    seen = set()
    for path in manifests:
        manifest = json.loads(path.read_text())
        seen.add(manifest["agent_id"])
        assert manifest["repository_release"] == "3.0.0"
        shared = set(manifest.get("shared_skills", []))
        if manifest["agent_id"] in {"cos", "cro", "cmo"}:
            assert "mesh-message-operations" in shared
        else:
            assert "mesh-message-operations" not in shared
    assert "message-ops" not in seen


def test_mcp_has_no_message_ops_principal_and_consumers_retain_governed_skill_invocation() -> None:
    contract = json.loads(MCP.read_text())
    allowlists = contract["agent_tool_allowlists"]
    assert "message-ops" not in allowlists
    assert contract["runtime_release"] == "3.0.0"
    for agent_id in ("cos", "cro", "cmo"):
        assert "skills.invoke_governed" in allowlists[agent_id]


def test_release_identity_is_v3() -> None:
    assert __version__ == "3.0.0"
    assert 'version = "3.0.0"' in (ROOT / "pyproject.toml").read_text()
    assert '"version": "3.0.0"' in (ROOT / "mcp" / "package.json").read_text()
    release = (ROOT / "RELEASE.md").read_text()
    assert "v3.0.0" in release
    assert "Shared Mesh Message Operations" in release
