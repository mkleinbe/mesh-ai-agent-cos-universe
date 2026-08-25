#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
STATE_ROOT=${QNAP_MESH_ROOT:-/share/Docker/cos-mcp/state}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
SECRET_FILE=${QNAP_TUNNEL_API_KEY_FILE:-/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key}
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
FAIL=0

pass() { echo "PASS $1"; }
warn() { echo "WARN $1" >&2; }
fail() { echo "FAIL $1" >&2; FAIL=1; }

cd "$SCRIPT_ROOT" || exit 1

ARCH=$(uname -m 2>/dev/null || echo unknown)
[ "$ARCH" = "x86_64" ] && pass "architecture linux/amd64" || fail "architecture expected x86_64, got $ARCH"
CPU=$(grep -c '^processor' /proc/cpuinfo 2>/dev/null || echo 0)
[ "$CPU" -ge 2 ] && pass "CPU count $CPU supports 2-CPU limit" || fail "fewer than 2 CPUs"
MEM_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)
[ "$MEM_KB" -ge 33554432 ] && pass "RAM leaves headroom above 24-GiB container limit" || fail "less than 32 GiB host RAM"

command -v docker >/dev/null 2>&1 && pass "docker present" || fail "docker missing"
docker compose version >/dev/null 2>&1 && pass "docker compose present" || fail "docker compose missing"
LAN7=$(docker network inspect lan7 2>/dev/null || true)
echo "$LAN7" | grep -q '"Driver": "qnet"' && pass "lan7 uses qnet" || fail "lan7 is missing or not qnet"
echo "$LAN7" | grep -q '"Subnet": "192.168.7.0/24"' && pass "lan7 subnet" || fail "lan7 subnet mismatch"
echo "$LAN7" | grep -q '"Gateway": "192.168.7.1"' && pass "lan7 gateway" || fail "lan7 gateway mismatch"
IP_OWNER=$(docker network inspect lan7 --format '{{range .Containers}}{{println .Name .IPv4Address}}{{end}}' 2>/dev/null | awk '$2 ~ /^192\.168\.7\.60\// {print $1; exit}')
case "$IP_OWNER" in
  "") pass "192.168.7.60 not attached to Docker" ;;
  mesh-cos-mcp) pass "192.168.7.60 belongs to the existing mesh-cos-mcp endpoint" ;;
  *) fail "192.168.7.60 belongs to another Docker endpoint: $IP_OWNER" ;;
esac
if ping -c 1 -W 1 192.168.7.60 >/dev/null 2>&1; then
  if [ "$IP_OWNER" = "mesh-cos-mcp" ]; then
    pass "192.168.7.60 responds as the existing Mesh service"
  else
    fail "192.168.7.60 answered ping without the expected Mesh endpoint; investigate LAN conflict"
  fi
else
  [ -z "$IP_OWNER" ] && warn "192.168.7.60 did not answer ping; this reduces but does not eliminate non-Docker LAN-conflict risk" || true
fi

[ -d "$APP_ROOT" ] && pass "application root exists" || fail "$APP_ROOT missing"
[ -d "$STATE_ROOT" ] && pass "state root exists" || fail "$STATE_ROOT missing"
[ -d "$BACKUP_ROOT" ] && [ -w "$BACKUP_ROOT" ] && pass "quoted backup root exists and is writable" || fail "backup root unavailable: $BACKUP_ROOT"
LEDGER="$STATE_ROOT/ledger/taskledger.sqlite3"
[ -f "$LEDGER" ] && pass "canonical ledger exists" || fail "canonical ledger missing: $LEDGER"
[ -r "$LEDGER" ] && [ -w "$LEDGER" ] && pass "canonical ledger read/write" || fail "canonical ledger permissions"
[ -f "$SECRET_FILE" ] && [ -s "$SECRET_FILE" ] && pass "tunnel secret file exists and is non-empty" || fail "tunnel secret file missing or empty"

if command -v stat >/dev/null 2>&1 && [ -f "$SECRET_FILE" ]; then
  SECRET_UID=$(stat -c '%u' "$SECRET_FILE" 2>/dev/null || echo unknown)
  SECRET_GID=$(stat -c '%g' "$SECRET_FILE" 2>/dev/null || echo unknown)
  SECRET_MODE=$(stat -c '%a' "$SECRET_FILE" 2>/dev/null || echo unknown)
  [ "$SECRET_UID" = "$MESH_UID" ] && [ "$SECRET_GID" = "$MESH_GID" ] && pass "tunnel secret ownership" || fail "tunnel secret must be $MESH_UID:$MESH_GID"
  [ "$SECRET_MODE" = "400" ] && pass "tunnel secret mode 400" || fail "tunnel secret mode must be 400, got $SECRET_MODE"
fi

[ -f "$APP_ROOT/.env" ] && pass ".env exists" || fail ".env missing"
[ -f "$APP_ROOT/compose.yaml" ] && pass "compose.yaml exists" || fail "compose.yaml missing"
if [ -f "$APP_ROOT/.env" ]; then
  set -a
  . "$APP_ROOT/.env"
  set +a
  [ "${MESH_COS_DEPLOYMENT_RELEASE:-}" = "4.1.1" ] && pass "deployment release 4.1.1" || fail "MESH_COS_DEPLOYMENT_RELEASE must be 4.1.1"
  [ "${MESH_CPU_LIMIT:-}" = "2.0" ] && pass "2-CPU limit configured" || fail "MESH_CPU_LIMIT must be 2.0"
  [ "${MESH_MEMORY_LIMIT:-}" = "24g" ] && pass "24-GiB memory limit configured" || fail "MESH_MEMORY_LIMIT must be 24g"
  grep -q '^MESH_PIDS_LIMIT=' "$APP_ROOT/.env" && fail "PID limit must not be configured" || pass "no PID limit configured"
  case "${MESH_COS_IMAGE_ID:-}" in sha256:*) pass "Mesh image ID recorded" ;; *) fail "MESH_COS_IMAGE_ID must be recorded" ;; esac
  ACTUAL_MESH_ID=$(docker image inspect --format '{{.Id}}' "${MESH_COS_IMAGE:-missing}" 2>/dev/null || true)
  [ -n "$ACTUAL_MESH_ID" ] && [ "$ACTUAL_MESH_ID" = "${MESH_COS_IMAGE_ID:-}" ] && pass "local Mesh tag resolves to recorded immutable image ID" || fail "Mesh image identity mismatch"
  printf '%s' "${TUNNEL_IMAGE:-}" | grep -Eq '^ghcr\.io/openai/tunnel-client@sha256:[0-9a-fA-F]{64}$' && pass "tunnel image uses RepoDigest" || fail "tunnel image must use immutable ghcr.io/openai/tunnel-client RepoDigest"
  ACTUAL_TUNNEL_ID=$(docker image inspect --format '{{.Id}}' "${TUNNEL_IMAGE:-missing}" 2>/dev/null || true)
  [ -n "$ACTUAL_TUNNEL_ID" ] && [ "$ACTUAL_TUNNEL_ID" = "${TUNNEL_IMAGE_ID:-}" ] && pass "tunnel RepoDigest resolves to recorded image ID" || fail "tunnel image identity mismatch"
  printf '%s' "${CONTROL_PLANE_TUNNEL_ID:-}" | grep -Eq '^tunnel_[0-9a-fA-F]{32}$' && pass "tunnel_id format" || fail "invalid CONTROL_PLANE_TUNNEL_ID"
fi

if [ -d "$APP_ROOT" ]; then
  FREE_KB=$(df -Pk "$APP_ROOT" 2>/dev/null | awk 'NR==2 {print $4}')
  USED_PCT=$(df -Pk "$APP_ROOT" 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
  [ "${FREE_KB:-0}" -ge 20971520 ] && pass "at least 20 GiB free on application filesystem" || fail "less than 20 GiB free"
  [ "${USED_PCT:-100}" -ge 95 ] && warn "application filesystem is ${USED_PCT}% used; absolute free-space gate passes but QNAP capacity/snapshot headroom should be monitored" || true
fi

if [ -f "$APP_ROOT/compose.yaml" ] && [ -f "$APP_ROOT/.env" ]; then
  (cd "$APP_ROOT" && docker compose --env-file .env -f compose.yaml config >/tmp/mesh-cos-mcp-compose.rendered.yaml) && pass "Compose renders" || fail "Compose render failed"
fi

[ "$FAIL" -eq 0 ] || exit 1
pass "QNAP host preflight complete"
