#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
cd "$SCRIPT_ROOT"

fail() { echo "FAIL $1" >&2; exit 1; }
pass() { echo "PASS $1"; }
warn() { echo "WARN $1" >&2; }

[ -f "$APP_ROOT/.env" ] || fail "$APP_ROOT/.env missing"
set -a
. "$APP_ROOT/.env"
set +a

for name in mesh-cos-mcp mesh-cos-tunnel; do
  docker inspect "$name" >/dev/null 2>&1 || fail "missing container: $name"
  [ "$(docker inspect -f '{{.State.Health.Status}}' "$name" 2>/dev/null || echo unknown)" = "healthy" ] || fail "$name is not healthy"
done
pass "both containers healthy"

docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>{if(!r.ok)process.exit(1)})"
docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>{if(!r.ok)process.exit(1)})"
docker exec mesh-cos-mcp python3 deployment/qnap/runtime_preflight.py
pass "runtime health, readiness, and canonical preflight"

test "$(docker exec mesh-cos-mcp id -u)" = "65532" || fail "runtime UID"
test "$(docker inspect -f '{{.HostConfig.Privileged}}' mesh-cos-mcp)" = "false" || fail "privileged mode"
test "$(docker inspect -f '{{.HostConfig.ReadonlyRootfs}}' mesh-cos-mcp)" = "true" || fail "read-only root filesystem"
test "$(docker inspect -f '{{.HostConfig.NanoCpus}}' mesh-cos-mcp)" = "2000000000" || fail "2 CPU limit"
test "$(docker inspect -f '{{.HostConfig.Memory}}' mesh-cos-mcp)" = "25769803776" || fail "24 GiB memory limit"
docker exec mesh-cos-mcp test ! -S /var/run/docker.sock || fail "Docker socket present"
pass "least-privilege and resource controls"

PIDS=$(docker inspect -f '{{.HostConfig.PidsLimit}}' mesh-cos-mcp 2>/dev/null || echo unknown)
case "$PIDS" in 0|'<nil>'|-1) pass "no PID limit" ;; *) fail "unexpected PID limit: $PIDS" ;; esac

RUNNING_MESH_ID=$(docker inspect -f '{{.Image}}' mesh-cos-mcp)
[ "$RUNNING_MESH_ID" = "$MESH_COS_IMAGE_ID" ] || fail "running Mesh image differs from prepared image ID"
RUNNING_TUNNEL_ID=$(docker inspect -f '{{.Image}}' mesh-cos-tunnel)
[ "$RUNNING_TUNNEL_ID" = "$TUNNEL_IMAGE_ID" ] || fail "running tunnel image differs from prepared image ID"
pass "running containers match pinned image identities"

DIRECT_CODE=$(docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/mcp',{method:'POST',headers:{'content-type':'application/json'},body:'{}'}).then(r=>process.stdout.write(String(r.status))).catch(()=>process.exit(2))")
[ "$DIRECT_CODE" = "403" ] || fail "non-tunnel direct MCP request returned $DIRECT_CODE instead of 403"
pass "non-tunnel direct MCP request denied"

if command -v curl >/dev/null 2>&1; then
  set +e
  LAN_CODE=$(curl -sS --connect-timeout 3 --max-time 5 -o /tmp/mesh-cos-mcp-lan-denied.json -w '%{http_code}' -X POST -H 'content-type: application/json' -d '{}' http://192.168.7.60:8080/mcp)
  CURL_RC=$?
  set -e
  if [ "$CURL_RC" -eq 0 ]; then
    [ "$LAN_CODE" = "403" ] || fail "LAN MCP request returned $LAN_CODE instead of 403"
    pass "LAN MCP request denied with 403"
  else
    warn "QNAP host could not route to its qnet service IP; direct non-tunnel denial already passed and tunnel acceptance remains required"
  fi
else
  warn "curl is unavailable on the QNAP host; direct non-tunnel denial already passed"
fi

pass "local container verification complete"
echo "Mesh image ID: $RUNNING_MESH_ID"
echo "Tunnel image ID: $RUNNING_TUNNEL_ID"
docker network inspect lan7 --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}' 2>/dev/null || true
echo "NEXT: complete CHATGPT-ACCEPTANCE.md through the Secure MCP Tunnel."
