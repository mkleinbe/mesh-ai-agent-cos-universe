#!/bin/sh
set -u
TMP=${TMPDIR:-/tmp}/mesh-perm-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
mkdir -p "$TMP/state" "$TMP/secrets" "$TMP/logs"
printf 'ledger-data\n' > "$TMP/source.sqlite3"
CALLS="$TMP/docker.calls"
: > "$CALLS"
export CALLS

docker() {
  printf '%s\n' "$*" >> "$CALLS"
  return 0
}

QNAP_APP_ROOT="$TMP"
MESH_COS_LOG_ROOT="$TMP/logs"
MESH_COS_SCRIPT=test-runtime-permissions.sh
export QNAP_APP_ROOT MESH_COS_LOG_ROOT MESH_COS_SCRIPT
. "$(dirname "$0")/../scripts/mesh-cos-qnap-observability.sh"
. "$(dirname "$0")/../scripts/mesh-cos-qnap-permissions.sh"
mesh_obs_init permission-test || exit 1

mesh_apply_state_permissions image:test 65532 65532 "$TMP/state" || exit 1
mesh_stage_ledger image:test 65532 65532 "$TMP/state" "$TMP/source.sqlite3" || exit 1
printf 'secret\n' > "$TMP/secrets/openai-tunnel-runtime-key"
printf 'U0TESTAPPROVER\n' > "$TMP/secrets/slack-approver-user-id"
printf 'xoxb-test-verifier\n' > "$TMP/secrets/slack-verifier-token"
printf 'xapp-test-socket\n' > "$TMP/secrets/slack-socket-app-token"
printf 'xoxb-test-bot\n' > "$TMP/secrets/slack-bot-token"
mesh_apply_secret_permissions image:test 65532 65532 "$TMP/secrets" || exit 1

[ "$(grep -c -- '--network none' "$CALLS")" -ge 3 ]
[ "$(grep -c -- '--read-only' "$CALLS")" -ge 3 ]
[ "$(grep -c -- '--cap-drop ALL' "$CALLS")" -ge 3 ]
grep -q -- '--cap-add CHOWN' "$CALLS"
grep -q -- '--cap-add FOWNER' "$CALLS"
grep -q -- '--cap-add DAC_OVERRIDE' "$CALLS"
grep -q -- '--security-opt no-new-privileges' "$CALLS"
grep -q -- '--user 0:0' "$CALLS"
grep -q -- '--user 65532:65532' "$CALLS"
grep -q -- 'openai-tunnel-runtime-key' "$CALLS"
grep -q -- 'slack-approver-user-id' "$CALLS"
grep -q -- 'slack-verifier-token' "$CALLS"
grep -q -- 'slack-socket-app-token' "$CALLS"
grep -q -- 'slack-bot-token' "$CALLS"

if mesh_validate_runtime_identity root 65532; then
  echo 'FAIL nonnumeric UID accepted' >&2
  exit 1
fi
if mesh_validate_runtime_identity 65532 bad; then
  echo 'FAIL nonnumeric GID accepted' >&2
  exit 1
fi

echo 'PASS constrained Docker permission helpers and runtime identity validation'
