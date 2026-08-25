#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
LABEL=${1:-manual}
SAFE_LABEL=$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
STAMP=$(date '+%Y%m%d-%H%M%S')
TMP_REL="runtime/taskledger-$STAMP-$$.sqlite3"
DEST="$BACKUP_ROOT/$STAMP-$SAFE_LABEL-$$"
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-backup.sh
export QNAP_SCRIPT_ROOT QNAP_APP_ROOT QNAP_BACKUP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init backup || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-backup}" "$1"; }

mesh_set_stage backup_preflight
cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$BACKUP_ROOT" ] || fail "backup root missing: $BACKUP_ROOT"
[ -w "$BACKUP_ROOT" ] || fail "backup root not writable: $BACKUP_ROOT"
docker inspect mesh-cos-mcp >/dev/null 2>&1 || fail "mesh-cos-mcp is not available for an online SQLite backup"
[ "$(docker inspect -f '{{.State.Running}}' mesh-cos-mcp 2>/dev/null || echo false)" = "true" ] || fail "mesh-cos-mcp must be running for online backup"
mkdir "$DEST" || fail "unable to create unique backup destination: $DEST"

mesh_set_stage sqlite_online_backup
mesh_run sqlite_online_backup sqlite-backup \
  docker exec mesh-cos-mcp python3 deployment/qnap/sqlite_backup.py \
    --source /var/lib/mesh/ledger/taskledger.sqlite3 \
    --destination "/var/lib/mesh/$TMP_REL" || fail "online SQLite backup failed"

mesh_set_stage backup_export
mesh_run backup_export docker-cp-ledger \
  docker cp "mesh-cos-mcp:/var/lib/mesh/$TMP_REL" "$DEST/taskledger.sqlite3" || fail "Docker-mediated backup export failed"
mesh_run backup_export remove-container-temp \
  docker exec mesh-cos-mcp rm -f "/var/lib/mesh/$TMP_REL" || fail "unable to remove temporary in-container backup"
[ -s "$DEST/taskledger.sqlite3" ] || fail "exported SQLite backup missing or empty"

mesh_set_stage backup_configuration
[ -f "$APP_ROOT/compose.yaml" ] && cp "$APP_ROOT/compose.yaml" "$DEST/compose.yaml"
[ -f "$APP_ROOT/.env" ] && cp "$APP_ROOT/.env" "$DEST/.env"
[ -f "$APP_ROOT/release-metadata.txt" ] && cp "$APP_ROOT/release-metadata.txt" "$DEST/release-metadata.txt"
if [ -f "$DEST/.env" ]; then
  grep -q '^OPENAI_TUNNEL_RUNTIME_KEY=' "$DEST/.env" && fail "secret value found in .env backup"
  grep -q '^CONTROL_PLANE_API_KEY=' "$DEST/.env" && fail "control-plane key found in .env backup"
fi

{
  echo "created_at=$STAMP"
  echo "label=$SAFE_LABEL"
  echo "mesh_container_image_id=$(docker inspect -f '{{.Image}}' mesh-cos-mcp)"
  echo "tunnel_container_image_id=$(docker inspect -f '{{.Image}}' mesh-cos-tunnel 2>/dev/null || echo unavailable)"
  echo "secret_material_included=false"
  echo "state_export_method=docker_cp"
  echo "deployment_log=$MESH_COS_LOG_FILE"
} > "$DEST/deployment-state.txt"

mesh_set_stage backup_integrity
(
  cd "$DEST" || exit 1
  sha256sum taskledger.sqlite3 compose.yaml .env release-metadata.txt deployment-state.txt 2>/dev/null > SHA256SUMS
  sha256sum -c SHA256SUMS >/dev/null
) || fail "backup SHA-256 verification failed"
chmod 0640 "$DEST/.env" 2>/dev/null || true

mesh_log INFO backup_complete "destination=$DEST secrets_included=false state_export_method=docker_cp"
echo "backup=$DEST"
echo "secrets_included=false"
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
echo "PASS online state and non-secret deployment configuration backup"
