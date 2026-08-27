from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build-qnap-release-v4.2.0.sh"


def test_v420_wrapper_rebuilds_zip_inside_dist() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    assert 'ZIP="dist/mesh-cos-mcp-qnap-v${VERSION}.zip"' in script
    assert 'cd dist/qnap-bundle' in script
    assert 'zip -rq "../mesh-cos-mcp-qnap-v${VERSION}.zip" "v${VERSION}"' in script
    assert 'zip -rq "../../mesh-cos-mcp-qnap-v${VERSION}.zip"' not in script
    assert 'cd dist\n  sha256sum "mesh-cos-mcp-qnap-v${VERSION}.zip"' in script
