#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
cd "$SCRIPT_ROOT"

for name in mesh-cos-mcp mesh-cos-tunnel; do
  docker inspect "$name" >/dev/null 2>&1 || { echo "FAIL missing container: $name" >&2; exit 1; }
done

docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>{if(!r.ok)process.exit(1)})"
docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>{if(!r.ok)process.exit(1)})"
docker exec mesh-cos-mcp python3 deployment/qnap/runtime_preflight.py

test "$(docker exec mesh-cos-mcp id -u)" = "65532"
test "$(docker inspect -f '{{.HostConfig.Privileged}}' mesh-cos-mcp)" = "false"
test "$(docker inspect -f '{{.HostConfig.ReadonlyRootfs}}' mesh-cos-mcp)" = "true"
test "$(docker inspect -f '{{.HostConfig.NanoCpus}}' mesh-cos-mcp)" = "2000000000"
test "$(docker inspect -f '{{.HostConfig.Memory}}' mesh-cos-mcp)" = "25769803776"
docker exec mesh-cos-mcp test ! -S /var/run/docker.sock

if docker inspect -f '{{.HostConfig.PidsLimit}}' mesh-cos-mcp 2>/dev/null | grep -Eq '(^0$|^<nil>$|^-1$)'; then
  echo "PASS no PID limit"
else
  echo "WARN Docker reports a PID setting; inspect manually" >&2
fi

echo "Mesh image: $(docker inspect -f '{{.Image}}' mesh-cos-mcp)"
echo "Tunnel image: $(docker inspect -f '{{.Image}}' mesh-cos-tunnel)"
docker network inspect lan7 --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}' 2>/dev/null || true

echo "PASS local container verification"
echo "Next: from an authorized LAN workstation confirm POST http://192.168.7.60:8080/mcp returns 403, then complete the ChatGPT tunnel acceptance tests."
