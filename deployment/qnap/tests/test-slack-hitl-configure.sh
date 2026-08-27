#!/bin/sh
set -u

TMP=${TMPDIR:-/tmp}/mesh-slack-hitl-config-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
APP="$TMP/app"
BUNDLE="$TMP/release/cos-mcp"
mkdir -p "$APP/secrets" "$APP/logs/deployment" "$BUNDLE"
printf 'MESH_COS_IMAGE=image:test\nMESH_COS_DEPLOYMENT_RELEASE=4.1.15\n' > "$BUNDLE/.env.runtime"
printf 'tunnel-test-value\n' > "$APP/secrets/openai-tunnel-runtime-key"
printf 'xapp-test-socket\n' > "$APP/secrets/slack-socket-app-token"
# A legacy verifier file may remain for rollback compatibility, but v4.1.15 must not use it.
printf 'xoxb-legacy-verifier\n' > "$APP/secrets/slack-verifier-token"
CALLS="$TMP/docker.calls"
: > "$CALLS"

docker() {
  printf '%s\n' "$*" >> "$CALLS"
  return 0
}

QNAP_SCRIPT_ROOT="$(CDPATH= cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd -P)"
QNAP_BUNDLE_APP_ROOT="$BUNDLE"
QNAP_APP_ROOT="$APP"
QNAP_SLACK_APPROVER_USER_ID_FILE="$APP/secrets/slack-approver-user-id"
QNAP_SLACK_SOCKET_APP_TOKEN_FILE="$APP/secrets/slack-socket-app-token"
MESH_COS_LOG_ROOT="$APP/logs/deployment"
MESH_UID=65532
MESH_GID=65532
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT QNAP_SLACK_APPROVER_USER_ID_FILE
export QNAP_SLACK_SOCKET_APP_TOKEN_FILE MESH_COS_LOG_ROOT MESH_UID MESH_GID

. "$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh"

[ -s "$APP/secrets/slack-approver-user-id" ]
[ "$(cat "$APP/secrets/slack-approver-user-id")" = 'U01KG3CNYHK' ] || {
  echo 'FAIL governed Slack approver user ID was not bootstrapped' >&2
  exit 1
}
[ -s "$APP/secrets/slack-socket-app-token" ]
grep -q -- 'image inspect image:test' "$CALLS"
grep -q -- 'openai-tunnel-runtime-key' "$CALLS"
grep -q -- 'slack-approver-user-id' "$CALLS"
grep -q -- 'slack-socket-app-token' "$CALLS"

CONFIGURE="$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh"
PROVISION="$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-provision.sh"
SECRET_INPUT="$QNAP_SCRIPT_ROOT/mesh-cos-qnap-secret-input.sh"
PREPARE="$QNAP_SCRIPT_ROOT/mesh-cos-mcp-prepare.sh"
TUNNEL_PROVISION="$QNAP_SCRIPT_ROOT/mesh-cos-tunnel-key-provision.sh"
! grep -q 'read_secret_tty' "$CONFIGURE"
! grep -q 'command -v stty' "$CONFIGURE"
! grep -q 'read_visible_tty' "$CONFIGURE"
! grep -q 'Slack user ID for the human approval principal' "$CONFIGURE"
! grep -q 'QNAP_SLACK_VERIFIER_TOKEN_FILE' "$CONFIGURE"
! grep -q 'xoxb-' "$CONFIGURE"
grep -q 'DEFAULT_APPROVER_USER_ID=.*U01KG3CNYHK' "$CONFIGURE"
grep -q 'Slack conversation/DM channel ID is not a user ID' "$CONFIGURE"
grep -q "grep -Eq '\^\[UW\]\[A-Z0-9\]+\$'" "$CONFIGURE"
grep -q 'non_interactive=true' "$CONFIGURE"
grep -q 'verifier_required=false' "$CONFIGURE"
test -f "$PROVISION"
test -f "$SECRET_INPUT"
test -f "$TUNNEL_PROVISION"
grep -q 'mesh_read_secret_tty' "$PROVISION"
grep -q 'Slack Socket Mode app-level token (input hidden)' "$PROVISION"
! grep -q 'Slack read-only verifier bot token' "$PROVISION"
! grep -q 'xoxb-' "$PROVISION"
grep -q 'mesh_shell_supports_silent_read' "$SECRET_INPUT"
grep -q '/bin/stty /usr/bin/stty' "$SECRET_INPUT"
! grep -q 'read_secret_tty' "$PREPARE"
! grep -q 'command -v stty' "$PREPARE"
! grep -q 'QNAP_SLACK_VERIFIER_TOKEN_FILE' "$PREPARE"
! grep -q 'MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS' "$PREPARE"
grep -q 'mesh-cos-tunnel-key-provision.sh' "$PREPARE"
grep -q 'mesh_read_secret_tty' "$TUNNEL_PROVISION"

LOGS=$(find "$APP/logs/deployment" -type f -print)
[ -n "$LOGS" ]
if grep -R -q 'U01KG3CNYHK\|xoxb-legacy-verifier\|xapp-test-socket\|tunnel-test-value' "$APP/logs/deployment"; then
  echo 'FAIL Slack HITL protected value leaked to deployment logs' >&2
  exit 1
fi

echo 'PASS Slack HITL deploy path requires only governed approver identity and Socket Mode credential and does not log protected values'
