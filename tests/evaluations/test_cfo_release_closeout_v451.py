from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_current_repository_release_pointers_are_v451() -> None:
    readme = (ROOT / "README.md").read_text()
    release = (ROOT / "RELEASE.md").read_text()
    security = (ROOT / "SECURITY.md").read_text()

    assert "v4.5.1 CFO Financial Analysis Release Closeout" in readme
    assert "# v4.5.1 CFO Financial Analysis Release Closeout" in release
    assert "v4.5.1 CFO Financial Analysis Release Closeout" in security


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


def test_v451_patch_is_documentation_only_and_preserves_runtime_boundaries() -> None:
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
    assert "Do not alter CFO implementation version `1.1.0`" in material_turn
    assert "Do not alter canonical runtime `4.0.0` or QNAP production `4.4.0`" in material_turn


def test_v451_release_workflow_targets_v451_after_full_verification() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.5.1.yml").read_text()
    assert "v4.5.1 CFO Financial Analysis Release Closeout" in workflow
    assert "pytest -q tests/evaluations/test_cfo_financial_analysis_v450.py" in workflow
    assert "pytest -q tests/evaluations/test_cfo_release_closeout_v451.py" in workflow
    assert "gh release create v4.5.1" in workflow
    assert '--target "$GITHUB_SHA"' in workflow
    assert "docs/release-v4.5.1-release-closeout.md" in workflow
