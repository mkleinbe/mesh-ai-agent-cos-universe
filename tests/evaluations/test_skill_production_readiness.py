from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "chatgpt" / "skills"
EXPECTED = {
    "mesh-chief-of-staff",
    "mesh-agentops-controller",
    "mesh-answer-decision-desk",
    "mesh-cro",
    "mesh-cfo",
    "mesh-coo",
    "mesh-consultant-network-steward",
    "mesh-cmo",
    "mesh-vp-content",
    "mesh-message-operations",
}


def test_every_repository_local_role_skill_contains_production_readiness_contract() -> None:
    assert {path.name for path in SKILLS.iterdir() if path.is_dir()} == EXPECTED
    assert not (SKILLS / "mesh-devils-advocate").exists()
    for name in EXPECTED:
        text = (SKILLS / name / "references" / "production-readiness.md").read_text()
        for token in (
            "ProductionPreflight",
            "TaskLedger",
            "task.complete",
            "task.verify",
            "approval.record_decision",
            "reliability.human_override",
            "server-registered replay executor",
        ):
            assert token in text, (name, token)


def test_shared_mesh_devils_advocate_is_external_not_duplicated_role_skill() -> None:
    source = json.loads((ROOT / "agents" / "registry.json").read_text())
    shared = {item["capability"]: item for item in source["shared_capabilities"]}
    challenge = shared["mesh-devils-advocate"]
    assert challenge["deployment"] == "EXTERNAL_SHARED_SKILL"
    assert set(challenge["consumers"]) == {"cos", "cro"}
    assert challenge["authority"] == "ADVISORY_ONLY"
    assert challenge["canonical_facts_modified"] is False
    assert challenge["external_action_included"] is False


def test_message_operations_role_skill_is_local_and_registered() -> None:
    source = json.loads((ROOT / "agents" / "registry.json").read_text())
    shared = {item["capability"]: item for item in source["shared_capabilities"]}
    records = {item["agent_id"]: item for item in source["agents"]}
    assert "mesh-message-operations" not in shared
    assert records["message-ops"]["skills"] == ["mesh-message-operations"]
    assert (SKILLS / "mesh-message-operations" / "SKILL.md").is_file()
    assert (SKILLS / "mesh-message-operations" / "references" / "role-contract.md").is_file()
    assert (SKILLS / "mesh-message-operations" / "references" / "production-readiness.md").is_file()


def test_builder_prompt_requires_skill_production_readiness_contract() -> None:
    text = (ROOT / "chatgpt" / "workspace-agent-builder-prompt.md").read_text()
    assert "references/production-readiness.md" in text
    assert "100% branch-aware" in text
    assert "production preflight" in text.lower()
    assert "task.complete" in text
    assert "task.verify" in text
    assert "Mesh Devil's Advocate" in text
    assert "Message Operations" in text
    assert "shared Skill" in text
