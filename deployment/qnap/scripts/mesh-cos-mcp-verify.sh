#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-verify.sh
export QNAP_SCRIPT_ROOT QNAP_APP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init verify || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-verify}" "$1"; }
pass() { echo "PASS $1"; mesh_log INFO verify_pass "check=$1"; }
warn() { echo "WARN $1" >&2; mesh_log WARN verify_warn "check=$1"; }

mesh_set_stage verify_environment
cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -f "$APP_ROOT/.env" ] || fail "$APP_ROOT/.env missing"
set -a
. "$APP_ROOT/.env"
set +a
[ -n "${MESH_COS_DEPLOYMENT_RELEASE:-}" ] || fail "MESH_COS_DEPLOYMENT_RELEASE missing from .env"

mesh_set_stage container_health
for name in mesh-cos-mcp mesh-cos-tunnel; do
  docker inspect "$name" >/dev/null 2>&1 || fail "missing container: $name"
  [ "$(docker inspect -f '{{.State.Health.Status}}' "$name" 2>/dev/null || echo unknown)" = "healthy" ] || fail "$name is not healthy"
done
pass "both containers healthy"

mesh_set_stage runtime_readiness
IDENTITY_CHECK="fetch('http://127.0.0.1:8080/STATUS').then(async r=>{const j=await r.json();if(!r.ok||j.ok!==true||j.mcp_version!=='4.0.0'||j.deployment_release!==process.env.EXPECTED_RELEASE||j.agent_id!=='cos'||j.transport!=='SECURE_MCP_TUNNEL')process.exit(1)})"
mesh_run runtime_readiness healthz docker exec -e EXPECTED_RELEASE="$MESH_COS_DEPLOYMENT_RELEASE" mesh-cos-mcp node -e "$(printf '%s' "$IDENTITY_CHECK" | sed 's/STATUS/healthz/g')" || fail "healthz identity check failed"
mesh_run runtime_readiness readyz docker exec -e EXPECTED_RELEASE="$MESH_COS_DEPLOYMENT_RELEASE" mesh-cos-mcp node -e "$(printf '%s' "$IDENTITY_CHECK" | sed 's/STATUS/readyz/g')" || fail "readyz identity check failed"
mesh_run runtime_readiness runtime-preflight docker exec mesh-cos-mcp python3 deployment/qnap/runtime_preflight.py || fail "canonical runtime preflight failed"
pass "runtime health, readiness, dual release identity, and canonical preflight"

MCP_ENVELOPE_CHECK="const expected=process.env.EXPECTED_RELEASE;const meta={'io.modelcontextprotocol/protocolVersion':'2026-07-28','io.modelcontextprotocol/clientCapabilities':{},'io.modelcontextprotocol/clientInfo':{name:'mesh-qnap-verify',version:expected}};const body={jsonrpc:'2.0',id:'verify-envelope',method:'tools/call',params:{name:'registry.get_agent',arguments:{agent_id:'cos'},_meta:meta}};fetch('http://172.30.60.2:8080/mcp',{method:'POST',headers:{'content-type':'application/json','accept':'application/json, text/event-stream','MCP-Protocol-Version':'2026-07-28','Mcp-Method':'tools/call','Mcp-Name':'registry.get_agent'},body:JSON.stringify(body)}).then(async r=>{if(!r.ok)throw new Error('http_'+r.status);const outer=JSON.parse(await r.text());const content=outer&&outer.result&&outer.result.content;if(!Array.isArray(content))throw new Error('missing_content');const item=content.find(x=>x&&x.type==='text');if(!item||typeof item.text!=='string')throw new Error('missing_text');const envelope=JSON.parse(item.text);if(envelope.ok!==true||envelope.mcp_version!=='4.0.0'||envelope.deployment_release!==expected||envelope.agent_id!=='cos'||!envelope.result)throw new Error('identity_mismatch')}).catch(()=>process.exit(1))"
mesh_run runtime_readiness governed-tool-envelope \
  docker run --rm \
    --network container:mesh-cos-tunnel \
    --read-only \
    --user 65532:65532 \
    --cap-drop ALL \
    --security-opt no-new-privileges \
    --tmpfs /tmp:rw,noexec,nosuid,nodev,size=16m \
    -e EXPECTED_RELEASE="$MESH_COS_DEPLOYMENT_RELEASE" \
    --entrypoint node "$MESH_COS_IMAGE_ID" -e "$MCP_ENVELOPE_CHECK" || fail "governed MCP tool response envelope identity check failed"
pass "governed tool envelope dual release identity"

mesh_set_stage runtime_controls
test "$(docker exec mesh-cos-mcp id -u)" = "65532" || fail "runtime UID"
test "$(docker inspect -f '{{.HostConfig.Privileged}}' mesh-cos-mcp)" = "false" || fail "privileged mode"
test "$(docker inspect -f '{{.HostConfig.ReadonlyRootfs}}' mesh-cos-mcp)" = "true" || fail "read-only root filesystem"
test "$(docker inspect -f '{{.HostConfig.NanoCpus}}' mesh-cos-mcp)" = "2000000000" || fail "2 CPU limit"
test "$(docker inspect -f '{{.HostConfig.Memory}}' mesh-cos-mcp)" = "25769803776" || fail "24 GiB memory limit"
docker exec mesh-cos-mcp test ! -S /var/run/docker.sock || fail "Docker socket present"
pass "least-privilege and resource controls"

PIDS=$(docker inspect -f '{{.HostConfig.PidsLimit}}' mesh-cos-mcp 2>/dev/null || echo unknown)
case "$PIDS" in 0|'<nil>'|-1) pass "no PID limit" ;; *) fail "unexpected PID limit: $PIDS" ;; esac

mesh_set_stage image_identity
RUNNING_MESH_ID=$(docker inspect -f '{{.Image}}' mesh-cos-mcp)
[ "$RUNNING_MESH_ID" = "$MESH_COS_IMAGE_ID" ] || fail "running Mesh image differs from prepared image ID"
RUNNING_TUNNEL_ID=$(docker inspect -f '{{.Image}}' mesh-cos-tunnel)
[ "$RUNNING_TUNNEL_ID" = "$TUNNEL_IMAGE_ID" ] || fail "running tunnel image differs from prepared image ID"
pass "running containers match pinned image identities"

mesh_set_stage ingress_denial
DIRECT_CODE=$(docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/mcp',{method:'POST',headers:{'content-type':'application/json'},body:'{}'}).then(r=>process.stdout.write(String(r.status))).catch(()=>process.exit(2))")
[ "$DIRECT_CODE" = "403" ] || fail "non-tunnel direct MCP request returned $DIRECT_CODE instead of 403"
pass "non-tunnel direct MCP request denied"

if command -v curl >/dev/null 2>&1; then
  LAN_CODE=$(curl -sS --connect-timeout 3 --max-time 5 -o /tmp/mesh-cos-mcp-lan-denied.json -w '%{http_code}' -X POST -H 'content-type: application/json' -d '{}' http://192.168.7.60:8080/mcp 2>/dev/null)
  CURL_RC=$?
  if [ "$CURL_RC" -eq 0 ]; then
    [ "$LAN_CODE" = "403" ] || fail "LAN MCP request returned $LAN_CODE instead of 403"
    pass "LAN MCP request denied with 403"
  else
    warn "QNAP host could not route to its qnet service IP; direct non-tunnel denial already passed and tunnel acceptance remains required"
  fi
else
  warn "curl is unavailable on the QNAP host; direct non-tunnel denial already passed"
fi

mesh_set_stage complete
pass "local container verification complete"
mesh_log INFO verify_complete "deployment_release=$MESH_COS_DEPLOYMENT_RELEASE mesh_image_id=$RUNNING_MESH_ID tunnel_image_id=$RUNNING_TUNNEL_ID"
echo "Deployment release: $MESH_COS_DEPLOYMENT_RELEASE"
echo "Canonical MCP contract: 4.0.0"
echo "Mesh image ID: $RUNNING_MESH_ID"
echo "Tunnel image ID: $RUNNING_TUNNEL_ID"
docker network inspect lan7 --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}' 2>/dev/null || true
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
echo "NEXT: complete CHATGPT-ACCEPTANCE.md through the Secure MCP Tunnel."
