from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"
BUILDER = ROOT / "scripts" / "build-qnap-release-bundle.sh"
STEPS = QNAP / "DEPLOYMENT-STEPS.md"
FEATURE = ROOT / "specs" / "qnap-release-root-bootstrap-v4.1.12.feature"


def text(path: Path) -> str:
    return path.read_text()


def test_v4112_behavior_contract_is_ready_and_complete() -> None:
    feature = text(FEATURE)
    assert "@ready" in feature
    for scenario_id in range(83, 92):
        assert f"Scenario: QNAP-{scenario_id:03d}" in feature


def test_bundle_extracts_current_release_as_single_versioned_directory() -> None:
    builder = text(BUILDER)
    assert 'VERSION=${1:-4.1.12}' in builder
    assert 'RELEASE_DIR="$BUNDLE/v${VERSION}"' in builder
    assert 'BUILD_CONTEXT="$RELEASE_DIR/cos-mcp/build-context"' in builder
    assert 'LEGACY_FLAT=0' in builder
    assert '4.1.10|4.1.11' in builder
    assert 'LEGACY_FLAT=1' in builder
    assert 'if [ "$LEGACY_FLAT" -eq 1 ]; then' in builder
    assert 'zip -qr "$OLDPWD/$ASSET" .' in builder
    assert 'zip -qr "$OLDPWD/$ASSET" "v${VERSION}"' in builder


def test_all_operator_scripts_self_resolve_and_never_depend_on_cwd() -> None:
    operator_scripts = [
        "mesh-cos-mcp-deploy.sh",
        "mesh-cos-mcp-prepare.sh",
        "mesh-cos-mcp-preflight.sh",
        "mesh-cos-mcp-backup.sh",
        "mesh-cos-mcp-verify.sh",
        "mesh-cos-slack-hitl-configure.sh",
    ]
    for filename in operator_scripts:
        script = text(SCRIPTS / filename)
        assert 'dirname "$0"' in script
        assert "pwd -P" in script
        assert "QNAP_SCRIPT_ROOT:-/share/Docker" not in script


def test_release_layout_helper_validates_version_directory_against_metadata() -> None:
    layout = text(SCRIPTS / "mesh-cos-qnap-layout.sh")
    assert "mesh_validate_release_root()" in layout
    assert "QNAP_RELEASES_ROOT" in layout
    assert "release directory version does not match staged metadata" in layout
    deploy = text(SCRIPTS / "mesh-cos-mcp-deploy.sh")
    assert "mesh_validate_release_root" in deploy
    assert "before candidate preparation" in deploy


def test_runbook_uses_only_canonical_release_root_as_working_directory() -> None:
    steps = text(STEPS)
    assert "cd /share/Docker/cos-mcp/releases" in steps
    assert "cd /share/Docker/cos-mcp/releases/v4.1.12" not in steps
    assert "mkdir -p /share/Docker/cos-mcp/releases/v4.1.12" not in steps
    assert "cp /share/Docker/mesh-cos-mcp-qnap" not in steps
    assert "chmod 0755" not in steps
    assert "sudo sh ./v4.1.12/mesh-cos-mcp-deploy.sh" in steps
    assert "sudo sh ./v4.1.12/mesh-cos-mcp-preflight.sh" in steps
    assert "sudo sh ./v4.1.12/mesh-cos-mcp-verify.sh" in steps


def test_v4112_bundle_builder_keeps_runtime_state_and_secrets_outside_release() -> None:
    builder = text(BUILDER)
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/.env.runtime"' in builder
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/secrets"' in builder
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/state"' in builder
    assert 'test -f "$RELEASE_DIR/cos-mcp/release-metadata.txt"' in builder


def test_release_root_contract_does_not_change_phase1_authority() -> None:
    deploy = text(SCRIPTS / "mesh-cos-mcp-deploy.sh")
    assert "/share/Docker/cos-mcp/state" in text(SCRIPTS / "mesh-cos-mcp-prepare.sh")
    assert "mesh-cos-mcp-verify.sh" in deploy
    contract = json.loads(text(ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"))
    assert contract["runtime_release"] == "4.0.0"
    assert len(contract["agent_tool_allowlists"]) == 10
    assert len(contract["agent_tool_allowlists"]["cos"]) == 27
    assert set(contract["human_tool_allowlist"]) == {
        "approval.record_decision",
        "reliability.human_override",
    }
