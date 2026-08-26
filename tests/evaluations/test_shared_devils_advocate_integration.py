from __future__ import annotations

import json
from pathlib import Path

from mesh_cos import __version__
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[2]


def test_devils_advocate_is_shared_capability_not_workspace_agent() -> None:
    registry = load_registry()
    assert "devils-advocate" not in registry
    assert "message-ops" in registry
    assert len(registry) == 10
    assert "mesh-devils-advocate" in registry["cos"]["skills"]
    assert "mesh-devils-advocate" in registry["cro"]["skills"]
    assert not (ROOT / "agents" / "devils-advocate.md").exists()
    assert not (ROOT / "chatgpt" / "workspace-agents" / "devils-advocate.json").exists()
    assert not (ROOT / "chatgpt" / "skills" / "mesh-devils-advocate").exists()


def test_shared_challenge_contract_preserves_owner_authority() -> None:
    source = json.loads((ROOT / "agents" / "registry.json").read_text())
    shared = {item["capability"]: item for item in source.get("shared_capabilities", [])}
    challenge = shared["mesh-devils-advocate"]
    assert challenge["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert challenge["consumers"] == ["cos", "cro"]
    assert challenge["authority"] == "ADVISORY_ONLY"
    assert challenge["canonical_facts_modified"] is False
    assert challenge["external_action_included"] is False
    assert challenge["request_contract"] == "mesh.devils-advocate.challenge-request.v1"
    assert challenge["response_contract"] == "mesh.devils-advocate.challenge-packet.v1"
    registry = load_registry()
    assert "request_devils_advocate_review" in registry["cro"]["permitted_actions"]


def test_mcp_projects_shared_challenge_without_agent_principal() -> None:
    contract = json.loads((ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json").read_text())
    allowlists = contract["agent_tool_allowlists"]
    assert "devils-advocate" not in allowlists
    assert "message-ops" in allowlists
    assert "skills.invoke_governed" in allowlists["cos"]
    assert "skills.invoke_governed" in allowlists["cro"]


def test_workspace_manifests_attach_shared_skill_only_to_governed_consumers() -> None:
    expected_shared = {"cos": ["mesh-devils-advocate"], "cro": ["mesh-devils-advocate"]}
    for agent_id, expected in expected_shared.items():
        manifest = json.loads(
            (ROOT / "chatgpt" / "workspace-agents" / f"{agent_id}.json").read_text()
        )
        assert manifest["shared_skills"] == expected
        assert manifest["builder_configuration"]["shared_skills"] == expected
    for path in (ROOT / "chatgpt" / "workspace-agents").glob("*.json"):
        if path.stem in {"cos", "cro"}:
            continue
        manifest = json.loads(path.read_text())
        assert "mesh-devils-advocate" not in manifest.get("shared_skills", [])


def test_qnap_release_preserves_v4_authority_contract() -> None:
    assert __version__ == "4.0.0"
    assert 'version = "4.0.0"' in (ROOT / "pyproject.toml").read_text()
    release_workflow = (
        ROOT / ".github" / "workflows" / "release-production-readiness.yml"
    ).read_text()
    assert "TAG: v4.1.13" in release_workflow
    assert '--title "v4.1.13 Slack Approver Bootstrap"' in release_workflow
    release_notes = (ROOT / "RELEASE.md").read_text()
    assert "v4.1.13 Slack Approver Bootstrap" in release_notes
    assert "canonical Phase 1 authority/runtime contract remains **`4.0.0`**" in release_notes
    assert "Mesh Devil's Advocate" in release_notes
    assert "Message Operations" in release_notes
