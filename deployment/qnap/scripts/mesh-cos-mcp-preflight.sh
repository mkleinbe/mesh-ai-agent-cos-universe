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
echo "$LAN7" | grep -q '192.168.7.60' && fail "192.168.7.60 already attached to a Docker endpoint" || pass "192.168.7.60 not attached to Docker"
if ping -c 1 -W 1 192.168.7.60 >/dev/null 2>&1; then
  fail "192.168.7.60 answered ping; investigate LAN conflict"
else
  warn "192.168.7.60 did not answer ping; this reduces but does not eliminate LAN-conflict risk"
fi

[ -d "$APP_ROOT" ] && pass "application root exists" || fail "$APP_ROOT missing"
[ -d "$STATE_ROOT" ] && pass "state root exists" || fail "$STATE_ROOT missing"
[ -d "$BACKUP_ROOT" ] && [ -w "$BACKUP_ROOT" ] && pass "quoted backup root exists and is writable" || fail "backup root unavailable: $BACKUP_ROOT"
LEDGER="$STATE_ROOT/ledger/taskledger.sqlite3"
[ -f "$LEDGER" ] && pass "canonical ledger exists" || fail "canonical ledger missing: $LEDGER"
[ -r "$LEDGER" ] && [ -w "$LEDGER" ] && pass "canonical ledger read/write" || fail "canonical ledger permissions"
[ -f "$SECRET_FILE" ] && pass "tunnel secret file exists" || fail "tunnel secret file missing"

if command -v stat >/dev/null 2>&1 && [ -f "$SECRET_FILE" ]; then
  SECRET_UID=$(stat -c '%u' "$SECRET_FILE" 2>/dev/null || echo unknown)
  SECRET_GID=$(stat -c '%g' "$SECRET_FILE" 2>/dev/null || echo unknown)
  SECRET_MODE=$(stat -c '%a' "$SECRET_FILE" 2>/dev/null || echo unknown)
  [ "$SECRET_UID" = "$MESH_UID" ] && [ "$SECRET_GID" = "$MESH_GID" ] && pass "tunnel secret ownership" || fail "tunnel secret must be $MESH_UID:$MESH_GID"
  case "$SECRET_MODE" in 400|440|600|640) pass "tunnel secret mode $SECRET_MODE" ;; *) fail "tunnel secret mode too broad: $SECRET_MODE" ;; esac
fi

[ -f "$APP_ROOT/.env" ] && pass ".env exists" || fail ".env missing"
[ -f "$APP_ROOT/compose.yaml" ] && pass "compose.yaml exists" || fail "compose.yaml missing"
if [ -f "$APP_ROOT/.env" ]; then
  grep -q '^MESH_CPU_LIMIT=2\.0$' "$APP_ROOT/.env" && pass "2-CPU limit configured" || fail "MESH_CPU_LIMIT must be 2.0"
  grep -q '^MESH_MEMORY_LIMIT=24g$' "$APP_ROOT/.env" && pass "24-GiB memory limit configured" || fail "MESH_MEMORY_LIMIT must be 24g"
  grep -q '^MESH_PIDS_LIMIT=' "$APP_ROOT/.env" && fail "PID limit must not be configured" || pass "no PID limit configured"
  grep -q '^MESH_COS_IMAGE=.*@sha256:' "$APP_ROOT/.env" && pass "Mesh image uses digest" || fail "Mesh image must use immutable digest"
  grep -q '^TUNNEL_IMAGE=.*@sha256:' "$APP_ROOT/.env" && pass "tunnel image uses digest" || fail "tunnel image must use immutable digest"
fi

if [ -d "$APP_ROOT" ]; then
  FREE_KB=$(df -Pk "$APP_ROOT" 2>/dev/null | awk 'NR==2 {print $4}')
  USED_PCT=$(df -Pk "$APP_ROOT" 2>/dev/null | awk 'NR==2 {gsub(/%/,"",$5); print $5}')
  [ "${FREE_KB:-0}" -ge 20971520 ] && pass "at least 20 GiB free on application filesystem" || fail "less than 20 GiB free"
  [ "${USED_PCT:-100}" -ge 95 ] && warn "application filesystem is ${USED_PCT}% used; probe showed large absolute free space but QNAP capacity/snapshot headroom should be monitored" || true
fi

if [ -f "$APP_ROOT/compose.yaml" ] && [ -f "$APP_ROOT/.env" ]; then
  (cd "$APP_ROOT" && docker compose --env-file .env -f compose.yaml config >/tmp/mesh-cos-mcp-compose.rendered.yaml) && pass "Compose renders" || fail "Compose render failed"
fi

[ "$FAIL" -eq 0 ] || exit 1
pass "QNAP host preflight complete"
