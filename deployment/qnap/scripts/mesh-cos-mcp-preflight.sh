#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
STATE_ROOT=${QNAP_MESH_ROOT:-/share/Docker/cos-mcp/state}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
SECRET_FILE=${QNAP_TUNNEL_API_KEY_FILE:-/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key}
RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"
ACTIVE_ENV_FILE="$APP_ROOT/.env"
CANDIDATE_ENV_FILE="$BUNDLE_APP_ROOT/.env.runtime"
CANDIDATE_COMPOSE="$BUNDLE_APP_ROOT/compose.yaml"
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
LAYOUT_LIB="$SCRIPT_ROOT/mesh-cos-qnap-layout.sh"
COMPOSE_LIB="$SCRIPT_ROOT/mesh-cos-qnap-compose.sh"
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-preflight.sh
FAIL=0
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT QNAP_MESH_ROOT QNAP_BACKUP_ROOT QNAP_TUNNEL_API_KEY_FILE MESH_UID MESH_GID MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init preflight || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"
[ -r "$LAYOUT_LIB" ] || mesh_fail 1 bootstrap "release layout helper missing: $LAYOUT_LIB"
. "$LAYOUT_LIB"

pass() { echo "PASS $1"; mesh_log INFO check_pass "check=$1"; }
warn() { echo "WARN $1" >&2; mesh_log WARN check_warn "check=$1"; }
fail_check() { echo "FAIL $1" >&2; mesh_log ERROR check_fail "check=$1"; FAIL=1; }

mesh_set_stage host_baseline
cd "$SCRIPT_ROOT" || mesh_fail 1 host_baseline "cannot enter $SCRIPT_ROOT"
ARCH=$(uname -m 2>/dev/null || echo unknown)
[ "$ARCH" = "x86_64" ] && pass "architecture linux/amd64" || fail_check "architecture expected x86_64, got $ARCH"
CPU=$(grep -c '^processor' /proc/cpuinfo 2>/dev/null || echo 0)
[ "$CPU" -ge 2 ] 2>/dev/null && pass "CPU count $CPU supports 2-CPU limit" || fail_check "fewer than 2 CPUs"
MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)
[ "$MEM_KB" -ge 33554432 ] 2>/dev/null && pass "RAM leaves headroom above 24-GiB container limit" || fail_check "less than 32 GiB host RAM"
command -v docker >/dev/null 2>&1 && pass "docker present" || fail_check "docker missing"
if [ -r "$COMPOSE_LIB" ]; then
  . "$COMPOSE_LIB"
  if mesh_resolve_compose; then pass "Compose V2 resolved via $(mesh_compose_description)"; else fail_check "Docker Compose V2 could not be resolved from QNAP Container Station"; fi
else
  fail_check "Compose discovery helper missing: $COMPOSE_LIB"
fi

mesh_set_stage network
LAN7=$(docker network inspect lan7 2>/dev/null || true)
echo "$LAN7" | grep -q '"Driver": "qnet"' && pass "lan7 uses qnet" || fail_check "lan7 is missing or not qnet"
echo "$LAN7" | grep -q '"Subnet": "192.168.7.0/24"' && pass "lan7 subnet" || fail_check "lan7 subnet mismatch"
echo "$LAN7" | grep -q '"Gateway": "192.168.7.1"' && pass "lan7 gateway" || fail_check "lan7 gateway mismatch"
IP_OWNER=$(docker network inspect lan7 --format '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' 2>/dev/null | awk '$2 ~ /^192\.168\.7\.60\// {print $1; exit}')
case "$IP_OWNER" in "") pass "192.168.7.60 not attached to Docker" ;; mesh-cos-mcp) pass "192.168.7.60 belongs to the existing mesh-cos-mcp endpoint" ;; *) fail_check "192.168.7.60 belongs to another Docker endpoint: $IP_OWNER" ;; esac

mesh_set_stage paths
[ -d "$APP_ROOT" ] && pass "application root exists" || fail_check "$APP_ROOT missing"
[ -d "$BUNDLE_APP_ROOT" ] && pass "versioned candidate payload exists" || fail_check "$BUNDLE_APP_ROOT missing"
[ -d "$STATE_ROOT" ] && pass "state root exists" || fail_check "$STATE_ROOT missing"
[ -d "$BACKUP_ROOT" ] && [ -w "$BACKUP_ROOT" ] && pass "quoted backup root exists and is writable" || fail_check "backup root unavailable: $BACKUP_ROOT"
[ -d "$APP_ROOT/.docker-cli" ] && [ -w "$APP_ROOT/.docker-cli" ] && pass "deployment-local Docker config exists and is writable" || fail_check "deployment-local Docker config unavailable"
[ -f "$RELEASE_METADATA" ] && pass "staged bundle release metadata exists" || fail_check "staged bundle release metadata missing: $RELEASE_METADATA"
[ -f "$CANDIDATE_COMPOSE" ] && pass "staged candidate Compose exists" || fail_check "staged candidate Compose missing: $CANDIDATE_COMPOSE"

EXPECTED_RELEASE=""
if [ -r "$RELEASE_METADATA" ]; then
  EXPECTED_RELEASE=$(mesh_candidate_release "$RELEASE_METADATA" 2>/dev/null || true)
  [ -n "$EXPECTED_RELEASE" ] && pass "staged candidate release $EXPECTED_RELEASE" || fail_check "staged bundle release metadata has invalid version"
fi

LEDGER="$STATE_ROOT/ledger/taskledger.sqlite3"
[ -f "$LEDGER" ] && pass "canonical ledger exists" || fail_check "canonical ledger missing: $LEDGER"
if command -v stat >/dev/null 2>&1 && [ -f "$LEDGER" ]; then
  LEDGER_UID=$(stat -c '%u' "$LEDGER" 2>/dev/null || echo unknown)
  LEDGER_GID=$(stat -c '%g' "$LEDGER" 2>/dev/null || echo unknown)
  LEDGER_MODE=$(stat -c '%a' "$LEDGER" 2>/dev/null || echo unknown)
  [ "$LEDGER_UID" = "$MESH_UID" ] && [ "$LEDGER_GID" = "$MESH_GID" ] && pass "canonical ledger runtime ownership" || fail_check "canonical ledger must be $MESH_UID:$MESH_GID, got $LEDGER_UID:$LEDGER_GID"
  [ "$LEDGER_MODE" = "660" ] && pass "canonical ledger mode 660" || fail_check "canonical ledger mode must be 660, got $LEDGER_MODE"
fi
[ -f "$SECRET_FILE" ] && [ -s "$SECRET_FILE" ] && pass "tunnel secret file exists and is non-empty" || fail_check "tunnel secret file missing or empty"
if command -v stat >/dev/null 2>&1 && [ -f "$SECRET_FILE" ]; then
  SECRET_UID=$(stat -c '%u' "$SECRET_FILE" 2>/dev/null || echo unknown)
  SECRET_GID=$(stat -c '%g' "$SECRET_FILE" 2>/dev/null || echo unknown)
  SECRET_MODE=$(stat -c '%a' "$SECRET_FILE" 2>/dev/null || echo unknown)
  [ "$SECRET_UID" = "$MESH_UID" ] && [ "$SECRET_GID" = "$MESH_GID" ] && pass "tunnel secret ownership" || fail_check "tunnel secret must be $MESH_UID:$MESH_GID"
  [ "$SECRET_MODE" = "400" ] && pass "tunnel secret mode 400" || fail_check "tunnel secret mode must be 400, got $SECRET_MODE"
fi

mesh_set_stage environment
if [ -f "$ACTIVE_ENV_FILE" ]; then
  ACTIVE_RELEASE=$(sed -n 's/^MESH_COS_DEPLOYMENT_RELEASE=//p' "$ACTIVE_ENV_FILE" | tail -n 1 | sed 's/^"//;s/"$//')
  [ -n "$ACTIVE_RELEASE" ] && pass "active deployment release $ACTIVE_RELEASE" || warn "active deployment release is not recorded"
  if [ -n "$EXPECTED_RELEASE" ] && [ -n "$ACTIVE_RELEASE" ] && [ "$ACTIVE_RELEASE" != "$EXPECTED_RELEASE" ]; then
    pass "active release may differ before candidate promotion"
  fi
else
  warn "active .env missing; install path will require preparation"
fi

if [ -f "$CANDIDATE_ENV_FILE" ]; then
  pass "staged candidate runtime environment exists"
  set -a
  . "$CANDIDATE_ENV_FILE"
  set +a
  [ "${MESH_COS_DEPLOYMENT_RELEASE:-}" = "$EXPECTED_RELEASE" ] && pass "candidate deployment release $EXPECTED_RELEASE" || fail_check "candidate MESH_COS_DEPLOYMENT_RELEASE must match staged bundle release $EXPECTED_RELEASE"
  [ "${MESH_CPU_LIMIT:-}" = "2.0" ] && pass "2-CPU limit configured" || fail_check "MESH_CPU_LIMIT must be 2.0"
  [ "${MESH_MEMORY_LIMIT:-}" = "24g" ] && pass "24-GiB memory limit configured" || fail_check "MESH_MEMORY_LIMIT must be 24g"
  grep -q '^MESH_PIDS_LIMIT=' "$CANDIDATE_ENV_FILE" && fail_check "PID limit must not be configured" || pass "no PID limit configured"
  case "${MESH_COS_IMAGE_ID:-}" in sha256:*) pass "Mesh image ID recorded" ;; *) fail_check "MESH_COS_IMAGE_ID must be recorded" ;; esac
  ACTUAL_MESH_ID=$(docker image inspect --format '{{.Id}}' "${MESH_COS_IMAGE:-missing}" 2>/dev/null || true)
  [ -n "$ACTUAL_MESH_ID" ] && [ "$ACTUAL_MESH_ID" = "${MESH_COS_IMAGE_ID:-}" ] && pass "candidate Mesh tag resolves to recorded immutable image ID" || fail_check "candidate Mesh image identity mismatch"
  printf '%s' "${TUNNEL_IMAGE:-}" | grep -Eq '^ghcr\.io/openai/tunnel-client@sha256:[0-9a-fA-F]{64}$' && pass "tunnel image uses RepoDigest" || fail_check "tunnel image must use immutable RepoDigest"
  ACTUAL_TUNNEL_ID=$(docker image inspect --format '{{.Id}}' "${TUNNEL_IMAGE:-missing}" 2>/dev/null || true)
  [ -n "$ACTUAL_TUNNEL_ID" ] && [ "$ACTUAL_TUNNEL_ID" = "${TUNNEL_IMAGE_ID:-}" ] && pass "tunnel RepoDigest resolves to recorded image ID" || fail_check "tunnel image identity mismatch"
  printf '%s' "${CONTROL_PLANE_TUNNEL_ID:-}" | grep -Eq '^tunnel_[0-9a-fA-F]{32}$' && pass "tunnel_id format" || fail_check "invalid CONTROL_PLANE_TUNNEL_ID"
  if [ -n "${MESH_COS_IMAGE:-}" ] && docker image inspect "$MESH_COS_IMAGE" >/dev/null 2>&1; then
    if mesh_run runtime_permissions runtime-state-access docker run --rm --network none --read-only --user "$MESH_UID:$MESH_GID" --cap-drop ALL --security-opt no-new-privileges -v "$STATE_ROOT:/var/lib/mesh:rw" --entrypoint /bin/sh "$MESH_COS_IMAGE" -c 'test -r /var/lib/mesh/ledger/taskledger.sqlite3 && test -w /var/lib/mesh/ledger/taskledger.sqlite3'; then
      pass "canonical ledger is read/write for candidate runtime UID/GID"
    else
      fail_check "canonical ledger is not read/write for candidate runtime UID/GID"
    fi
  fi
else
  pass "candidate runtime environment not yet prepared; active release remains untouched"
fi

mesh_set_stage capacity
if [ -d "$APP_ROOT" ]; then
  FREE_KB=$(df -Pk "$APP_ROOT" 2>/dev/null | awk 'NR==2 {print $4}')
  USED_PCT=$(df -Pk "$APP_ROOT" 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
  [ "${FREE_KB:-0}" -ge 20971520 ] 2>/dev/null && pass "at least 20 GiB free on application filesystem" || fail_check "less than 20 GiB free"
  [ "${USED_PCT:-100}" -ge 95 ] 2>/dev/null && warn "application filesystem is ${USED_PCT}% used; absolute free-space gate passes but QNAP capacity/snapshot headroom should be monitored" || true
fi

mesh_set_stage compose_render
if [ -f "$CANDIDATE_ENV_FILE" ] && command -v mesh_compose >/dev/null 2>&1; then
  cd "$BUNDLE_APP_ROOT" || fail_check "cannot enter candidate application payload for Compose render"
  if mesh_run compose_render compose-config mesh_compose --env-file "$CANDIDATE_ENV_FILE" -f "$CANDIDATE_COMPOSE" config; then pass "staged candidate Compose renders"; else fail_check "staged candidate Compose render failed"; fi
  cd "$SCRIPT_ROOT" 2>/dev/null || true
else
  pass "staged candidate Compose render deferred until prepare creates .env.runtime"
fi

if [ "$FAIL" -ne 0 ]; then
  MESH_COS_STAGE=preflight_failed
  export MESH_COS_STAGE
  mesh_log ERROR preflight_complete "result=FAIL candidate_release=${EXPECTED_RELEASE:-unknown}"
  mesh_collect_diagnostics "one or more QNAP host/candidate preflight checks failed" || true
  echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE" >&2
  exit 1
fi
mesh_log INFO preflight_complete "result=PASS candidate_release=${EXPECTED_RELEASE:-unknown}"
pass "QNAP host and staged-candidate preflight complete"
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
