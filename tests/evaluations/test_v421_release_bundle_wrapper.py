from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build-qnap-release-v4.2.1.sh"


def test_v421_wrapper_rebuilds_zip_inside_dist_and_contains_current_contract() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    assert "VERSION=4.2.1" in script
    assert 'ZIP="dist/mesh-cos-mcp-qnap-v${VERSION}.zip"' in script
    assert 'cd dist/qnap-bundle' in script
    assert 'zip -rq "../mesh-cos-mcp-qnap-v${VERSION}.zip" "v${VERSION}"' in script
    assert 'zip -rq "../../mesh-cos-mcp-qnap-v${VERSION}.zip"' not in script
    assert 'cd dist\n  sha256sum "mesh-cos-mcp-qnap-v${VERSION}.zip"' in script
    assert "CHANGELOG-v4.2.1.md" in script
    assert "slack-app-manifest.v4.2.1.json" in script
    assert "native-slack-event-hitl-v4.2.1.feature" in script
    assert "security-review-v4.2.1.md" in script
    assert "chatgpt-native-slack-dispatcher-v4.2.1.md" in script
    assert "chatgpt-published-app-production-acceptance-v4.2.1.md" in script
    assert "release-4.2.1-slack-rendered-decision.md" in script
    assert "/mesh-approval Socket Mode ingress" in script
    assert "! grep -q '/mesh-approval Socket Mode ingress'" in script
