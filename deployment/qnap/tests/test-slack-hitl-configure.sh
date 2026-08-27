#!/bin/sh
set -u
TMP=${TMPDIR:-/tmp}/mesh-slack-hitl-config-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
APP="$TMP/app"; BUNDLE="$TMP/release/cos-mcp"
mkdir -p "$APP/secrets" "$APP/logs/deployment" "$BUNDLE"
printf 'MESH_COS_IMAGE=image:test\nMESH_COS_DEPLOYMENT_RELEASE=4.2.0\nMESH_COS_SLACK_HITL_MODE=CHATGPT_NATIVE_EVENT_TRIGGER\n' > "$BUNDLE/.env.runtime"
printf 'tunnel-test-value\n' > "$APP/secrets/openai-tunnel-runtime-key"
printf 'xoxb-test-bot\n' > "$APP/secrets/slack-bot-token"
CALLS="$TMP/docker.calls"; : > "$CALLS"
docker() { printf '%s\n' "$*" >> "$CALLS"; return 0; }
QNAP_SCRIPT_ROOT="$(CDPATH= cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd -P)"
QNAP_BUNDLE_APP_ROOT="$BUNDLE"; QNAP_APP_ROOT="$APP"; QNAP_SLACK_APPROVER_USER_ID_FILE="$APP/secrets/slack-approver-user-id"; QNAP_SLACK_BOT_TOKEN_FILE="$APP/secrets/slack-bot-token"; MESH_COS_LOG_ROOT="$APP/logs/deployment"; MESH_UID=65532; MESH_GID=65532
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT QNAP_SLACK_APPROVER_USER_ID_FILE QNAP_SLACK_BOT_TOKEN_FILE MESH_COS_LOG_ROOT MESH_UID MESH_GID
. "$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh"
[ -s "$APP/secrets/slack-approver-user-id" ]; [ "$(cat "$APP/secrets/slack-approver-user-id")" = 'U01KG3CNYHK' ] || exit 1; [ -s "$APP/secrets/slack-bot-token" ]; [ ! -e "$APP/secrets/slack-socket-app-token" ]
grep -q -- 'image inspect image:test' "$CALLS"; grep -q -- 'slack-approver-user-id' "$CALLS"; grep -q -- 'slack-bot-token' "$CALLS"; ! grep -q -- 'slack-socket-app-token' "$CALLS"
CONFIGURE="$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh"; PROVISION="$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-provision.sh"; SECRET_INPUT="$QNAP_SCRIPT_ROOT/mesh-cos-qnap-secret-input.sh"; PREPARE="$QNAP_SCRIPT_ROOT/mesh-cos-mcp-prepare.sh"; TUNNEL_PROVISION="$QNAP_SCRIPT_ROOT/mesh-cos-tunnel-key-provision.sh"
! grep -q 'read_secret_tty' "$CONFIGURE"; ! grep -q 'command -v stty' "$CONFIGURE"; ! grep -q 'read_visible_tty' "$CONFIGURE"; ! grep -q 'QNAP_SLACK_VERIFIER_TOKEN_FILE' "$CONFIGURE"; ! grep -q 'slack-verifier-token' "$CONFIGURE"; grep -q 'DEFAULT_APPROVER_USER_ID=.*U01KG3CNYHK' "$CONFIGURE"; grep -q 'Slack bot OAuth token file is missing' "$CONFIGURE"; grep -q 'non_interactive=true' "$CONFIGURE"; grep -q 'CHATGPT_NATIVE_EVENT_TRIGGER' "$CONFIGURE"; grep -q 'legacy Slack Socket Mode must not be configured' "$CONFIGURE"
test -f "$PROVISION"; test -f "$SECRET_INPUT"; test -f "$TUNNEL_PROVISION"; grep -q 'mesh_read_secret_tty' "$PROVISION"; ! grep -q 'Slack Socket Mode app-level token (input hidden)' "$PROVISION"; grep -q 'Slack bot OAuth token (input hidden)' "$PROVISION"; grep -q 'xoxb-' "$PROVISION"; ! grep -q 'slack-verifier-token' "$PROVISION"; grep -q 'socket_required=false' "$PROVISION"; grep -q 'mesh_shell_supports_silent_read' "$SECRET_INPUT"; grep -q '/bin/stty /usr/bin/stty' "$SECRET_INPUT"; ! grep -q 'read_secret_tty' "$PREPARE"; ! grep -q 'QNAP_SLACK_VERIFIER_TOKEN_FILE' "$PREPARE"; grep -q 'mesh-cos-tunnel-key-provision.sh' "$PREPARE"
LOGS=$(find "$APP/logs/deployment" -type f -print); [ -n "$LOGS" ]
if grep -R -q 'U01KG3CNYHK\|xoxb-test-bot\|tunnel-test-value' "$APP/logs/deployment"; then echo 'FAIL Slack HITL protected value leaked to deployment logs' >&2; exit 1; fi
echo 'PASS Slack HITL deploy path validates governed approver and dedicated bot credential for native-trigger reconciliation without logging protected values'
