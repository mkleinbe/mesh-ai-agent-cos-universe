from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _head(path: str, size: int = 2600) -> str:
    return (ROOT / path).read_text()[:size]


def _current_release_line(path: str) -> str:
    for line in (ROOT / path).read_text().splitlines()[:20]:
        if "current repository release" in line.lower():
            return line
    raise AssertionError(f"{path} does not declare a current repository release")


def test_current_release_pointers_are_durable_after_publication() -> None:
    for path in ("README.md", "RELEASE.md", "SECURITY.md"):
        line = _current_release_line(path)
        assert "v4.5.2 CFO Financial Analysis Release State Finalization" in line
        assert "release candidate" not in line.lower()


def test_current_release_preserves_cfo_and_runtime_boundaries() -> None:
    readme = _head("README.md", 2600)
    release = _head("RELEASE.md", 3000)
    security = _head("SECURITY.md", 2400)
    combined = readme + release + security
    assert "1.1.0" in combined
    assert "4.0.0" in combined
    assert "4.4.0" in combined
    assert "exactly 10 registered agents" in combined
    assert "read-only" in combined.lower()


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


def test_v452_release_workflow_targets_exact_main_sha() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.5.2.yml").read_text()
    assert "v4.5.2 CFO Financial Analysis Release State Finalization" in workflow
    assert "pytest -q tests/evaluations/test_cfo_financial_analysis_v450.py" in workflow
    assert "pytest -q tests/evaluations/test_cfo_release_closeout_v451.py" in workflow
    assert "pytest -q tests/evaluations/test_cfo_release_state_v452.py" in workflow
    assert "gh release create v4.5.2" in workflow
    assert '--target "$GITHUB_SHA"' in workflow
