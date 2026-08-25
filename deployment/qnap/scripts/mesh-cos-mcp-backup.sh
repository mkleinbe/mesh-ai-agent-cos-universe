#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
LABEL=${1:-manual}
SAFE_LABEL=$(printf '%s' "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
STAMP=$(date '+%Y%m%d-%H%M%S')
TMP_REL="runtime/taskledger-$STAMP.sqlite3"
TMP_HOST="$APP_ROOT/state/$TMP_REL"
DEST="$BACKUP_ROOT/$STAMP-$SAFE_LABEL"

fail() { echo "ERROR: $1" >&2; exit 1; }

cd "$SCRIPT_ROOT"
[ -d "$BACKUP_ROOT" ] || fail "backup root missing: $BACKUP_ROOT"
[ -w "$BACKUP_ROOT" ] || fail "backup root not writable: $BACKUP_ROOT"
docker inspect mesh-cos-mcp >/dev/null 2>&1 || fail "mesh-cos-mcp is not available for an online SQLite backup"
[ "$(docker inspect -f '{{.State.Running}}' mesh-cos-mcp 2>/dev/null || echo false)" = "true" ] || fail "mesh-cos-mcp must be running for online backup"

mkdir -p "$DEST"
docker exec mesh-cos-mcp python3 deployment/qnap/sqlite_backup.py \
  --source /var/lib/mesh/ledger/taskledger.sqlite3 \
  --destination "/var/lib/mesh/$TMP_REL"
[ -f "$TMP_HOST" ] || fail "completed SQLite backup not found at $TMP_HOST"
cp "$TMP_HOST" "$DEST/taskledger.sqlite3"
rm -f "$TMP_HOST"

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
} > "$DEST/deployment-state.txt"

(
  cd "$DEST"
  sha256sum taskledger.sqlite3 compose.yaml .env release-metadata.txt deployment-state.txt 2>/dev/null > SHA256SUMS
  sha256sum -c SHA256SUMS >/dev/null
)
chmod 0640 "$DEST/.env" 2>/dev/null || true

echo "backup=$DEST"
echo "secrets_included=false"
echo "PASS online state and non-secret deployment configuration backup"
