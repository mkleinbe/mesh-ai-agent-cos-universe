from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_v4120_bundle_contains_only_changed_skill() -> None:
    script = (ROOT / "scripts" / "build-chatgpt-skill-bundle-v4.12.0.sh").read_text()
    assert "VERSION=4.12.0" in script
    assert "mesh-chief-of-staff" in script
    for unchanged in ("mesh-cro", "mesh-coo", "mesh-cfo", "mesh-cmo"):
        assert unchanged not in script


def test_v4120_release_workflow_publishes_exact_sha() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.12.0.yml").read_text()
    assert "gh release create v4.12.0" in workflow
    assert '--target "$GITHUB_SHA"' in workflow
    assert "mesh-cos-chief-of-staff-v4.12.0.zip" in workflow


def test_v4111_publisher_is_frozen() -> None:
    workflow = (ROOT / ".github" / "workflows" / "release-v4.11.1.yml").read_text()
    assert "push:" not in workflow
    assert "pull_request:" not in workflow
    assert "workflow_dispatch:" in workflow
    assert "a2860c133c4ca3fc41c2769f2e3bfbe0d2eb2a7f" in workflow


def test_v4120_human_install_boundary_is_documented() -> None:
    doc = (ROOT / "docs" / "skills-v4.12.0.md").read_text()
    assert "mesh-chief-of-staff" in doc
    assert "Installation remains human controlled" in doc

def test_v4120_bundle_has_real_shell_expansion() -> None:
    script = (ROOT / "scripts" / "build-chatgpt-skill-bundle-v4.12.0.sh").read_text()
    assert r"\${VERSION}" not in script
    assert r"\$ROOT" not in script
    assert 'ROOT="dist/chatgpt-skill-bundle/v${VERSION}"' in script
    assert 'rm -rf "$ROOT"' in script
