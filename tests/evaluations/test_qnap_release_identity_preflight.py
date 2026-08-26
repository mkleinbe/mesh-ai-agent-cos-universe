from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT = ROOT / "deployment" / "qnap" / "scripts" / "mesh-cos-mcp-preflight.sh"


def test_preflight_derives_expected_release_from_bundle_metadata() -> None:
    preflight = PREFLIGHT.read_text()
    assert 'RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"' in preflight
    assert 'EXPECTED_RELEASE=$(mesh_candidate_release "$RELEASE_METADATA"' in preflight
    assert "candidate MESH_COS_DEPLOYMENT_RELEASE must match staged bundle release" in preflight
    assert "active release may differ before candidate promotion" in preflight


def test_preflight_has_no_stale_release_literal_gate() -> None:
    preflight = PREFLIGHT.read_text()
    assert 'MESH_COS_DEPLOYMENT_RELEASE must be 4.1.3' not in preflight
    assert 'deployment release 4.1.3' not in preflight
