#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
CANDIDATE_ENV="$BUNDLE_APP_ROOT/.env.runtime"
CANDIDATE_COMPOSE="$BUNDLE_APP_ROOT/compose.yaml"
ACTIVE_ENV="$APP_ROOT/.env"
ACTIVE_COMPOSE="$APP_ROOT/compose.yaml"
LAYOUT_LIB="$SCRIPT_ROOT/mesh-cos-qnap-layout.sh"
COMPOSE_LIB="$SCRIPT_ROOT/mesh-cos-qnap-compose.sh"
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-deploy.sh
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init deploy || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"
[ -r "$LAYOUT_LIB" ] || mesh_fail 1 bootstrap "release layout helper missing: $LAYOUT_LIB"
. "$LAYOUT_LIB"

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

promote_candidate_file() {
  promote_source=$1
  promote_target=$2
  promote_mode=$3
  promote_incoming="$promote_target.incoming.$$"
  cp "$promote_source" "$promote_incoming" || return 1
  chmod "$promote_mode" "$promote_incoming" 2>/dev/null || return 1
  mv "$promote_incoming" "$promote_target" || return 1
}

ACTIVE_ROLLBACK_AVAILABLE=0
if [ -r "$ACTIVE_ENV" ] && [ -r "$ACTIVE_COMPOSE" ]; then
  ACTIVE_ROLLBACK_AVAILABLE=1
fi

restore_active_stack() {
  reason=$1
  [ "$ACTIVE_ROLLBACK_AVAILABLE" -eq 1 ] || return 1
  mesh_set_stage rollback
  mesh_log WARN rollback_start "reason=$reason active_env=$ACTIVE_ENV active_compose=$ACTIVE_COMPOSE"

  cd "$BUNDLE_APP_ROOT" || return 1
  mesh_compose --env-file "$CANDIDATE_ENV" -f "$CANDIDATE_COMPOSE" down --remove-orphans >/dev/null 2>&1 || true

  cd "$APP_ROOT" || return 1
  mesh_run rollback active-compose-up mesh_compose --env-file "$ACTIVE_ENV" -f "$ACTIVE_COMPOSE" up -d --no-build || return 1
  wait_healthy mesh-cos-mcp || return 1
  wait_healthy mesh-cos-tunnel || return 1
  mesh_log INFO rollback_complete "result=PASS active_release_preserved=true"
  return 0
}

fail_candidate_before_promotion() {
  reason=$1
  if [ "$ACTIVE_ROLLBACK_AVAILABLE" -eq 1 ]; then
    if restore_active_stack "$reason"; then
      fail "$reason; previously active stack restored"
    fi
    fail "$reason; automatic restoration of the previously active stack also failed"
  fi
  fail "$reason; no previously active stack was available for rollback"
}

mesh_set_stage bootstrap
cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$BUNDLE_APP_ROOT" ] || fail "candidate application payload missing: $BUNDLE_APP_ROOT"
[ -r "$BUNDLE_APP_ROOT/release-metadata.txt" ] || fail "candidate release metadata missing: $BUNDLE_APP_ROOT/release-metadata.txt"
[ -r "$CANDIDATE_COMPOSE" ] || fail "candidate Compose file missing: $CANDIDATE_COMPOSE"
[ -d "$APP_ROOT" ] || fail "$APP_ROOT is missing; canonical runtime root must already exist"
mesh_validate_release_root "$SCRIPT_ROOT" "$BUNDLE_APP_ROOT/release-metadata.txt" || fail "release-root validation failed before candidate preparation"
mesh_log INFO deployment_start "bundle_root=$SCRIPT_ROOT candidate_root=$BUNDLE_APP_ROOT app_root=$APP_ROOT releases_root=${QNAP_RELEASES_ROOT:-/share/Docker/cos-mcp/releases} log=$MESH_COS_LOG_FILE"
mesh_log INFO rollback_preflight "available=$ACTIVE_ROLLBACK_AVAILABLE active_configuration_promoted=false"

mesh_set_stage pre_backup
if docker inspect mesh-cos-mcp >/dev/null 2>&1 && [ "$(docker inspect -f '{{.State.Running}}' mesh-cos-mcp 2>/dev/null || echo false)" = "true" ]; then
  run_child pre_backup "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" pre-deploy || fail "pre-deploy online state/configuration backup failed"
else
  mesh_log INFO pre_backup "status=skipped reason=no-running-mesh-cos-mcp"
fi

run_child prepare "$SCRIPT_ROOT/mesh-cos-mcp-prepare.sh" || fail "prepare failed"
[ -r "$CANDIDATE_ENV" ] || fail "prepare did not produce candidate runtime environment: $CANDIDATE_ENV"
run_child slack_hitl_configure "$SCRIPT_ROOT/mesh-cos-slack-hitl-configure.sh" || fail "Slack HITL protected configuration failed"
run_child preflight "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh" || fail "preflight failed"

mesh_set_stage compose_render
cd "$BUNDLE_APP_ROOT" || fail "cannot enter candidate application payload $BUNDLE_APP_ROOT"
mesh_run compose_render compose-config mesh_compose --env-file "$CANDIDATE_ENV" -f "$CANDIDATE_COMPOSE" config || fail "candidate Compose render failed"

mesh_set_stage compose_up
if ! mesh_run compose_up compose-up mesh_compose --env-file "$CANDIDATE_ENV" -f "$CANDIDATE_COMPOSE" up -d --no-build; then
  fail_candidate_before_promotion "candidate Compose deployment failed"
fi

mesh_set_stage health_wait
wait_healthy mesh-cos-mcp || fail_candidate_before_promotion "candidate mesh-cos-mcp did not become healthy"
wait_healthy mesh-cos-tunnel || fail_candidate_before_promotion "candidate mesh-cos-tunnel did not become healthy"

mesh_set_stage candidate_promote
promote_candidate_file "$CANDIDATE_ENV" "$ACTIVE_ENV" 0640 || fail "unable to promote candidate runtime environment"
promote_candidate_file "$CANDIDATE_COMPOSE" "$ACTIVE_COMPOSE" 0644 || fail "unable to promote candidate Compose file"
promote_candidate_file "$BUNDLE_APP_ROOT/release-metadata.txt" "$APP_ROOT/release-metadata.txt" 0644 || fail "unable to promote candidate release metadata"
mesh_log INFO candidate_promote "candidate_root=$BUNDLE_APP_ROOT active_root=$APP_ROOT result=PASS"

cd "$SCRIPT_ROOT" || fail "cannot return to $SCRIPT_ROOT"
run_child verify "$SCRIPT_ROOT/mesh-cos-mcp-verify.sh" || fail "post-deploy verification failed"
run_child post_backup "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" post-deploy || fail "post-deploy backup failed"

DEPLOYMENT_RELEASE=$(sed -n 's/^MESH_COS_DEPLOYMENT_RELEASE=//p' "$ACTIVE_ENV" 2>/dev/null | tail -n 1)
[ -n "$DEPLOYMENT_RELEASE" ] || DEPLOYMENT_RELEASE=unknown
mesh_set_stage complete
info "deployment, promotion, verification, and post-deploy backup complete"
mesh_log INFO deployment_complete "release=$DEPLOYMENT_RELEASE bundle_root=$SCRIPT_ROOT log=$MESH_COS_LOG_FILE"
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
echo "NEXT: verify connected Slack collaboration and the authenticated /mesh-approval Socket Mode ingress, then run CHATGPT-ACCEPTANCE.md for deployment release $DEPLOYMENT_RELEASE."
