from __future__ import annotations

import json
from pathlib import Path

from mesh_cos import __version__

ROOT = Path(__file__).resolve().parents[2]


def test_shared_devils_advocate_is_not_registered_agent() -> None:
    registry = json.loads((ROOT / "config" / "agent-registry.json").read_text())
    agent_ids = {agent["agent_id"] for agent in registry["agents"]}
    assert len(agent_ids) == 10
    assert "devils-advocate" not in agent_ids
    assert "message-ops" in agent_ids


def test_shared_devils_advocate_is_external_advisory_skill() -> None:
    registry = json.loads((ROOT / "config" / "agent-registry.json").read_text())
    shared = registry["shared_skills"]["mesh-devils-advocate"]
    assert shared["implementation"] == "EXTERNAL_SHARED_SKILL"
    assert shared["authority"] == "ADVISORY_ONLY"
    assert shared["can_own_tasks"] is False
    assert shared["can_execute_external_actions"] is False
    assert set(shared["authorized_agents"]) == {"cos", "cro"}


def test_workspace_agents_project_shared_skill_only_where_authorized() -> None:
    expected_shared = {
        "cos": ["mesh-devils-advocate"],
        "cro": ["mesh-devils-advocate"],
    }
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
