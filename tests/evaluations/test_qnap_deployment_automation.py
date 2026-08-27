from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QNAP = ROOT / "deployment" / "qnap"
SCRIPTS = QNAP / "scripts"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prepare_automates_candidate_without_protected_secret_input_or_verifier_dependency() -> None:
    prepare = text(SCRIPTS / "mesh-cos-mcp-prepare.sh")
    tunnel_provision = text(SCRIPTS / "mesh-cos-tunnel-key-provision.sh")
    assert 'BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}' in prepare
    assert 'CANDIDATE_ENV="$BUNDLE_APP_ROOT/.env.runtime"' in prepare
    assert "mesh_candidate_release" in prepare
    assert "mesh_normalize_release" in prepare
    assert "docker build" in prepare
    assert "mesh_image_provenance_matches" in prepare
    assert "MESH_COS_LEDGER_SOURCE" in prepare
    assert "mesh_apply_state_permissions" in prepare
    assert "mesh_stage_ledger" in prepare
    assert "mesh_apply_secret_permissions" in prepare
    assert 'sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"' in prepare
    assert "read_secret_tty" not in prepare
    assert "command -v stty" not in prepare
    assert "QNAP_SLACK_APPROVER_USER_ID_FILE=" in prepare
    assert "QNAP_SLACK_SOCKET_APP_TOKEN_FILE=" in prepare
    assert "QNAP_SLACK_VERIFIER_TOKEN_FILE=" not in prepare
    assert "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS=" not in prepare
    assert "MESH_COS_SLACK_APPROVER_USER_ID=" not in prepare
    assert "OpenAI tunnel runtime API key (input hidden)" in tunnel_provision
    assert "mesh_read_secret_tty" in tunnel_provision
    assert "value_logged=false" in tunnel_provision


def test_deploy_rolls_back_failed_candidate_before_promotion() -> None:
    deploy = text(SCRIPTS / "mesh-cos-mcp-deploy.sh")
    required_order = [
        "mesh-cos-mcp-backup.sh\" pre-deploy",
        "mesh-cos-mcp-prepare.sh",
        "mesh-cos-slack-hitl-configure.sh",
        "mesh-cos-mcp-preflight.sh",
        "mesh_compose --env-file \"$CANDIDATE_ENV\" -f \"$CANDIDATE_COMPOSE\" up -d --no-build",
        "wait_healthy mesh-cos-mcp",
        "wait_healthy mesh-cos-tunnel",
        "candidate_promote",
        "mesh-cos-mcp-verify.sh",
        "mesh-cos-mcp-backup.sh\" post-deploy",
    ]
    positions = [deploy.index(token) for token in required_order]
    assert positions == sorted(positions)
    assert 'ACTIVE_ENV="$APP_ROOT/.env"' in deploy
    assert 'ACTIVE_COMPOSE="$APP_ROOT/compose.yaml"' in deploy
    assert "restore_active_stack()" in deploy
    assert "fail_candidate_before_promotion()" in deploy
    assert 'mesh_compose --env-file "$CANDIDATE_ENV" -f "$CANDIDATE_COMPOSE" down --remove-orphans' in deploy
    assert 'mesh_compose --env-file "$ACTIVE_ENV" -f "$ACTIVE_COMPOSE" up -d --no-build' in deploy
    assert "active_release_preserved=true" in deploy
    assert "previously active stack restored" in deploy
    assert "mesh_validate_release_root" in deploy


def test_operator_scripts_self_resolve_versioned_bundle_root() -> None:
    for filename in [
        "mesh-cos-mcp-deploy.sh",
        "mesh-cos-mcp-prepare.sh",
        "mesh-cos-mcp-preflight.sh",
        "mesh-cos-mcp-backup.sh",
        "mesh-cos-mcp-verify.sh",
        "mesh-cos-slack-hitl-configure.sh",
        "mesh-cos-slack-hitl-provision.sh",
        "mesh-cos-tunnel-key-provision.sh",
    ]:
        script = text(SCRIPTS / filename)
        assert "QNAP_SCRIPT_ROOT:-/share/Docker" not in script
        assert 'dirname "$0"' in script
        assert "pwd -P" in script


def test_slack_hitl_configuration_is_minimal_candidate_bound_and_secret_safe() -> None:
    configure = text(SCRIPTS / "mesh-cos-slack-hitl-configure.sh")
    provision = text(SCRIPTS / "mesh-cos-slack-hitl-provision.sh")
    secret_input = text(SCRIPTS / "mesh-cos-qnap-secret-input.sh")
    assert 'CANDIDATE_ENV_FILE=${QNAP_CANDIDATE_ENV_FILE:-"$BUNDLE_APP_ROOT/.env.runtime"}' in configure
    assert "DEFAULT_APPROVER_USER_ID" in configure
    assert "U01KG3CNYHK" in configure
    assert "Slack conversation/DM channel ID is not a user ID" in configure
    assert "grep -Eq '^[UW][A-Z0-9]+$'" in configure
    assert "Slack Socket Mode app token file is missing" in configure
    assert "slack-socket-app-token" in configure
    assert "Slack verifier" not in configure
    assert "xoxb-" not in configure
    assert "read_secret_tty" not in configure
    assert "command -v stty" not in configure
    assert "value_logged=false" in configure
    assert "verifier_required=false" in configure
    assert "Slack Socket Mode app-level token (input hidden)" in provision
    assert "Slack read-only verifier bot token" not in provision
    assert "xoxb-" not in provision
    assert "xapp-*" in provision
    assert "mesh_read_secret_tty" in provision
    assert "value_logged=false" in provision
    assert "mesh_shell_supports_silent_read" in secret_input
    assert "/bin/stty /usr/bin/stty" in secret_input


def test_qnap_compose_has_deterministic_egress_and_minimal_slack_mounts() -> None:
    compose = text(QNAP / "compose.yaml")
    assert compose.count("pull_policy: never") == 2
    assert 'MESH_COS_SLACK_HITL_REQUIRED: "true"' in compose
    assert "MESH_COS_SLACK_APPROVER_USER_ID_FILE: /run/secrets/slack_approver_user_id" in compose
    assert "MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE: /run/secrets/slack_socket_app_token" in compose
    assert "MESH_COS_SLACK_APPROVAL_COMMAND: /mesh-approval" in compose
    assert "MESH_COS_SLACK_VERIFIER_TOKEN_FILE" not in compose
    assert "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS" not in compose
    assert "/run/secrets/slack_verifier_token" not in compose
    assert "mesh-cos-private:" in compose
    assert "internal: true" in compose
    assert "mesh-cos-egress:" in compose
    assert "172.30.61.0/29" in compose
    assert "172.30.61.2" in compose
    assert "MCP_TRUSTED_CLIENT_IP: 172.30.60.3" in compose
    assert "ipv4_address: 192.168.7.60" in compose
    assert "gw_priority" not in compose
    assert "ports:" not in compose
    assert "pids_limit" not in compose


def test_preflight_and_verify_remain_fail_closed_around_runtime_identity() -> None:
    preflight = text(SCRIPTS / "mesh-cos-mcp-preflight.sh")
    verify = text(SCRIPTS / "mesh-cos-mcp-verify.sh")
    runtime_preflight = text(QNAP / "runtime_preflight.py")
    assert 'ACTIVE_ENV_FILE="$APP_ROOT/.env"' in preflight
    assert 'CANDIDATE_ENV_FILE="$BUNDLE_APP_ROOT/.env.runtime"' in preflight
    assert "active release may differ before candidate promotion" in preflight
    assert "canonical ledger is read/write for candidate runtime UID/GID" in preflight
    assert "MESH_COS_SLACK_VERIFIER_TOKEN_FILE" not in runtime_preflight
    assert "xoxb-" not in runtime_preflight
    assert "MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE" in runtime_preflight
    assert "xapp-" in runtime_preflight
    assert "slack_approval_command_invalid" in runtime_preflight
    assert "non-tunnel direct MCP request denied" in verify
    assert "--network container:mesh-cos-tunnel" in verify
    assert "registry.get_agent" in verify


def test_backup_excludes_secrets_and_preserves_recoverable_state() -> None:
    backup = text(SCRIPTS / "mesh-cos-mcp-backup.sh")
    assert "docker cp" in backup
    assert 'cp "$APP_ROOT/.env" "$DEST/.env"' in backup
    assert 'cp "$APP_ROOT/compose.yaml" "$DEST/compose.yaml"' in backup
    assert "release-metadata.txt" in backup
    assert "SHA256SUMS" in backup
    assert "secrets_included=false" in backup
    assert 'cp "$APP_ROOT/secrets' not in backup


def test_v4115_release_builder_packages_current_contract_without_runtime_secrets() -> None:
    builder = text(ROOT / "scripts" / "build-qnap-release-bundle.sh")
    assert 'VERSION=${1:-4.1.15}' in builder
    assert 'RELEASE_DIR="$BUNDLE/v${VERSION}"' in builder
    assert 'BUILD_CONTEXT="$RELEASE_DIR/cos-mcp/build-context"' in builder
    assert "qnap-slack-plugin-hitl-v4.1.15.feature" in builder
    assert "engineering-contract-v4.1.15.md" in builder
    assert "security-review-v4.1.15.md" in builder
    assert "release-4.1.15-slack-plugin-hitl.md" in builder
    assert "verification-v4.1.15-slack-plugin-hitl.md" in builder
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/.env"' in builder
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/.env.runtime"' in builder
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/secrets"' in builder
    assert 'test ! -e "$RELEASE_DIR/cos-mcp/state"' in builder
    assert 'zip -qr "$OLDPWD/$ASSET" "v${VERSION}"' in builder
