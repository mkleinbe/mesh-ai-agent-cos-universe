from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v452_release_identity_remains_preserved_as_history() -> None:
    readme = (ROOT / "README.md").read_text()
    changelog = (ROOT / "CHANGELOG-v4.5.2.md").read_text()
    release_doc = (ROOT / "docs" / "release-v4.5.2-release-state-finalization.md").read_text()
    assert "## v4.5.2 CFO Financial Analysis Release State Finalization" in readme
    assert "# Changelog v4.5.2" in changelog
    assert "# v4.5.2 CFO Financial Analysis Release State Finalization" in release_doc


def test_v452_release_contract_is_documentation_only() -> None:
    text = (ROOT / "docs" / "release-v4.5.2-release-state-finalization.md").read_text()
    for token in (
        "No CFO behavior",
        "CFO implementation: `1.1.0`, unchanged",
        "Canonical runtime contract: `4.0.0`, unchanged",
        "Production QNAP deployment: `4.4.0`, unchanged",
        "No QNAP deployment is required or authorized",
    ):
        assert token in text


def test_v452_release_workflow_is_historical_manual_verification_only() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.5.2.yml").read_text()
    assert "v4.5.2 CFO Financial Analysis Release State Finalization" in workflow
    assert "workflow_dispatch:" in workflow
    assert "branches: [main]" not in workflow
    assert "gh release create" not in workflow


def test_current_release_is_later_than_v452_without_rewriting_history() -> None:
    combined = (ROOT / "README.md").read_text()[:5000] + (ROOT / "RELEASE.md").read_text()[:5000]
    assert "v4.6.0 CFO Zero-Defect Execution Remediation" in combined
    assert "4.0.0" in combined
    assert "4.4.0" in combined
