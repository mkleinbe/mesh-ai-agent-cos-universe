from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"


def text(path: Path) -> str:
    return path.read_text()


def test_operator_scripts_resolve_helpers_from_extracted_bundle_root() -> None:
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
        assert "QNAP_SCRIPT_ROOT:-/share/Docker" not in script
        assert 'dirname "$0"' in script
        assert "pwd -P" in script


def test_prepare_binds_candidate_identity_to_staged_bundle_not_active_root() -> None:
    prepare = text(SCRIPTS / "mesh-cos-mcp-prepare.sh")
    assert 'BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}' in prepare
    assert 'BUILD_CONTEXT="$BUNDLE_APP_ROOT/build-context"' in prepare
    assert 'RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"' in prepare
    assert 'CANDIDATE_COMPOSE="$BUNDLE_APP_ROOT/compose.yaml"' in prepare
    assert 'CANDIDATE_ENV="$BUNDLE_APP_ROOT/.env.runtime"' in prepare
    assert "MESH_COS_DEPLOYMENT_RELEASE:-4.1.10" not in prepare
    assert "mesh_candidate_release" in prepare
    assert "mesh_normalize_release" in prepare
    assert "requested deployment release does not match extracted bundle metadata" in prepare


def test_preflight_distinguishes_active_release_from_staged_candidate() -> None:
    preflight = text(SCRIPTS / "mesh-cos-mcp-preflight.sh")
    assert 'BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}' in preflight
    assert 'RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"' in preflight
    assert 'ACTIVE_ENV_FILE="$APP_ROOT/.env"' in preflight
    assert 'CANDIDATE_ENV_FILE="$BUNDLE_APP_ROOT/.env.runtime"' in preflight
    assert "active deployment release" in preflight
    assert "staged candidate release" in preflight
    assert "active release may differ before candidate promotion" in preflight


def test_deploy_runs_in_place_then_promotes_transactionally_after_candidate_health() -> None:
    deploy = text(SCRIPTS / "mesh-cos-mcp-deploy.sh")
    helper = text(SCRIPTS / "mesh-cos-qnap-promotion.sh")
    assert 'BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}' in deploy
    assert 'CANDIDATE_ENV="$BUNDLE_APP_ROOT/.env.runtime"' in deploy
    assert 'CANDIDATE_COMPOSE="$BUNDLE_APP_ROOT/compose.yaml"' in deploy
    assert 'mesh_compose --env-file "$CANDIDATE_ENV" -f "$CANDIDATE_COMPOSE" up -d --no-build' in deploy
    execution = deploy[deploy.index("mesh_set_stage pre_backup") :]
    health_pos = execution.index("wait_healthy mesh-cos-tunnel")
    promote_pos = execution.index("mesh_set_stage candidate_promote")
    verify_pos = execution.index("mesh-cos-mcp-verify.sh")
    commit_pos = execution.index("candidate_promotion_commit")
    assert health_pos < promote_pos < verify_pos < commit_pos
    assert "mesh_snapshot_active_configuration" in deploy
    assert "mesh_promote_candidate_configuration" in deploy
    assert "mesh_restore_active_configuration" in deploy
    assert 'incoming="$target.incoming.$$"' in helper
    assert 'mv "$incoming" "$target"' in helper


def test_release_identity_normalization_accepts_git_v_prefix_but_preserves_mismatch_gate() -> None:
    layout = text(SCRIPTS / "mesh-cos-qnap-layout.sh")
    assert "mesh_normalize_release()" in layout
    assert 'v*) printf \'%s\\n\' "${1#v}" ;;' in layout
    assert "mesh_release_is_semver" in layout
    prepare = text(SCRIPTS / "mesh-cos-mcp-prepare.sh")
    assert "mesh_normalize_release" in prepare
    assert "requested deployment release does not match extracted bundle metadata" in prepare


def test_v4111_release_evidence_remains_historical_and_current_default_advances() -> None:
    builder = text(ROOT / "scripts" / "build-qnap-release-bundle.sh")
    historical_release = text(ROOT / "docs" / "release-4.1.11-qnap-versioned-release-staging.md")
    historical_spec = text(ROOT / "specs" / "qnap-versioned-release-staging-v4.1.11.feature")
    assert "4.1.10|4.1.11" in builder
    assert "LEGACY_FLAT=1" in builder
    assert "v4.1.11" in historical_release
    assert "QNAP-074" in historical_spec
    assert "QNAP-082" in historical_spec
    assert 'VERSION=${1:-4.1.16}' in builder
