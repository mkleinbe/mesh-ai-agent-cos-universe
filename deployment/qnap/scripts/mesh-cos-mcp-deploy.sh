#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
COMPOSE_LIB="$SCRIPT_ROOT/mesh-cos-qnap-compose.sh"
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-deploy.sh
export QNAP_SCRIPT_ROOT QNAP_APP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init deploy || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-deploy}" "$1"; }
info() { mesh_log INFO info "$1"; }

on_signal() {
  sig=$1
  mesh_log ERROR signal "signal=$sig stage=${MESH_COS_STAGE:-unknown}"
  mesh_collect_diagnostics "deployment interrupted by signal $sig" || true
  printf 'ERROR: deployment interrupted by signal %s\n' "$sig" >&2
  printf 'DIAGNOSTIC_LOG=%s\n' "$MESH_COS_LOG_FILE" >&2
  exit 130
}
trap 'on_signal HUP' 1
trap 'on_signal INT' 2
trap 'on_signal TERM' 15

[ -r "$COMPOSE_LIB" ] || fail "Compose discovery helper is missing: $COMPOSE_LIB"
. "$COMPOSE_LIB"
mesh_resolve_compose || fail "Docker Compose V2 could not be resolved from the QNAP Container Station installation"
mesh_log INFO compose_resolved "via=$(mesh_compose_description)"

wait_healthy() {
  name=$1
  count=0
  mesh_log INFO health_wait_start "container=$name max_attempts=60 interval_seconds=2"
  while [ "$count" -lt 60 ]; do
    status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || echo missing)
    if [ "$status" = "healthy" ]; then
      mesh_log INFO health_wait_end "container=$name status=healthy attempts=$count"
      return 0
    fi
    count=$((count + 1))
    case "$count" in 1|5|10|20|30|40|50|60) mesh_log INFO health_wait "container=$name status=$status attempt=$count" ;; esac
    sleep 2
  done
  mesh_log ERROR health_wait_end "container=$name status=$status attempts=$count"
  return 1
}

run_child() {
  stage=$1
  script=$2
  shift 2
  MESH_COS_STAGE=$stage
  export MESH_COS_STAGE
  mesh_log INFO child_start "stage=$stage script=$(basename "$script")"
  sh "$script" "$@"
  rc=$?
  if [ "$rc" -eq 0 ]; then
    mesh_log INFO child_end "stage=$stage script=$(basename "$script") rc=0"
  else
    mesh_log ERROR child_end "stage=$stage script=$(basename "$script") rc=$rc"
  fi
  return "$rc"
}

mesh_set_stage bootstrap
cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$APP_ROOT" ] || fail "$APP_ROOT is missing. Extract the release bundle first."
mesh_log INFO deployment_start "app_root=$APP_ROOT log=$MESH_COS_LOG_FILE"

mesh_set_stage pre_backup
if docker inspect mesh-cos-mcp >/dev/null 2>&1 && [ "$(docker inspect -f '{{.State.Running}}' mesh-cos-mcp 2>/dev/null || echo false)" = "true" ]; then
  run_child pre_backup "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" pre-deploy || fail "pre-deploy online state/configuration backup failed"
else
  mesh_log INFO pre_backup "status=skipped reason=no-running-mesh-cos-mcp"
fi

run_child prepare "$SCRIPT_ROOT/mesh-cos-mcp-prepare.sh" || fail "prepare failed"
run_child slack_hitl_configure "$SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh" || fail "Slack HITL protected configuration failed"
run_child preflight "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh" || fail "preflight failed"

mesh_set_stage compose_render
cd "$APP_ROOT" || fail "cannot enter $APP_ROOT"
mesh_run compose_render compose-config mesh_compose --env-file .env -f compose.yaml config || fail "Compose render failed"

mesh_set_stage compose_up
mesh_run compose_up compose-up mesh_compose --env-file .env -f compose.yaml up -d --no-build || fail "Compose deployment failed"

mesh_set_stage health_wait
wait_healthy mesh-cos-mcp || fail "mesh-cos-mcp did not become healthy"
wait_healthy mesh-cos-tunnel || fail "mesh-cos-tunnel did not become healthy"

cd "$SCRIPT_ROOT" || fail "cannot return to $SCRIPT_ROOT"
run_child verify "$SCRIPT_ROOT/mesh-cos-mcp-verify.sh" || fail "post-deploy verification failed"
run_child post_backup "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" post-deploy || fail "post-deploy backup failed"

DEPLOYMENT_RELEASE=$(sed -n 's/^MESH_COS_DEPLOYMENT_RELEASE=//p' "$APP_ROOT/.env" 2>/dev/null | tail -n 1)
[ -n "$DEPLOYMENT_RELEASE" ] || DEPLOYMENT_RELEASE=unknown
mesh_set_stage complete
info "deployment, verification, and post-deploy backup complete"
mesh_log INFO deployment_complete "release=$DEPLOYMENT_RELEASE log=$MESH_COS_LOG_FILE"
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
echo "NEXT: verify the deployed OpenAI Workspace Agent can author the synthetic Slack HITL notice, then run CHATGPT-ACCEPTANCE.md and the v4.1.10 hosted acceptance procedure."
