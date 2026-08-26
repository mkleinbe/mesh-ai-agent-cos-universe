#!/bin/sh
set -u

TMP=${TMPDIR:-/tmp}/mesh-slack-hitl-config-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
APP="$TMP/app"
BUNDLE="$TMP/release/cos-mcp"
mkdir -p "$APP/secrets" "$APP/logs/deployment" "$BUNDLE"
printf 'MESH_COS_IMAGE=image:test\nMESH_COS_DEPLOYMENT_RELEASE=4.1.11\n' > "$BUNDLE/.env.runtime"
printf 'tunnel-test-value\n' > "$APP/secrets/openai-tunnel-runtime-key"
printf 'U0TESTAPPROVER\n' > "$APP/secrets/slack-approver-user-id"
printf 'xoxb-test-verifier\n' > "$APP/secrets/slack-verifier-token"
printf 'xapp-test-socket\n' > "$APP/secrets/slack-socket-app-token"
CALLS="$TMP/docker.calls"
: > "$CALLS"

# Execute in the current shell so the constrained Docker stub is visible to sourced helpers.
docker() {
  printf '%s\n' "$*" >> "$CALLS"
  return 0
}

QNAP_SCRIPT_ROOT="$(CDPATH= cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd -P)"
QNAP_BUNDLE_APP_ROOT="$BUNDLE"
QNAP_APP_ROOT="$APP"
QNAP_SLACK_APPROVER_USER_ID_FILE="$APP/secrets/slack-approver-user-id"
QNAP_SLACK_VERIFIER_TOKEN_FILE="$APP/secrets/slack-verifier-token"
QNAP_SLACK_SOCKET_APP_TOKEN_FILE="$APP/secrets/slack-socket-app-token"
MESH_COS_LOG_ROOT="$APP/logs/deployment"
MESH_UID=65532
MESH_GID=65532
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT QNAP_SLACK_APPROVER_USER_ID_FILE
export QNAP_SLACK_VERIFIER_TOKEN_FILE QNAP_SLACK_SOCKET_APP_TOKEN_FILE
export MESH_COS_LOG_ROOT MESH_UID MESH_GID

. "$QNAP_SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh"

[ -s "$APP/secrets/slack-approver-user-id" ]
[ -s "$APP/secrets/slack-verifier-token" ]
[ -s "$APP/secrets/slack-socket-app-token" ]
grep -q -- 'image inspect image:test' "$CALLS"
grep -q -- 'openai-tunnel-runtime-key' "$CALLS"
grep -q -- 'slack-approver-user-id' "$CALLS"
grep -q -- 'slack-verifier-token' "$CALLS"
grep -q -- 'slack-socket-app-token' "$CALLS"

LOGS=$(find "$APP/logs/deployment" -type f -print)
[ -n "$LOGS" ]
if grep -R -q 'U0TESTAPPROVER\|xoxb-test-verifier\|xapp-test-socket\|tunnel-test-value' "$APP/logs/deployment"; then
  echo 'FAIL Slack HITL protected value leaked to deployment logs' >&2
  exit 1
fi

echo 'PASS Slack HITL protected provisioning uses staged candidate image and does not log protected values'
