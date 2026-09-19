from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v4111_skill_bundle_declares_exact_changed_skills() -> None:
    script = (ROOT / "scripts" / "build-chatgpt-skill-bundle-v4.11.1.sh").read_text(encoding="utf-8")
    for skill in ("mesh-chief-of-staff", "mesh-cro", "mesh-coo", "mesh-cfo"):
        assert skill in script
    for unchanged in ("mesh-agentops-controller", "mesh-cmo", "mesh-answer-decision-desk"):
        assert unchanged not in script
    assert "VERSION=4.11.1" in script


def test_v4111_release_workflow_builds_and_attaches_skill_bundle() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.11.1.yml").read_text(encoding="utf-8")
    assert "build-chatgpt-skill-bundle-v4.11.1.sh" in workflow
    assert "mesh-cos-chatgpt-skills-v4.11.1.zip" in workflow
    assert "mesh-cos-chatgpt-skills-v4.11.1.zip.sha256" in workflow
    assert "gh release create v4.11.1" in workflow
    assert "--target \"$GITHUB_SHA\"" in workflow


def test_v4110_historical_publisher_is_frozen() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.11.0.yml").read_text(encoding="utf-8")
    assert "github.sha == '2e7ff513e5e1da1c9520a2d2abc7510f6a83a4c5'" in workflow


def test_v4111_bundle_manifest_documents_human_install_boundary() -> None:
    doc = (ROOT / "docs" / "skills-v4.11.1.md").read_text(encoding="utf-8")
    assert "four changed ChatGPT Skills" in doc
    assert "human-controlled" in doc
    assert "mesh-chief-of-staff" in doc
    assert "mesh-cro" in doc
    assert "mesh-coo" in doc
    assert "mesh-cfo" in doc
