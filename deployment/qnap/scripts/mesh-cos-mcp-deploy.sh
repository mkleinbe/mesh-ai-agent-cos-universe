#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}

cd "$SCRIPT_ROOT"
[ -f "$APP_ROOT/.env" ] || { echo "ERROR: $APP_ROOT/.env missing" >&2; exit 1; }

set -a
. "$APP_ROOT/.env"
set +a

sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"
cd "$APP_ROOT"
docker compose --env-file .env -f compose.yaml config >/tmp/mesh-cos-mcp-compose.rendered.yaml
docker compose --env-file .env -f compose.yaml up -d

echo "Deployment command completed. Run: cd /share/Docker && sh mesh-cos-mcp-verify.sh"
