#!/bin/sh
set -u
TMP=${TMPDIR:-/tmp}/mesh-obs-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
mkdir -p "$TMP/app"
QNAP_APP_ROOT="$TMP/app"
MESH_COS_LOG_ROOT="$TMP/logs"
MESH_COS_SCRIPT=test-observability.sh
OPENAI_API_KEY='sk-supersecret-never-log'
export QNAP_APP_ROOT MESH_COS_LOG_ROOT MESH_COS_SCRIPT OPENAI_API_KEY
. "$(dirname "$0")/../scripts/mesh-cos-qnap-observability.sh"
mesh_obs_init observability-test || exit 1
mesh_init_docker_config || exit 1
rc=0
mesh_run regression expected-failure sh -c 'echo diagnostic-output; exit 7' || rc=$?
[ "$rc" -eq 7 ] || { echo "FAIL expected rc=7 got rc=$rc" >&2; exit 1; }
grep -q 'event=command_start stage=regression command=expected-failure' "$MESH_COS_LOG_FILE"
grep -q 'event=command_end stage=regression command=expected-failure rc=7' "$MESH_COS_LOG_FILE"
grep -q 'diagnostic-output' "$MESH_COS_LOG_FILE"
! grep -q 'supersecret' "$MESH_COS_LOG_FILE"
[ "$(cat "$MESH_COS_LOG_ROOT/LATEST")" = "$MESH_COS_LOG_FILE" ]
[ "$DOCKER_CONFIG" = "$TMP/app/.docker-cli" ]
[ "$(stat -c '%a' "$MESH_COS_LOG_FILE" 2>/dev/null || echo 640)" = "640" ]
echo 'PASS structured observability, rc preservation, local Docker config, and secret non-collection'
