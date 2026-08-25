#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/../../.." && pwd)
LIB="$ROOT/deployment/qnap/scripts/mesh-cos-qnap-compose.sh"
TMP=${TMPDIR:-/tmp}/mesh-compose-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
mkdir -p "$TMP/bin" "$TMP/plugin"

cat > "$TMP/bin/docker" <<'MOCK'
#!/bin/sh
case "${1:-}" in
  compose)
    if [ "${MOCK_DOCKER_COMPOSE_OK:-0}" = "1" ] && [ "${2:-}" = version ]; then
      echo 'Docker Compose version v2.29.1-qnap2'
      exit 0
    fi
    exit 1
    ;;
  info)
    printf '%s\n' "${MOCK_COMPOSE_PLUGIN:-}"
    exit 0
    ;;
  *) exit 0 ;;
esac
MOCK

cat > "$TMP/plugin/docker-compose" <<'MOCK'
#!/bin/sh
if [ "${1:-}" = version ]; then
  echo "Docker Compose version ${MOCK_PLUGIN_VERSION:-v2.29.1-qnap2}"
  exit 0
fi
printf 'PLUGIN %s\n' "$*"
MOCK
chmod +x "$TMP/bin/docker" "$TMP/plugin/docker-compose"

PATH="$TMP/bin:/bin:/usr/bin" MOCK_DOCKER_COMPOSE_OK=1 sh -c '
  . "$1"
  mesh_resolve_compose
  [ "$MESH_COMPOSE_MODE" = docker-subcommand ]
  mesh_compose version | grep -q "v2.29.1-qnap2"
' sh "$LIB"

PATH="$TMP/bin:/bin:/usr/bin" MOCK_DOCKER_COMPOSE_OK=0 MOCK_COMPOSE_PLUGIN="$TMP/plugin/docker-compose" sh -c '
  . "$1"
  mesh_resolve_compose
  [ "$MESH_COMPOSE_MODE" = direct-plugin ]
  [ "$MESH_COMPOSE_BIN" = "$2" ]
  mesh_compose version | grep -q "v2.29.1-qnap2"
' sh "$LIB" "$TMP/plugin/docker-compose"

if MOCK_PLUGIN_VERSION=v1.29.2 sh -c '
  . "$1"
  mesh_compose_v2 "$2"
' sh "$LIB" "$TMP/plugin/docker-compose"; then
  echo 'FAIL Compose V1 validator accepted a V1 plugin' >&2
  exit 1
fi

echo 'PASS QNAP Compose V2 subcommand, direct-plugin fallback, and V1 rejection'
