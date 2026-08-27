#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
STATE_ROOT=${QNAP_MESH_ROOT:-$APP_ROOT/state}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
LABEL=${1:-manual}
SAFE_LABEL=$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
STAMP=$(date '+%Y%m%d-%H%M%S')
TMP_REL="runtime/taskledger-$STAMP-$$.sqlite3"
TMP_HOST="$STATE_ROOT/$TMP_REL"
DEST="$BACKUP_ROOT/$STAMP-$SAFE_LABEL-$$"
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-mcp-backup.sh
BACKUP_COMPLETE=0
RESTORE_RUNNING_INTENT=0
STATE_EXPORT_METHOD=unknown
export QNAP_SCRIPT_ROOT QNAP_APP_ROOT QNAP_MESH_ROOT QNAP_BACKUP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init backup || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
mesh_init_docker_config || mesh_fail 1 bootstrap "unable to initialize deployment-local Docker config"

cleanup_partial_backup() {
  rm -f "$TMP_HOST" 2>/dev/null || true
  if [ "$BACKUP_COMPLETE" -ne 1 ] && [ -d "$DEST" ]; then
    rm -rf "$DEST" 2>/dev/null || true
  fi
}

fail() {
  cleanup_partial_backup
  mesh_fail 1 "${MESH_COS_STAGE:-backup}" "$1"
}

restore_running_intent() {
  [ "$RESTORE_RUNNING_INTENT" -eq 1 ] || return 0
  mesh_set_stage sqlite_runtime_restore
  if mesh_run sqlite_runtime_restore docker-start docker start mesh-cos-mcp; then
    RESTORE_RUNNING_INTENT=0
    mesh_log INFO sqlite_runtime_restore "result=PASS prior_running_intent=true"
    return 0
  fi
  mesh_log ERROR sqlite_runtime_restore "result=FAIL prior_running_intent=true"
  return 1
}

mesh_set_stage backup_preflight
cd "$SCRIPT_ROOT" || fail "cannot enter $SCRIPT_ROOT"
[ -d "$BACKUP_ROOT" ] || fail "backup root missing: $BACKUP_ROOT"
[ -w "$BACKUP_ROOT" ] || fail "backup root not writable: $BACKUP_ROOT"
docker inspect mesh-cos-mcp >/dev/null 2>&1 || fail "mesh-cos-mcp is not available for state backup"
[ -s "$STATE_ROOT/ledger/taskledger.sqlite3" ] || fail "canonical TaskLedger is missing or empty: $STATE_ROOT/ledger/taskledger.sqlite3"

CONTAINER_STATUS=$(docker inspect -f '{{.State.Status}}' mesh-cos-mcp 2>/dev/null || echo unknown)
CONTAINER_RUNNING=$(docker inspect -f '{{.State.Running}}' mesh-cos-mcp 2>/dev/null || echo false)
CONTAINER_RESTARTING=$(docker inspect -f '{{.State.Restarting}}' mesh-cos-mcp 2>/dev/null || echo false)
ACTIVE_IMAGE_ID=$(docker inspect -f '{{.Image}}' mesh-cos-mcp 2>/dev/null || echo '')
[ -n "$ACTIVE_IMAGE_ID" ] || fail "unable to resolve active Mesh image for state backup"
mkdir "$DEST" || fail "unable to create unique backup destination: $DEST"
mesh_log INFO backup_mode_select "container_status=$CONTAINER_STATUS running=$CONTAINER_RUNNING restarting=$CONTAINER_RESTARTING"

if [ "$CONTAINER_STATUS" = "running" ] && [ "$CONTAINER_RESTARTING" = "false" ]; then
  STATE_EXPORT_METHOD=docker_exec_online
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
else
  STATE_EXPORT_METHOD=quiesced_helper
  mesh_set_stage sqlite_quiesce
  case "$CONTAINER_STATUS:$CONTAINER_RUNNING" in
    restarting:*|running:true)
      mesh_run sqlite_quiesce docker-stop docker stop -t 20 mesh-cos-mcp || fail "unable to quiesce unstable mesh-cos-mcp before SQLite backup"
      RESTORE_RUNNING_INTENT=1
      ;;
  esac

  mesh_set_stage sqlite_quiesced_backup
  helper_rc=0
  mesh_run sqlite_quiesced_backup sqlite-backup-helper \
    docker run --rm --network none \
      --user "${MESH_UID:-65532}:${MESH_GID:-65532}" \
      --read-only \
      --cap-drop ALL \
      --security-opt no-new-privileges \
      --tmpfs /tmp:rw,noexec,nosuid,nodev,size=16m \
      -v "$STATE_ROOT:/var/lib/mesh:rw" \
      "$ACTIVE_IMAGE_ID" \
      python3 deployment/qnap/sqlite_backup.py \
        --source /var/lib/mesh/ledger/taskledger.sqlite3 \
        --destination "/var/lib/mesh/$TMP_REL" || helper_rc=$?

  export_rc=0
  if [ "$helper_rc" -eq 0 ]; then
    mesh_set_stage backup_export
    mesh_run backup_export host-copy-ledger cp "$TMP_HOST" "$DEST/taskledger.sqlite3" || export_rc=$?
  fi
  rm -f "$TMP_HOST" 2>/dev/null || true

  restore_rc=0
  restore_running_intent || restore_rc=$?
  if [ "$helper_rc" -ne 0 ]; then
    fail "quiesced SQLite backup helper failed"
  fi
  if [ "$export_rc" -ne 0 ]; then
    fail "quiesced SQLite backup export failed"
  fi
  if [ "$restore_rc" -ne 0 ]; then
    fail "SQLite backup succeeded but prior mesh-cos-mcp running intent could not be restored"
  fi
fi

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
  echo "mesh_container_image_id=$ACTIVE_IMAGE_ID"
  echo "tunnel_container_image_id=$(docker inspect -f '{{.Image}}' mesh-cos-tunnel 2>/dev/null || echo unavailable)"
  echo "secret_material_included=false"
  echo "state_export_method=$STATE_EXPORT_METHOD"
  echo "source_container_status=$CONTAINER_STATUS"
  echo "source_container_restarting=$CONTAINER_RESTARTING"
  echo "deployment_log=$MESH_COS_LOG_FILE"
} > "$DEST/deployment-state.txt"

mesh_set_stage backup_integrity
(
  cd "$DEST" || exit 1
  sha256sum taskledger.sqlite3 compose.yaml .env release-metadata.txt deployment-state.txt 2>/dev/null > SHA256SUMS
  sha256sum -c SHA256SUMS >/dev/null
) || fail "backup SHA-256 verification failed"
chmod 0640 "$DEST/.env" 2>/dev/null || true

BACKUP_COMPLETE=1
cleanup_partial_backup
mesh_log INFO backup_complete "destination=$DEST secrets_included=false state_export_method=$STATE_EXPORT_METHOD"
echo "backup=$DEST"
echo "secrets_included=false"
echo "DIAGNOSTIC_LOG=$MESH_COS_LOG_FILE"
echo "PASS state and non-secret deployment configuration backup"
