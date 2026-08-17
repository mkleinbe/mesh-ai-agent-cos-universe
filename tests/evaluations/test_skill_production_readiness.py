from __future__ import annotations

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
    "mesh-devils-advocate",
    "mesh-message-operations",
}


def test_every_role_skill_contains_production_readiness_contract() -> None:
    assert {path.name for path in SKILLS.iterdir() if path.is_dir()} == EXPECTED
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


def test_builder_prompt_requires_skill_production_readiness_contract() -> None:
    text = (ROOT / "chatgpt" / "workspace-agent-builder-prompt.md").read_text()
    assert "references/production-readiness.md" in text
    assert "100% branch-aware" in text
    assert "production preflight" in text.lower()
    assert "task.complete" in text
    assert "task.verify" in text
