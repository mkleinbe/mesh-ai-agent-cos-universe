from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def _active_yaml_text(path: Path) -> str:
    return "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


def test_v483_release_records_explicitly_include_v460_retirement() -> None:
    for path in (
        ROOT / "CHANGELOG-v4.8.3.md",
        ROOT / "docs" / "release-v4.8.3-historical-publisher-retirement.md",
        ROOT / "docs" / "gap-audit-v4.8.3-historical-publisher-retirement.md",
    ):
        text = path.read_text(encoding="utf-8")
        assert "v4.6.0" in text, path
        assert "v4.8.2" in text, path


def test_v483_is_historical_and_v484_is_the_only_current_publisher() -> None:
    historical = _active_yaml_text(WORKFLOWS / "release-v4.8.3.yml")
    assert "workflow_dispatch:" in historical
    assert "branches: [main]" not in historical
    assert "pull_request:" not in historical
    assert "gh release create" not in historical
    assert "contents: write" not in historical
    assert "permissions:\n  contents: read" in historical

    current = _active_yaml_text(WORKFLOWS / "release-v4.8.4.yml")
    assert "branches: [main]" in current
    assert "pull_request:" in current
    assert "gh release create v4.8.4" in current
    assert "--target \"$GITHUB_SHA\"" in current
    assert "permissions:\n  contents: read" in current
    assert "contents: write" in current


def test_v484_is_documentation_and_release_control_only() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    release = (ROOT / "RELEASE.md").read_text(encoding="utf-8")
    docs_index = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    for text in (readme, release, docs_index):
        assert "v4.8.4 Release Record Correction" in text
        assert "4.0.0" in text
        assert "4.4.0" in text
    assert "exactly 10" in readme.lower()
