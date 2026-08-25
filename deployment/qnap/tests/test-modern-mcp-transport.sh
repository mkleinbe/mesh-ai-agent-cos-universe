#!/bin/sh
set -eu

IMAGE=${1:-mesh-cos-mcp:ci}
DEPLOYMENT_RELEASE=${MESH_COS_DEPLOYMENT_RELEASE:-4.1.7}
NAME=mesh-cos-modern-transport-test
ROOT=${TMPDIR:-/tmp}/mesh-cos-modern-transport-$$
STATE=$ROOT/state
PORT=${MESH_COS_MODERN_TEST_PORT:-18081}

cleanup() {
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  rm -rf "$ROOT" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

mkdir -p "$STATE/ledger" "$STATE/governance" "$STATE/audit" "$STATE/runtime"

docker run --rm \
  --network none \
  --user 0:0 \
  --cap-drop ALL \
  --cap-add CHOWN \
  --cap-add FOWNER \
  --cap-add DAC_OVERRIDE \
  --security-opt no-new-privileges \
  -v "$STATE:/var/lib/mesh:rw" \
  --entrypoint /bin/sh "$IMAGE" \
  -c 'chown -R 65532:65532 /var/lib/mesh && find /var/lib/mesh -type d -exec chmod 0711 {} \;' >/dev/null

docker run --rm \
  --network none \
  --user 65532:65532 \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \
  -v "$STATE:/var/lib/mesh:rw" \
  --entrypoint python3 "$IMAGE" \
  -c "from mesh_cos.ledger import TaskLedger; x=TaskLedger('/var/lib/mesh/ledger/taskledger.sqlite3'); x.conn.close()"

docker run -d --name "$NAME" \
  --network host \
  --user 65532:65532 \
  --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  -e MESH_COS_AGENT_ID=cos \
  -e MESH_COS_DEPLOYMENT_RELEASE="$DEPLOYMENT_RELEASE" \
  -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \
  -e MESH_COS_REQUIRE_EXISTING_LEDGER=true \
  -e MESH_COS_KILL_SWITCH=false \
  -e MCP_AUTH_MODE=tunnel \
  -e MCP_BIND_HOST=127.0.0.1 \
  -e MCP_PORT="$PORT" \
  -e MCP_TRUSTED_CLIENT_IP=127.0.0.1 \
  -e MESH_COS_BRIDGE_TIMEOUT_MS=30000 \
  -e MESH_COS_MAX_BRIDGE_QUEUE=32 \
  -v "$STATE:/var/lib/mesh:rw" \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=32m \
  "$IMAGE" >/dev/null

ready=0
i=0
while [ "$i" -lt 30 ]; do
  if curl -fsS "http://127.0.0.1:$PORT/readyz" >/dev/null 2>&1; then ready=1; break; fi
  i=$((i + 1))
  sleep 1
done
[ "$ready" -eq 1 ] || { docker logs "$NAME" >&2 || true; echo 'FAIL modern MCP test server did not become ready' >&2; exit 1; }

HEALTH_OUT="$ROOT/health.json"
READY_OUT="$ROOT/ready.json"
curl -fsS "http://127.0.0.1:$PORT/healthz" > "$HEALTH_OUT"
curl -fsS "http://127.0.0.1:$PORT/readyz" > "$READY_OUT"
for OUT in "$HEALTH_OUT" "$READY_OUT"; do
  grep -Fq '"mcp_version":"4.0.0"' "$OUT" || { echo 'FAIL status response missing canonical mcp_version' >&2; cat "$OUT" >&2; exit 1; }
  grep -Fq "\"deployment_release\":\"$DEPLOYMENT_RELEASE\"" "$OUT" || { echo 'FAIL status response missing deployment_release' >&2; cat "$OUT" >&2; exit 1; }
  grep -Fq '"agent_id":"cos"' "$OUT" || { echo 'FAIL status response missing cos identity' >&2; cat "$OUT" >&2; exit 1; }
  grep -Fq '"transport":"SECURE_MCP_TUNNEL"' "$OUT" || { echo 'FAIL status response missing tunnel transport identity' >&2; cat "$OUT" >&2; exit 1; }
done

META="{\"io.modelcontextprotocol/protocolVersion\":\"2026-07-28\",\"io.modelcontextprotocol/clientCapabilities\":{},\"io.modelcontextprotocol/clientInfo\":{\"name\":\"mesh-ci\",\"version\":\"$DEPLOYMENT_RELEASE\"}}"
DISCOVER_BODY="{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"server/discover\",\"params\":{\"_meta\":$META}}"
DISCOVER_OUT="$ROOT/discover.json"
STATUS=$(curl -sS -o "$DISCOVER_OUT" -w '%{http_code}' \
  -X POST \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' \
  -H 'Mcp-Method: server/discover' \
  --data "$DISCOVER_BODY" \
  "http://127.0.0.1:$PORT/mcp")
[ "$STATUS" = 200 ] || { echo "FAIL server/discover expected HTTP 200, got $STATUS" >&2; cat "$DISCOVER_OUT" >&2 || true; exit 1; }
grep -Fq '2026-07-28' "$DISCOVER_OUT" || { echo 'FAIL discovery response did not advertise 2026-07-28' >&2; cat "$DISCOVER_OUT" >&2; exit 1; }

n=1
while [ "$n" -le 10 ]; do
  BODY="{\"jsonrpc\":\"2.0\",\"id\":$((100+n)),\"method\":\"tools/list\",\"params\":{\"_meta\":$META}}"
  OUT="$ROOT/tools-$n.json"
  STATUS=$(curl -sS -o "$OUT" -w '%{http_code}' \
    -X POST \
    -H 'content-type: application/json' \
    -H 'accept: application/json, text/event-stream' \
    -H 'MCP-Protocol-Version: 2026-07-28' \
    -H 'Mcp-Method: tools/list' \
    --data "$BODY" \
    "http://127.0.0.1:$PORT/mcp")
  [ "$STATUS" = 200 ] || { echo "FAIL sequential tools/list #$n expected HTTP 200, got $STATUS" >&2; cat "$OUT" >&2 || true; exit 1; }
  grep -Fq 'registry.list_agents' "$OUT" || { echo "FAIL tools/list #$n missing canonical tool catalog" >&2; cat "$OUT" >&2; exit 1; }
  n=$((n + 1))
done

CALL_BODY="{\"jsonrpc\":\"2.0\",\"id\":500,\"method\":\"tools/call\",\"params\":{\"name\":\"registry.list_agents\",\"arguments\":{},\"_meta\":$META}}"
CALL_OUT="$ROOT/call.json"
STATUS=$(curl -sS -o "$CALL_OUT" -w '%{http_code}' \
  -X POST \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -H 'MCP-Protocol-Version: 2026-07-28' \
  -H 'Mcp-Method: tools/call' \
  -H 'Mcp-Name: registry.list_agents' \
  --data "$CALL_BODY" \
  "http://127.0.0.1:$PORT/mcp")
[ "$STATUS" = 200 ] || { echo "FAIL registry.list_agents expected HTTP 200, got $STATUS" >&2; cat "$CALL_OUT" >&2 || true; exit 1; }
grep -Fq '\"agent_id\":\"cos\"' "$CALL_OUT" || { echo 'FAIL modern tool response did not preserve cos identity' >&2; cat "$CALL_OUT" >&2; exit 1; }
grep -Fq '\"mcp_version\":\"4.0.0\"' "$CALL_OUT" || { echo 'FAIL modern tool response missing canonical mcp_version' >&2; cat "$CALL_OUT" >&2; exit 1; }
grep -Fq "\\\"deployment_release\\\":\\\"$DEPLOYMENT_RELEASE\\\"" "$CALL_OUT" || { echo 'FAIL modern tool response missing deployment_release' >&2; cat "$CALL_OUT" >&2; exit 1; }

# Security regression: the same endpoint must reject an untrusted source identity.
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" \
  --network host \
  --user 65532:65532 --read-only --cap-drop ALL --security-opt no-new-privileges \
  -e MESH_COS_AGENT_ID=cos \
  -e MESH_COS_DEPLOYMENT_RELEASE="$DEPLOYMENT_RELEASE" \
  -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \
  -e MESH_COS_REQUIRE_EXISTING_LEDGER=true \
  -e MCP_AUTH_MODE=tunnel \
  -e MCP_BIND_HOST=127.0.0.1 \
  -e MCP_PORT="$PORT" \
  -e MCP_TRUSTED_CLIENT_IP=192.0.2.1 \
  -v "$STATE:/var/lib/mesh:rw" --tmpfs /tmp:rw,noexec,nosuid,nodev,size=32m \
  "$IMAGE" >/dev/null
sleep 2
STATUS=$(curl -sS -o "$ROOT/forbidden.json" -w '%{http_code}' \
  -X POST -H 'content-type: application/json' -H 'MCP-Protocol-Version: 2026-07-28' -H 'Mcp-Method: server/discover' \
  --data "$DISCOVER_BODY" "http://127.0.0.1:$PORT/mcp")
[ "$STATUS" = 403 ] || { echo "FAIL untrusted direct MCP ingress expected HTTP 403, got $STATUS" >&2; exit 1; }

echo "PASS modern server/discover, dual release identity, 10 sequential stateless MCP requests, cos identity, and tunnel-only ingress regression for deployment $DEPLOYMENT_RELEASE"
