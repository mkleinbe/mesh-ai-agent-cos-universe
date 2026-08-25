#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
STAMP=$(date '+%Y%m%d-%H%M%S')
TMP_REL="runtime/taskledger-$STAMP.sqlite3"
TMP_HOST="$APP_ROOT/state/$TMP_REL"
FINAL="$BACKUP_ROOT/taskledger-$STAMP.sqlite3"

cd "$SCRIPT_ROOT"
[ -d "$BACKUP_ROOT" ] || { echo "ERROR: backup root missing: $BACKUP_ROOT" >&2; exit 1; }
[ -w "$BACKUP_ROOT" ] || { echo "ERROR: backup root not writable: $BACKUP_ROOT" >&2; exit 1; }

docker exec mesh-cos-mcp python3 deployment/qnap/sqlite_backup.py \
  --source /var/lib/mesh/ledger/taskledger.sqlite3 \
  --destination "/var/lib/mesh/$TMP_REL"

[ -f "$TMP_HOST" ] || { echo "ERROR: completed SQLite backup not found at $TMP_HOST" >&2; exit 1; }
cp "$TMP_HOST" "$FINAL"
SRC_HASH=$(sha256sum "$TMP_HOST" | awk '{print $1}')
DST_HASH=$(sha256sum "$FINAL" | awk '{print $1}')
[ "$SRC_HASH" = "$DST_HASH" ] || { echo "ERROR: backup hash mismatch" >&2; exit 1; }
rm -f "$TMP_HOST"

echo "backup=$FINAL"
echo "sha256=$DST_HASH"
