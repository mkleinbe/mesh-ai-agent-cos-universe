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
PROMOTION_LIB="$SCRIPT_ROOT/mesh-cos-qnap-promotion.sh"
ROLLBACK_SNAPSHOT="$APP_ROOT/.release-rollback.$$"
MESH_COS_SCRIPT=mesh-cos-mcp-deploy.sh
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init deploy || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"
[ -r "$LAYOUT_LIB" ] || mesh_fail 1 bootstrap "release layout helper missing: $LAYOUT_LIB"
. "$LAYOUT_LIB"
[ -r "$PROMOTION_LIB" ] || mesh_fail 1 bootstrap "transactional promotion helper missing: $PROMOTION_LIB"
. "$PROMOTION_LIB"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-deploy}" "$1"; }
info() { mesh_log INFO info "$1"; }

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

ACTIVE_ROLLBACK_AVAILABLE=0
if [ -r "$ACTIVE_ENV" ] && [ -r "$ACTIVE_COMPOSE" ]; then
  ACTIVE_ROLLBACK_AVAILABLE=1
fi
PROMOTION_SNAPSHOT_READY=0
PROMOTION_IN_FLIGHT=0

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

stop_candidate_stack() {
  cd "$BUNDLE_APP_ROOT" || return 1
  mesh_compose --env-file "$CANDIDATE_ENV" -f "$CANDIDATE_COMPOSE" down --remove-orphans >/dev/null 2>&1 || true
  return 0
}

rollback_promoted_candidate() {
  reason=$1
  rollback_ok=1
  mesh_set_stage rollback
  mesh_log WARN promotion_rollback_start "reason=$reason snapshot_ready=$PROMOTION_SNAPSHOT_READY active_stack_available=$ACTIVE_ROLLBACK_AVAILABLE"

  if [ "$PROMOTION_SNAPSHOT_READY" -eq 1 ]; then
    if ! mesh_restore_active_configuration "$APP_ROOT" "$ROLLBACK_SNAPSHOT"; then
      rollback_ok=0
      mesh_log ERROR promotion_config_restore "result=FAIL snapshot_preserved=true snapshot=$ROLLBACK_SNAPSHOT"
    else
      mesh_log INFO promotion_config_restore "result=PASS"
    fi
  else
    rollback_ok=0
    mesh_log ERROR promotion_config_restore "result=FAIL reason=snapshot_unavailable"
  fi

  if [ "$ACTIVE_ROLLBACK_AVAILABLE" -eq 1 ]; then
    if ! restore_active_stack "$reason"; then
      rollback_ok=0
      mesh_log ERROR promotion_stack_restore "result=FAIL snapshot=$ROLLBACK_SNAPSHOT"
    fi
  else
    stop_candidate_stack || rollback_ok=0
    mesh_log INFO promotion_stack_restore "result=NO_PREVIOUS_STACK candidate_stopped=true"
  fi

  if [ "$rollback_ok" -eq 1 ]; then
    if ! mesh_cleanup_configuration_snapshot "$ROLLBACK_SNAPSHOT"; then
      rollback_ok=0
      mesh_log ERROR promotion_snapshot_cleanup "result=FAIL snapshot=$ROLLBACK_SNAPSHOT"
    else
      PROMOTION_SNAPSHOT_READY=0
    fi
  else
    mesh_log WARN promotion_snapshot_preserved "snapshot=$ROLLBACK_SNAPSHOT reason=rollback_incomplete"
  fi
  PROMOTION_IN_FLIGHT=0
  [ "$rollback_ok" -eq 1 ]
}

fail_candidate_before_promotion() {
  reason=$1
  if [ "$ACTIVE_ROLLBACK_AVAILABLE" -eq 1 ]; then
    if restore_active_stack "$reason"; then
      fail "$reason; previously active stack restored"
    fi
    fail "$reason; automatic restoration of the previously active stack also failed"
  fi
  stop_candidate_stack || true
  fail "$reason; no previously active stack was available for rollback"
}

fail_after_promotion() {
  reason=$1
  if rollback_promoted_candidate "$reason"; then
    fail "$reason; active configuration and previously active stack restored"
  fi
  fail "$reason; transactional rollback did not complete cleanly; recovery snapshot preserved at $ROLLBACK_SNAPSHOT"
}

on_signal() {
  sig=$1
  if [ "$PROMOTION_IN_FLIGHT" -eq 1 ]; then
    rollback_promoted_candidate "deployment interrupted by signal $sig" || true
  fi
  mesh_log ERROR signal "signal=$sig stage=${MESH_COS_STAGE:-unknown}"
  mesh_collect_diagnostics "deployment interrupted by signal $sig" || true
  printf 'ERROR: deployment interrupted by signal %s\n' "$sig" >&2
  printf 'DIAGNOSTIC_LOG=%s\n' "$MESH_COS_LOG_FILE" >&2
  exit 130
}
trap 'on_signal HUP' 1
trap 'on_signal INT' 2
trap 'on_signal TERM' 15

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
if docker inspect mesh-cos-mcp >/dev/null 2>&1; then
  run_child pre_backup "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" pre-deploy || fail "pre-deploy state/configuration backup failed"
else
  mesh_log INFO pre_backup "status=skipped reason=no-mesh-cos-mcp-container"
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
mesh_snapshot_active_configuration "$APP_ROOT" "$ROLLBACK_SNAPSHOT" || fail "unable to snapshot active configuration before promotion"
PROMOTION_SNAPSHOT_READY=1
PROMOTION_IN_FLIGHT=1
mesh_log INFO candidate_promotion_snapshot "snapshot_ready=true values_logged=false"
if ! mesh_promote_candidate_configuration \
  "$CANDIDATE_ENV" \
  "$CANDIDATE_COMPOSE" \
  "$BUNDLE_APP_ROOT/release-metadata.txt" \
  "$APP_ROOT"; then
  fail_after_promotion "candidate configuration promotion failed"
fi
mesh_log INFO candidate_promote "candidate_root=$BUNDLE_APP_ROOT active_root=$APP_ROOT result=PASS transactional_snapshot=true"

cd "$SCRIPT_ROOT" || fail_after_promotion "cannot return to $SCRIPT_ROOT after candidate promotion"
if ! run_child verify "$SCRIPT_ROOT/mesh-cos-mcp-verify.sh"; then
  fail_after_promotion "post-deploy verification failed"
fi

# Post-deploy verification is the transaction commit point. From here forward the
# candidate is the verified active release; cleanup failures must not attempt to
# restore a potentially partial snapshot and replace a valid running release.
PROMOTION_IN_FLIGHT=0
mesh_log INFO candidate_promotion_commit "result=PASS verification_complete=true"
if ! mesh_cleanup_configuration_snapshot "$ROLLBACK_SNAPSHOT"; then
  fail "verified candidate is active but rollback snapshot cleanup failed: $ROLLBACK_SNAPSHOT"
fi
PROMOTION_SNAPSHOT_READY=0
mesh_log INFO candidate_promotion_cleanup "result=PASS rollback_snapshot_removed=true"

run_child post_backup "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" post-deploy || fail "post-deploy backup failed after verified candidate promotion"

DEPLOYMENT_RELEASE=$(sed -n 's/^MESH_COS_DEPLOYMENT_RELEASE=//p' "$ACTIVE_ENV" 2>/dev/null | tail -n 1)
[ -n "$DEPLOYMENT_RELEASE" ] || DEPLOYMENT_RELEASE=unknown
mesh_set_stage complete
info "deployment, transactional promotion, verification, and post-deploy backup complete"
mesh_log INFO deployment_complete "release=$DEPLOYMENT_RELEASE bundle_root=$SCRIPT_ROOT log=$MESH_COS_LOG_FILE"
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
echo "NEXT: verify the ChatGPT-native Mesh Slack HITL Dispatcher is enabled, then run CHATGPT-ACCEPTANCE.md for deployment release $DEPLOYMENT_RELEASE."
