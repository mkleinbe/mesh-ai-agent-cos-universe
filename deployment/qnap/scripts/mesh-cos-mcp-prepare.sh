#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
STATE_ROOT=${QNAP_MESH_ROOT:-/share/Docker/cos-mcp/state}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
SECRET_FILE=${QNAP_TUNNEL_API_KEY_FILE:-/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key}
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
RELEASE_VERSION=${MESH_COS_DEPLOYMENT_RELEASE:-4.1.2}
MESH_IMAGE_TAG=${MESH_COS_LOCAL_TAG:-mesh-cos-mcp:qnap-v4.1.2}
TUNNEL_SOURCE=${OPENAI_TUNNEL_IMAGE_SOURCE:-ghcr.io/openai/tunnel-client:v0.0.12}
BUILD_CONTEXT="$APP_ROOT/build-context"
LEDGER="$STATE_ROOT/ledger/taskledger.sqlite3"
ENV_FILE="$APP_ROOT/.env"
COMPOSE_LIB="$SCRIPT_ROOT/mesh-cos-qnap-compose.sh"

fail() { echo "ERROR: $1" >&2; exit 1; }
info() { echo "INFO $1"; }

read_visible_tty() {
  prompt=$1
  [ -r /dev/tty ] || fail "interactive input requires a TTY"
  printf '%s' "$prompt" > /dev/tty
  IFS= read -r REPLY < /dev/tty || fail "unable to read from TTY"
}

read_secret_tty() {
  [ -r /dev/tty ] || fail "tunnel runtime key input requires a TTY"
  command -v stty >/dev/null 2>&1 || fail "stty is required for hidden secret input"
  printf '%s' "OpenAI tunnel runtime API key (input hidden): " > /dev/tty
  trap 'stty echo < /dev/tty >/dev/null 2>&1 || true' 0 1 2 15
  stty -echo < /dev/tty
  IFS= read -r SECRET_VALUE < /dev/tty || { stty echo < /dev/tty; fail "unable to read tunnel runtime key"; }
  stty echo < /dev/tty
  printf '\n' > /dev/tty
  trap - 0 1 2 15
}

existing_env_value() {
  key=$1
  [ -f "$ENV_FILE" ] || return 0
  sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n 1 | sed 's/^"//;s/"$//'
}

cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$APP_ROOT" ] || fail "$APP_ROOT is missing. Extract the release bundle into /share/Docker first."
[ -f "$APP_ROOT/compose.yaml" ] || fail "$APP_ROOT/compose.yaml is missing"
[ -d "$BUILD_CONTEXT" ] || fail "$BUILD_CONTEXT is missing from the release bundle"
[ -f "$BUILD_CONTEXT/Dockerfile" ] || fail "$BUILD_CONTEXT/Dockerfile is missing"
command -v docker >/dev/null 2>&1 || fail "docker is not available"
[ -r "$COMPOSE_LIB" ] || fail "Compose discovery helper is missing: $COMPOSE_LIB"
. "$COMPOSE_LIB"
mesh_resolve_compose || fail "Docker Compose V2 is installed by Container Station but could not be resolved from docker compose, Docker plugin metadata, /usr/local/lib/docker/cli-plugins, or the Container Station QPKG path"
info "using Compose V2 via $(mesh_compose_description)"

mkdir -p "$STATE_ROOT/ledger" "$STATE_ROOT/governance" "$STATE_ROOT/audit" "$STATE_ROOT/runtime" "$APP_ROOT/secrets"
[ -d "$BACKUP_ROOT" ] || mkdir -p "$BACKUP_ROOT"
chown -R "$MESH_UID:$MESH_GID" "$STATE_ROOT" "$APP_ROOT/secrets"
chmod 0750 "$APP_ROOT"
chmod 0770 "$STATE_ROOT" "$STATE_ROOT/ledger" "$STATE_ROOT/governance" "$STATE_ROOT/audit" "$STATE_ROOT/runtime"
chmod 0700 "$APP_ROOT/secrets"
[ -w "$BACKUP_ROOT" ] || fail "backup root is not writable: $BACKUP_ROOT"

if [ "${MESH_COS_FORCE_REBUILD:-0}" = "1" ] || ! docker image inspect "$MESH_IMAGE_TAG" >/dev/null 2>&1; then
  VCS_REF=$(sed -n 's/^commit=//p' "$APP_ROOT/release-metadata.txt" 2>/dev/null | head -n 1 || true)
  [ -n "$VCS_REF" ] || VCS_REF=release-bundle
  BUILD_DATE=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date)
  info "building release-bound Mesh image $MESH_IMAGE_TAG"
  docker build \
    --build-arg VCS_REF="$VCS_REF" \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg IMAGE_VERSION="${RELEASE_VERSION}-qnap" \
    -t "$MESH_IMAGE_TAG" "$BUILD_CONTEXT"
else
  info "reusing local release image $MESH_IMAGE_TAG"
fi
MESH_IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$MESH_IMAGE_TAG" 2>/dev/null || true)
case "$MESH_IMAGE_ID" in sha256:*) ;; *) fail "unable to resolve Mesh image ID" ;; esac

EXISTING_TUNNEL_IMAGE=$(existing_env_value TUNNEL_IMAGE || true)
if [ -n "$EXISTING_TUNNEL_IMAGE" ] && printf '%s' "$EXISTING_TUNNEL_IMAGE" | grep -Eq '@sha256:[0-9a-fA-F]{64}$' && docker image inspect "$EXISTING_TUNNEL_IMAGE" >/dev/null 2>&1; then
  TUNNEL_IMAGE=$EXISTING_TUNNEL_IMAGE
  info "reusing previously pinned tunnel image $TUNNEL_IMAGE"
else
  info "pulling versioned OpenAI tunnel client $TUNNEL_SOURCE"
  docker pull "$TUNNEL_SOURCE"
  TUNNEL_IMAGE=$(docker image inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' "$TUNNEL_SOURCE" 2>/dev/null | sed -n '1p')
fi
printf '%s' "$TUNNEL_IMAGE" | grep -Eq '^ghcr\.io/openai/tunnel-client@sha256:[0-9a-fA-F]{64}$' || fail "unable to resolve immutable OpenAI tunnel RepoDigest"
TUNNEL_IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$TUNNEL_IMAGE" 2>/dev/null || true)
case "$TUNNEL_IMAGE_ID" in sha256:*) ;; *) fail "unable to resolve tunnel image ID" ;; esac

if [ -f "$LEDGER" ]; then
  info "preserving existing canonical ledger $LEDGER"
else
  LEDGER_SOURCE=${MESH_COS_LEDGER_SOURCE:-}
  if [ -z "$LEDGER_SOURCE" ]; then
    read_visible_tty "Path to the approved existing canonical TaskLedger SQLite file: "
    LEDGER_SOURCE=$REPLY
  fi
  [ -f "$LEDGER_SOURCE" ] || fail "approved ledger source does not exist: $LEDGER_SOURCE"
  TMP_LEDGER="$LEDGER.incoming.$$"
  rm -f "$TMP_LEDGER"
  cp "$LEDGER_SOURCE" "$TMP_LEDGER"
  chown "$MESH_UID:$MESH_GID" "$TMP_LEDGER"
  chmod 0660 "$TMP_LEDGER"
  mv "$TMP_LEDGER" "$LEDGER"
  info "staged approved canonical ledger at $LEDGER"
fi
chown "$MESH_UID:$MESH_GID" "$LEDGER"
chmod 0660 "$LEDGER"

docker run --rm \
  --user "$MESH_UID:$MESH_GID" \
  -e MESH_COS_AGENT_ID=cos \
  -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \
  -e MESH_COS_REQUIRE_EXISTING_LEDGER=true \
  -e MCP_AUTH_MODE=tunnel \
  -e MESH_MIN_FREE_BYTES=1048576 \
  -v "$STATE_ROOT:/var/lib/mesh:rw" \
  --entrypoint python3 "$MESH_IMAGE_TAG" deployment/qnap/runtime_preflight.py >/tmp/mesh-cos-mcp-ledger-preflight.json
info "canonical ledger integrity/runtime preflight passed"

TUNNEL_ID=${CONTROL_PLANE_TUNNEL_ID:-}
[ -n "$TUNNEL_ID" ] || TUNNEL_ID=$(existing_env_value CONTROL_PLANE_TUNNEL_ID || true)
if [ -z "$TUNNEL_ID" ]; then
  read_visible_tty "OpenAI Secure MCP tunnel_id (tunnel_ plus 32 hex characters): "
  TUNNEL_ID=$REPLY
fi
printf '%s' "$TUNNEL_ID" | grep -Eq '^tunnel_[0-9a-fA-F]{32}$' || fail "invalid tunnel_id format"

if [ -s "$SECRET_FILE" ]; then
  info "preserving existing tunnel runtime key file"
else
  read_secret_tty
  [ -n "$SECRET_VALUE" ] || fail "tunnel runtime key cannot be empty"
  TMP_SECRET="$SECRET_FILE.incoming.$$"
  umask 077
  printf '%s' "$SECRET_VALUE" > "$TMP_SECRET"
  unset SECRET_VALUE
  chown "$MESH_UID:$MESH_GID" "$TMP_SECRET"
  chmod 0400 "$TMP_SECRET"
  mv "$TMP_SECRET" "$SECRET_FILE"
  info "created tunnel runtime key file without placing the key in .env or shell history"
fi
chown "$MESH_UID:$MESH_GID" "$SECRET_FILE"
chmod 0400 "$SECRET_FILE"

ENV_TMP="$ENV_FILE.incoming.$$"
cat > "$ENV_TMP" <<EOF
# Generated by mesh-cos-mcp-prepare.sh for QNAP release v${RELEASE_VERSION}. No secret values are stored here.
MESH_COS_DEPLOYMENT_RELEASE=${RELEASE_VERSION}
MESH_COS_IMAGE=${MESH_IMAGE_TAG}
MESH_COS_IMAGE_ID=${MESH_IMAGE_ID}
TUNNEL_IMAGE=${TUNNEL_IMAGE}
TUNNEL_IMAGE_ID=${TUNNEL_IMAGE_ID}
OPENAI_TUNNEL_IMAGE_SOURCE=${TUNNEL_SOURCE}
QNAP_SCRIPT_ROOT=/share/Docker
QNAP_APP_ROOT=/share/Docker/cos-mcp
QNAP_MESH_ROOT=/share/Docker/cos-mcp/state
QNAP_BACKUP_ROOT="/share/QNAP NAS/Mike Home/MCP/CoS/Backups"
QNAP_TUNNEL_API_KEY_FILE=/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key
MESH_UID=65532
MESH_GID=65532
MESH_CPU_LIMIT=2.0
MESH_MEMORY_LIMIT=24g
MESH_MIN_FREE_BYTES=21474836480
MESH_LOG_MAX_SIZE=10m
MESH_LOG_MAX_FILES=5
MESH_COS_BRIDGE_TIMEOUT_MS=30000
MESH_COS_MAX_BRIDGE_QUEUE=32
CONTROL_PLANE_TUNNEL_ID=${TUNNEL_ID}
EOF
chmod 0640 "$ENV_TMP"
mv "$ENV_TMP" "$ENV_FILE"

info "generated deterministic .env with pinned image identities"
sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"
info "prepare complete"
