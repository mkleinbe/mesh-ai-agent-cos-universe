from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
HISTORICAL = (
    "4.1.14", "4.1.15", "4.1.18",
    "4.2.0", "4.2.1", "4.2.2", "4.2.3",
    "4.3.0", "4.3.1",
    "4.4.1", "4.4.2",
    "4.5.0", "4.5.1", "4.5.2",
    "4.6.0", "4.7.0", "4.8.0", "4.8.1", "4.8.2",
)


def test_all_published_historical_release_workflows_are_read_only_manual_verifiers() -> None:
    for version in HISTORICAL:
        text = (WORKFLOWS / f"release-v{version}.yml").read_text(encoding="utf-8")
        assert "workflow_dispatch:" in text, version
        assert "branches: [main]" not in text, version
        assert "pull_request:" not in text, version
        assert "gh release create" not in text, version
        assert "permissions:\n  contents: read" in text, version
        assert "contents: write" not in text, version


def test_v483_is_the_only_semver_release_publisher() -> None:
    current = (WORKFLOWS / "release-v4.8.3.yml").read_text(encoding="utf-8")
    assert "branches: [main]" in current
    assert "gh release create v4.8.3" in current
    assert "--target \"$GITHUB_SHA\"" in current
    assert "permissions:\n  contents: read" in current
    assert "contents: write" in current
