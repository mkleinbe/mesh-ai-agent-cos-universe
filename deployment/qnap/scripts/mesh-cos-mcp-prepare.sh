#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
STATE_ROOT=${QNAP_MESH_ROOT:-/share/Docker/cos-mcp/state}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
SECRET_FILE=${QNAP_TUNNEL_API_KEY_FILE:-/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key}
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
RELEASE_VERSION=${MESH_COS_DEPLOYMENT_RELEASE:-4.1.6}
MESH_IMAGE_TAG=${MESH_COS_LOCAL_TAG:-mesh-cos-mcp:qnap-v4.1.6}
TUNNEL_SOURCE=${OPENAI_TUNNEL_IMAGE_SOURCE:-ghcr.io/openai/tunnel-client:v0.0.12}
BUILD_CONTEXT="$APP_ROOT/build-context"
LEDGER="$STATE_ROOT/ledger/taskledger.sqlite3"
ENV_FILE="$APP_ROOT/.env"
COMPOSE_LIB="$SCRIPT_ROOT/mesh-cos-qnap-compose.sh"
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
PERM_LIB="$SCRIPT_ROOT/mesh-cos-qnap-permissions.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-prepare.sh
export QNAP_SCRIPT_ROOT APP_ROOT STATE_ROOT BACKUP_ROOT SECRET_FILE MESH_UID MESH_GID MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init prepare || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"

[ -r "$PERM_LIB" ] || mesh_fail 1 bootstrap "runtime permission helper missing: $PERM_LIB"
. "$PERM_LIB"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-prepare}" "$1"; }
info() { mesh_log INFO info "$1"; }

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
  stty -echo < /dev/tty || fail "unable to disable terminal echo"
  IFS= read -r SECRET_VALUE < /dev/tty || { stty echo < /dev/tty >/dev/null 2>&1 || true; fail "unable to read tunnel runtime key"; }
  stty echo < /dev/tty >/dev/null 2>&1 || true
  printf '\n' > /dev/tty
  trap - 0 1 2 15
  mesh_log INFO secret_input "status=captured value_logged=false"
}

existing_env_value() {
  key=$1
  [ -f "$ENV_FILE" ] || return 0
  sed -n "s/^${key}=//p" "$ENV_FILE" | tail -n 1 | sed 's/^"//;s/"$//'
}

mesh_set_stage bootstrap
cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$APP_ROOT" ] || fail "$APP_ROOT is missing. Extract the release bundle into /share/Docker first."
[ -f "$APP_ROOT/compose.yaml" ] || fail "$APP_ROOT/compose.yaml is missing"
[ -d "$BUILD_CONTEXT" ] || fail "$BUILD_CONTEXT is missing from the release bundle"
[ -f "$BUILD_CONTEXT/Dockerfile" ] || fail "$BUILD_CONTEXT/Dockerfile is missing"
command -v docker >/dev/null 2>&1 || fail "docker is not available"
[ -r "$COMPOSE_LIB" ] || fail "Compose discovery helper is missing: $COMPOSE_LIB"
. "$COMPOSE_LIB"
mesh_resolve_compose || fail "Docker Compose V2 could not be resolved from the QNAP Container Station installation"
mesh_log INFO compose_resolved "via=$(mesh_compose_description)"

mesh_set_stage filesystem_init
mesh_run filesystem_init create-runtime-roots mkdir -p "$STATE_ROOT" "$APP_ROOT/secrets" "$BACKUP_ROOT" || fail "unable to create required runtime roots"
chmod 0750 "$APP_ROOT" 2>/dev/null || fail "unable to set application-root mode"
chmod 0700 "$APP_ROOT/secrets" 2>/dev/null || fail "unable to set secrets-directory mode"
[ -w "$BACKUP_ROOT" ] || fail "backup root is not writable: $BACKUP_ROOT"
mesh_log INFO filesystem_evidence "state_root=$STATE_ROOT secrets_root=$APP_ROOT/secrets backup_root=$BACKUP_ROOT"

mesh_set_stage mesh_image
if [ "${MESH_COS_FORCE_REBUILD:-0}" = "1" ] || ! docker image inspect "$MESH_IMAGE_TAG" >/dev/null 2>&1; then
  VCS_REF=$(sed -n 's/^commit=//p' "$APP_ROOT/release-metadata.txt" 2>/dev/null | head -n 1 || true)
  [ -n "$VCS_REF" ] || VCS_REF=release-bundle
  BUILD_DATE=$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date)
  mesh_run mesh_image build-release-image \
    docker build \
      --build-arg VCS_REF="$VCS_REF" \
      --build-arg BUILD_DATE="$BUILD_DATE" \
      --build-arg IMAGE_VERSION="${RELEASE_VERSION}-qnap" \
      -t "$MESH_IMAGE_TAG" "$BUILD_CONTEXT" || fail "release-bound Mesh image build failed"
else
  info "reusing local release image $MESH_IMAGE_TAG"
fi
MESH_IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$MESH_IMAGE_TAG" 2>/dev/null || true)
case "$MESH_IMAGE_ID" in sha256:*) ;; *) fail "unable to resolve Mesh image ID" ;; esac
mesh_log INFO image_identity "mesh_image=$MESH_IMAGE_TAG mesh_image_id=$MESH_IMAGE_ID"

mesh_set_stage runtime_permissions
mesh_apply_state_permissions "$MESH_IMAGE_TAG" "$MESH_UID" "$MESH_GID" "$STATE_ROOT" || fail "constrained Docker helper could not normalize QNAP state ownership/modes"
mesh_log INFO runtime_permissions "state_owner=$MESH_UID:$MESH_GID directory_mode=0711 file_mode=0660 host_chown_used=false"

mesh_set_stage canonical_ledger
if [ -f "$LEDGER" ]; then
  info "preserving existing canonical ledger $LEDGER"
else
  LEDGER_SOURCE=${MESH_COS_LEDGER_SOURCE:-}
  if [ -z "$LEDGER_SOURCE" ]; then
    read_visible_tty "Path to the approved existing canonical TaskLedger SQLite file: "
    LEDGER_SOURCE=$REPLY
  fi
  [ -r "$LEDGER_SOURCE" ] || fail "approved ledger source is not readable: $LEDGER_SOURCE"
  [ -s "$LEDGER_SOURCE" ] || fail "approved ledger source is empty: $LEDGER_SOURCE"
  mesh_stage_ledger "$MESH_IMAGE_TAG" "$MESH_UID" "$MESH_GID" "$STATE_ROOT" "$LEDGER_SOURCE" || fail "unable to stage the approved canonical ledger through the runtime identity"
  info "staged approved canonical ledger at $LEDGER"
fi

mesh_run canonical_ledger runtime-ledger-preflight \
  docker run --rm \
    --network none \
    --read-only \
    --user "$MESH_UID:$MESH_GID" \
    --cap-drop ALL \
    --security-opt no-new-privileges \
    --tmpfs /tmp:rw,noexec,nosuid,nodev,size=32m \
    -e MESH_COS_AGENT_ID=cos \
    -e MESH_COS_LEDGER_PATH=/var/lib/mesh/ledger/taskledger.sqlite3 \
    -e MESH_COS_REQUIRE_EXISTING_LEDGER=true \
    -e MCP_AUTH_MODE=tunnel \
    -e MESH_MIN_FREE_BYTES=1048576 \
    -v "$STATE_ROOT:/var/lib/mesh:rw" \
    --entrypoint python3 "$MESH_IMAGE_TAG" deployment/qnap/runtime_preflight.py || fail "canonical ledger integrity/runtime preflight failed"
info "canonical ledger integrity/runtime preflight passed"

mesh_set_stage tunnel_image
EXISTING_TUNNEL_IMAGE=$(existing_env_value TUNNEL_IMAGE || true)
if [ -n "$EXISTING_TUNNEL_IMAGE" ] && printf '%s' "$EXISTING_TUNNEL_IMAGE" | grep -Eq '@sha256:[0-9a-fA-F]{64}$' && docker image inspect "$EXISTING_TUNNEL_IMAGE" >/dev/null 2>&1; then
  TUNNEL_IMAGE=$EXISTING_TUNNEL_IMAGE
  info "reusing previously pinned tunnel image $TUNNEL_IMAGE"
else
  mesh_run tunnel_image pull-versioned-tunnel-image docker pull "$TUNNEL_SOURCE" || fail "unable to pull versioned OpenAI tunnel client"
  TUNNEL_IMAGE=$(docker image inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' "$TUNNEL_SOURCE" 2>/dev/null | sed -n '1p')
fi
printf '%s' "$TUNNEL_IMAGE" | grep -Eq '^ghcr\.io/openai/tunnel-client@sha256:[0-9a-fA-F]{64}$' || fail "unable to resolve immutable OpenAI tunnel RepoDigest"
TUNNEL_IMAGE_ID=$(docker image inspect --format '{{.Id}}' "$TUNNEL_IMAGE" 2>/dev/null || true)
case "$TUNNEL_IMAGE_ID" in sha256:*) ;; *) fail "unable to resolve tunnel image ID" ;; esac
mesh_log INFO image_identity "tunnel_image_repo_digest=$TUNNEL_IMAGE tunnel_image_id=$TUNNEL_IMAGE_ID"

mesh_set_stage tunnel_configuration
TUNNEL_ID=${CONTROL_PLANE_TUNNEL_ID:-}
[ -n "$TUNNEL_ID" ] || TUNNEL_ID=$(existing_env_value CONTROL_PLANE_TUNNEL_ID || true)
if [ -z "$TUNNEL_ID" ]; then
  read_visible_tty "OpenAI Secure MCP tunnel_id (tunnel_ plus 32 hex characters): "
  TUNNEL_ID=$REPLY
fi
printf '%s' "$TUNNEL_ID" | grep -Eq '^tunnel_[0-9a-fA-F]{32}$' || fail "invalid tunnel_id format"
mesh_log INFO tunnel_id "format=valid value_logged=false"

if [ -s "$SECRET_FILE" ]; then
  info "preserving existing tunnel runtime key file"
else
  read_secret_tty
  [ -n "$SECRET_VALUE" ] || fail "tunnel runtime key cannot be empty"
  TMP_SECRET="$APP_ROOT/secrets/.openai-tunnel-runtime-key.incoming.$$"
  umask 077
  printf '%s' "$SECRET_VALUE" > "$TMP_SECRET" || { unset SECRET_VALUE; fail "unable to write temporary tunnel runtime key file"; }
  unset SECRET_VALUE
  mv "$TMP_SECRET" "$SECRET_FILE" || fail "unable to stage tunnel runtime key file"
  mesh_log INFO secret_file "status=staged value_logged=false"
fi
mesh_apply_secret_permissions "$MESH_IMAGE_TAG" "$MESH_UID" "$MESH_GID" "$APP_ROOT/secrets" || fail "constrained Docker helper could not set tunnel secret ownership/mode"
mesh_log INFO secret_file "owner=$MESH_UID:$MESH_GID mode=0400 value_logged=false"

mesh_set_stage environment
ENV_TMP="$ENV_FILE.incoming.$$"
cat > "$ENV_TMP" <<EOF_ENV
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
MESH_COS_DOCKER_CONFIG=/share/Docker/cos-mcp/.docker-cli
MESH_COS_LOG_ROOT=/share/Docker/cos-mcp/logs/deployment
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
EOF_ENV
chmod 0640 "$ENV_TMP" || fail "unable to set generated .env mode"
mv "$ENV_TMP" "$ENV_FILE" || fail "unable to install generated .env"
info "generated deterministic .env with pinned image identities and no secret values"

mesh_set_stage host_preflight
mesh_log INFO child_start "script=mesh-cos-mcp-preflight.sh"
sh "$SCRIPT_ROOT/mesh-cos-mcp-preflight.sh"
rc=$?
mesh_log INFO child_end "script=mesh-cos-mcp-preflight.sh rc=$rc"
[ "$rc" -eq 0 ] || fail "QNAP host preflight failed"

mesh_set_stage complete
info "prepare complete"
mesh_log INFO prepare_complete "release=$RELEASE_VERSION log=$MESH_COS_LOG_FILE"
