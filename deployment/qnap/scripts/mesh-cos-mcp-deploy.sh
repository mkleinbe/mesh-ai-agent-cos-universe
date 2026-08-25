#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}

fail() { echo "ERROR: $1" >&2; exit 1; }
info() { echo "INFO $1"; }

wait_healthy() {
  name=$1
  count=0
  while [ "$count" -lt 60 ]; do
    status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || echo missing)
    [ "$status" = "healthy" ] && { info "$name is healthy"; return 0; }
    count=$((count + 1))
    sleep 2
  done
  docker logs --tail 80 "$name" 2>&1 || true
  fail "$name did not become healthy"
}

cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$APP_ROOT" ] || fail "$APP_ROOT is missing. Extract the release bundle first."

if docker inspect mesh-cos-mcp >/dev/null 2>&1 && [ "$(docker inspect -f '{{.State.Running}}' mesh-cos-mcp 2>/dev/null || echo false)" = "true" ]; then
  info "creating pre-deploy online state/configuration backup"
  sh "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" pre-deploy
fi

sh "$SCRIPT_ROOT/mesh-cos-mcp-prepare.sh"
sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"

cd "$APP_ROOT"
docker compose --env-file .env -f compose.yaml config >/tmp/mesh-cos-mcp-compose.rendered.yaml
docker compose --env-file .env -f compose.yaml up -d --no-build

wait_healthy mesh-cos-mcp
wait_healthy mesh-cos-tunnel

cd "$SCRIPT_ROOT"
sh "$SCRIPT_ROOT/mesh-cos-mcp-verify.sh"
sh "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" post-deploy

info "deployment, verification, and post-deploy backup complete"
echo "NEXT: create/select the OpenAI Secure MCP Tunnel app in ChatGPT, Scan Tools, and run CHATGPT-ACCEPTANCE.md."
