from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v451_release_identity_remains_preserved_as_history() -> None:
    readme = (ROOT / "README.md").read_text()
    changelog = (ROOT / "CHANGELOG-v4.5.1.md").read_text()
    release_doc = (ROOT / "docs" / "release-v4.5.1-release-closeout.md").read_text()
    assert "## v4.5.1 CFO Financial Analysis Release Closeout" in readme
    assert "# Changelog v4.5.1" in changelog
    assert "# v4.5.1 CFO Financial Analysis Release Closeout" in release_doc


def test_v450_verification_receipt_records_completed_release() -> None:
    receipt = (ROOT / "docs" / "verification-v4.5.0-cfo-financial-analysis.md").read_text()
    assert "**RELEASED**" in receipt
    assert "34148492601" in receipt
    assert "34148492715" in receipt
    assert "075eb8de04d6035a16ff2b6a24d2106ef8783b95" in receipt
    assert "semantic tag `v4.5.0`" in receipt
    assert "GitHub Release" in receipt
    assert "CFO implementation version: `1.1.0`" in receipt
    assert "Canonical Phase 1 runtime contract: `4.0.0`" in receipt
    assert "Production QNAP runtime: `4.4.0`, unchanged" in receipt


def test_v451_patch_history_preserves_runtime_boundaries() -> None:
    release_doc = (ROOT / "docs" / "release-v4.5.1-release-closeout.md").read_text()
    material_turn = (ROOT / "docs" / "material-turn-v4.5.1.md").read_text()
    for token in (
        "No CFO behavior",
        "CFO implementation: `1.1.0`, unchanged",
        "Canonical runtime contract: `4.0.0`, unchanged",
        "Production QNAP deployment: `4.4.0`, unchanged",
        "No QNAP deployment",
    ):
        assert token in release_doc
    assert "documentation and release-control patch" in material_turn


def test_v451_release_workflow_is_historical_manual_verification_only() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.5.1.yml").read_text()
    assert "v4.5.1 CFO Financial Analysis Release Closeout" in workflow
    assert "workflow_dispatch:" in workflow
    assert "branches: [main]" not in workflow
    assert "gh release create" not in workflow
