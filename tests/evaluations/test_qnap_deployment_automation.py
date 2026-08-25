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
    assert "OPENAI_TUNNEL_RUNTIME_KEY=" not in prepare
    assert "CONTROL_PLANE_API_KEY=" not in prepare
    assert "mesh_resolve_compose" in prepare
    assert "mesh_apply_state_permissions" in prepare
    assert "mesh_stage_ledger" in prepare
    assert "mesh_apply_secret_permissions" in prepare
    assert 'sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"' in prepare
    assert "chown -R" not in prepare
    assert 'chown "$MESH_UID:$MESH_GID"' not in prepare
    assert "MESH_COS_DEPLOYMENT_RELEASE:-4.1.7" in prepare
    assert "mesh-cos-mcp:qnap-v4.1.7" in prepare
    assert 'IMAGE_PROVENANCE_LIB="$SCRIPT_ROOT/mesh-cos-qnap-image-provenance.sh"' in prepare
    assert "mesh_image_provenance_matches" in prepare
    assert "built Mesh image version label mismatch" in prepare
    assert "built Mesh image revision label mismatch" in prepare


def test_deploy_is_single_orchestrated_operator_path_with_diagnostics() -> None:
    deploy = text(SCRIPTS / "mesh-cos-mcp-deploy.sh")
    required_order = [
        "mesh-cos-mcp-backup.sh\" pre-deploy",
        "mesh-cos-mcp-prepare.sh",
        "mesh-cos-mcp-preflight.sh",
        "mesh_compose --env-file .env -f compose.yaml up -d --no-build",
        "wait_healthy mesh-cos-mcp",
        "wait_healthy mesh-cos-tunnel",
        "mesh-cos-mcp-verify.sh",
        "mesh-cos-mcp-backup.sh\" post-deploy",
    ]
    positions = [deploy.index(token) for token in required_order]
    assert positions == sorted(positions)
    assert "mesh_obs_init deploy" in deploy
    assert "mesh_collect_diagnostics" in deploy
    assert 'echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"' in deploy


def test_compose_discovery_is_qnap_aware_and_v2_only() -> None:
    helper = text(SCRIPTS / "mesh-cos-qnap-compose.sh")
    regression = text(QNAP / "tests" / "test-compose-discovery.sh")
    assert "docker compose" in helper
    assert "/usr/local/lib/docker/cli-plugins/docker-compose" in helper
    assert "Install_Path" in helper
    assert "mesh_compose_v2" in helper
    assert "direct-plugin" in helper
    assert "MOCK_DOCKER_COMPOSE_OK=0" in regression
    assert "MOCK_PLUGIN_VERSION=v1.29.2" in regression


def test_observability_is_structured_redaction_safe_and_posix_sh() -> None:
    obs = text(SCRIPTS / "mesh-cos-qnap-observability.sh")
    regression = text(QNAP / "tests" / "test-observability.sh")
    for token in [
        "MESH_COS_RUN_ID",
        "MESH_COS_LOG_FILE",
        "command_start",
        "command_end",
        "mesh_collect_diagnostics",
        "DIAGNOSTIC_LOG",
        "secret_contents_collected=false",
        "env_contents_collected=false",
        "tunnel_logs_collected=false",
        "mesh_init_docker_config",
    ]:
        assert token in obs
    assert "PIPESTATUS" not in obs
    assert ">(" not in obs
    assert "set -e" not in obs
    assert "OPENAI_API_KEY='sk-supersecret-never-log'" in regression
    assert "! grep -q 'supersecret'" in regression


def test_permission_helper_is_constrained_and_host_chown_is_not_required() -> None:
    helper = text(SCRIPTS / "mesh-cos-qnap-permissions.sh")
    regression = text(QNAP / "tests" / "test-runtime-permissions.sh")
    for token in [
        "--network none",
        "--read-only",
        "--user 0:0",
        "--cap-drop ALL",
        "--cap-add CHOWN",
        "--cap-add FOWNER",
        "--cap-add DAC_OVERRIDE",
        "--security-opt no-new-privileges",
        "--user \"$uid:$gid\"",
        "mesh_run_stdin_file",
    ]:
        assert token in helper
    assert "mesh_validate_runtime_identity" in helper
    assert "nonnumeric UID" in regression
    assert "nonnumeric GID" in regression


def test_image_provenance_helper_rejects_stale_release_labels() -> None:
    helper = text(SCRIPTS / "mesh-cos-qnap-image-provenance.sh")
    regression = text(QNAP / "tests" / "test-image-provenance.sh")
    assert "mesh_release_metadata_value" in helper
    assert "mesh_image_provenance_matches" in helper
    assert "org.opencontainers.image.version" in helper
    assert "org.opencontainers.image.revision" in helper
    assert "stale image version was accepted" in regression
    assert "stale image revision was accepted" in regression


def test_preflight_validates_runtime_access_not_host_user_rw() -> None:
    preflight = text(SCRIPTS / "mesh-cos-mcp-preflight.sh")
    assert "runtime-state-access" in preflight
    assert '--user "$MESH_UID:$MESH_GID"' in preflight
    assert "canonical ledger is read/write for runtime UID/GID" in preflight
    assert '[ -r "$LEDGER" ] && [ -w "$LEDGER" ]' not in preflight
    assert "deployment-local Docker config exists and is writable" in preflight


def test_preflight_and_verify_bind_running_images_and_governed_envelope() -> None:
    preflight = text(SCRIPTS / "mesh-cos-mcp-preflight.sh")
    verify = text(SCRIPTS / "mesh-cos-mcp-verify.sh")
    assert "MESH_COS_IMAGE_ID" in preflight
    assert "TUNNEL_IMAGE_ID" in preflight
    assert "Mesh image identity mismatch" in preflight
    assert 'RUNNING_MESH_ID=$(docker inspect -f' in verify
    assert 'RUNNING_TUNNEL_ID=$(docker inspect -f' in verify
    assert "non-tunnel direct MCP request denied" in verify
    assert "mesh_obs_init verify" in verify
    assert "--network container:mesh-cos-tunnel" in verify
    assert "tools/call" in verify
    assert "registry.get_agent" in verify
    assert "governed tool envelope dual release identity" in verify


def test_compose_never_pulls_after_prepare_and_preserves_resource_policy() -> None:
    compose = text(QNAP / "compose.yaml")
    assert compose.count("pull_policy: never") == 2
    assert "cpus: ${MESH_CPU_LIMIT:-2.0}" in compose
    assert "mem_limit: ${MESH_MEMORY_LIMIT:-24g}" in compose
    assert "MESH_COS_DEPLOYMENT_RELEASE: ${MESH_COS_DEPLOYMENT_RELEASE:?deployment release required}" in compose
    assert "pids_limit" not in compose
    assert "ports:" not in compose


def test_backup_uses_docker_mediated_state_export_and_excludes_secrets() -> None:
    backup = text(SCRIPTS / "mesh-cos-mcp-backup.sh")
    assert "docker cp" in backup
    assert "remove-container-temp" in backup
    assert 'cp "$APP_ROOT/.env" "$DEST/.env"' in backup
    assert 'cp "$APP_ROOT/compose.yaml" "$DEST/compose.yaml"' in backup
    assert "release-metadata.txt" in backup
    assert "SHA256SUMS" in backup
    assert "secrets_included=false" in backup
    assert "state_export_method=docker_cp" in backup
    assert 'cp "$TMP_HOST"' not in backup
    assert 'cp "$APP_ROOT/secrets' not in backup


def test_release_bundle_contains_v417_docs_helpers_metadata_and_no_runtime_secret() -> None:
    builder = text(ROOT / "scripts" / "build-qnap-release-bundle.sh")
    assert 'VERSION=${1:-4.1.7}' in builder
    assert 'BUILD_CONTEXT="$BUNDLE/cos-mcp/build-context"' in builder
    assert "cp Dockerfile pyproject.toml .dockerignore" in builder
    assert "cp -R agents chatgpt config contracts src mcp" in builder
    assert "qnap-security-review-v4.1.7.md" in builder
    assert "qnap-image-provenance-envelope-debugging-v4.1.7.md" in builder
    assert "release-4.1.7-qnap-image-provenance-envelope.md" in builder
    assert "qnap-image-provenance-envelope-v4.1.7.feature" in builder
    assert 'test ! -e "$BUNDLE/cos-mcp/.env"' in builder
    assert 'test ! -e "$BUNDLE/cos-mcp/secrets"' in builder
    assert 'test -f "$BUNDLE/mesh-cos-qnap-compose.sh"' in builder
    assert 'test -f "$BUNDLE/mesh-cos-qnap-observability.sh"' in builder
    assert 'test -f "$BUNDLE/mesh-cos-qnap-permissions.sh"' in builder
    assert 'test -f "$BUNDLE/mesh-cos-qnap-image-provenance.sh"' in builder
    assert 'test -f "$BUNDLE/cos-mcp/release-metadata.txt"' in builder


def test_deployment_steps_contain_v417_subshell_sudo_and_log_receipt() -> None:
    steps = text(QNAP / "DEPLOYMENT-STEPS.md")
    assert "installer executes inside a subshell" in steps
    assert "SSH session remains active" in steps
    assert "DIAGNOSTIC_LOG" in steps
    assert "v4.1.7" in steps
    assert "sudo sh /share/Docker/mesh-cos-mcp-deploy.sh" in steps
    assert "exit \"$RC\"" not in steps


def test_bdd_covers_ownership_observability_docker_config_and_backup_remediation() -> None:
    feature = text(ROOT / "specs" / "qnap-deployment-remediation-v4.1.3.feature")
    assert "@ready" in feature
    for scenario_id in ["QNAP-038", "QNAP-039", "QNAP-040", "QNAP-041"]:
        assert f"Scenario: {scenario_id}" in feature


def test_v414_transport_bdd_is_ready_and_covers_502_regression() -> None:
    feature = text(ROOT / "specs" / "qnap-mcp-modern-transport-v4.1.4.feature")
    assert "@ready" in feature
    for scenario_id in ["QNAP-042", "QNAP-043", "QNAP-044", "QNAP-045", "QNAP-046", "QNAP-047"]:
        assert f"Scenario: {scenario_id}" in feature


def test_v415_release_identity_bdd_is_ready() -> None:
    feature = text(ROOT / "specs" / "qnap-release-identity-v4.1.5.feature")
    assert "@ready" in feature
    for scenario_id in ["QNAP-048", "QNAP-049", "QNAP-050"]:
        assert f"Scenario: {scenario_id}" in feature


def test_v416_published_app_bdd_covers_identity_and_hosted_acceptance() -> None:
    feature = text(ROOT / "specs" / "qnap-published-chatgpt-app-v4.1.6.feature")
    for scenario_id in ["QNAP-051", "QNAP-052", "QNAP-053", "QNAP-054", "QNAP-055"]:
        assert f"Scenario: {scenario_id}" in feature
    for token in ["deployment_release", "SECURE_MCP_TUNNEL", "exactly 27", "exactly 10", "HTTP 502"]:
        assert token in feature


def test_v417_image_provenance_and_envelope_bdd_is_ready() -> None:
    feature = text(ROOT / "specs" / "qnap-image-provenance-envelope-v4.1.7.feature")
    assert "@ready" in feature
    for scenario_id in ["QNAP-056", "QNAP-057", "QNAP-058"]:
        assert f"Scenario: {scenario_id}" in feature
    for token in ["release metadata", "deployment_release 4.1.7", "mcp_version 4.0.0", "agent_id cos"]:
        assert token in feature
