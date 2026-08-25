from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"


def text(path: Path) -> str:
    return path.read_text()


def test_prepare_automates_configuration_without_leaking_secret() -> None:
    prepare = text(SCRIPTS / "mesh-cos-mcp-prepare.sh")
    assert 'BUILD_CONTEXT="$APP_ROOT/build-context"' in prepare
    assert "docker build" in prepare
    assert "MESH_IMAGE_ID=$(docker image inspect" in prepare
    assert "TUNNEL_IMAGE=$(docker image inspect" in prepare
    assert "MESH_COS_LEDGER_SOURCE" in prepare
    assert 'stty -echo < /dev/tty' in prepare
    assert 'chmod 0400 "$SECRET_FILE"' in prepare
    assert "OPENAI_TUNNEL_RUNTIME_KEY=" not in prepare
    assert "CONTROL_PLANE_API_KEY=" not in prepare
    assert 'sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"' in prepare


def test_deploy_is_single_orchestrated_operator_path() -> None:
    deploy = text(SCRIPTS / "mesh-cos-mcp-deploy.sh")
    required_order = [
        "mesh-cos-mcp-backup.sh\" pre-deploy",
        "mesh-cos-mcp-prepare.sh",
        "mesh-cos-mcp-preflight.sh",
        "docker compose --env-file .env -f compose.yaml up -d --no-build",
        "wait_healthy mesh-cos-mcp",
        "wait_healthy mesh-cos-tunnel",
        "mesh-cos-mcp-verify.sh",
        "mesh-cos-mcp-backup.sh\" post-deploy",
    ]
    positions = [deploy.index(token) for token in required_order]
    assert positions == sorted(positions)


def test_preflight_and_verify_bind_running_images_to_recorded_ids() -> None:
    preflight = text(SCRIPTS / "mesh-cos-mcp-preflight.sh")
    verify = text(SCRIPTS / "mesh-cos-mcp-verify.sh")
    assert "MESH_COS_IMAGE_ID" in preflight
    assert "TUNNEL_IMAGE_ID" in preflight
    assert "Mesh image identity mismatch" in preflight
    assert 'RUNNING_MESH_ID=$(docker inspect -f' in verify
    assert 'RUNNING_TUNNEL_ID=$(docker inspect -f' in verify
    assert "non-tunnel direct MCP request denied" in verify


def test_compose_never_pulls_after_prepare_and_preserves_resource_policy() -> None:
    compose = text(QNAP / "compose.yaml")
    assert compose.count("pull_policy: never") == 2
    assert "cpus: ${MESH_CPU_LIMIT:-2.0}" in compose
    assert "mem_limit: ${MESH_MEMORY_LIMIT:-24g}" in compose
    assert "pids_limit" not in compose
    assert "ports:" not in compose


def test_backup_captures_nonsecret_configuration_only() -> None:
    backup = text(SCRIPTS / "mesh-cos-mcp-backup.sh")
    assert 'cp "$APP_ROOT/.env" "$DEST/.env"' in backup
    assert 'cp "$APP_ROOT/compose.yaml" "$DEST/compose.yaml"' in backup
    assert "release-metadata.txt" in backup
    assert "SHA256SUMS" in backup
    assert "secrets_included=false" in backup
    assert 'cp "$APP_ROOT/secrets' not in backup


def test_release_bundle_contains_build_context_and_no_runtime_secret() -> None:
    builder = text(ROOT / "scripts" / "build-qnap-release-bundle.sh")
    assert 'VERSION=${1:-4.1.1}' in builder
    assert 'BUILD_CONTEXT="$BUNDLE/cos-mcp/build-context"' in builder
    assert "cp Dockerfile pyproject.toml .dockerignore" in builder
    assert "cp -R agents chatgpt config contracts src mcp" in builder
    assert 'test ! -e "$BUNDLE/cos-mcp/.env"' in builder
    assert 'test ! -e "$BUNDLE/cos-mcp/secrets"' in builder


def test_bdd_covers_automated_qnap_lifecycle() -> None:
    feature = text(ROOT / "specs" / "mesh-cos-mcp.feature")
    for scenario_id in ["QNAP-031", "QNAP-032", "QNAP-033", "QNAP-034", "QNAP-035"]:
        assert f"Scenario: {scenario_id}" in feature
