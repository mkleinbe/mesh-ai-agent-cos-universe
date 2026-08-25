from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"


def text(path: Path) -> str:
    return path.read_text()


def test_prepare_validates_existing_image_provenance_before_reuse() -> None:
    prepare = text(SCRIPTS / "mesh-cos-mcp-prepare.sh")
    assert 'RELEASE_METADATA="$APP_ROOT/release-metadata.txt"' in prepare
    assert "EXPECTED_RELEASE" in prepare
    assert "EXPECTED_COMMIT" in prepare
    assert "org.opencontainers.image.version" in prepare
    assert "org.opencontainers.image.revision" in prepare
    assert "existing local Mesh image provenance mismatch; rebuilding" in prepare
    assert "built Mesh image version label mismatch" in prepare
    assert "built Mesh image revision label mismatch" in prepare


def test_verify_executes_real_tools_call_from_tunnel_network_namespace() -> None:
    verify = text(SCRIPTS / "mesh-cos-mcp-verify.sh")
    assert "--network container:mesh-cos-tunnel" in verify
    assert "tools/call" in verify
    assert "registry.get_agent" in verify
    assert "deployment_release" in verify
    assert "mcp_version" in verify
    assert "agent_id" in verify
    assert "governed tool envelope dual release identity" in verify


def test_v417_behavior_contract_is_ready_and_traced() -> None:
    feature = text(ROOT / "specs" / "qnap-image-provenance-envelope-v4.1.7.feature")
    assert "@ready" in feature
    for scenario_id in ["QNAP-056", "QNAP-057", "QNAP-058"]:
        assert f"Scenario: {scenario_id}" in feature
