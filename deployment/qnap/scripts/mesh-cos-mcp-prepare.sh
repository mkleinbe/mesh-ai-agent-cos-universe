#!/bin/sh
set -eu

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-/share/Docker}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
BACKUP_ROOT=${QNAP_BACKUP_ROOT:-/share/QNAP NAS/Mike Home/MCP/CoS/Backups}
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}

cd "$SCRIPT_ROOT"
[ -d "$APP_ROOT" ] || { echo "ERROR: $APP_ROOT is missing. Copy the release bundle first." >&2; exit 1; }

mkdir -p "$APP_ROOT/state/ledger" "$APP_ROOT/state/governance" "$APP_ROOT/state/audit" "$APP_ROOT/state/runtime" "$APP_ROOT/secrets" "$BACKUP_ROOT"
chown -R "$MESH_UID:$MESH_GID" "$APP_ROOT/state" "$APP_ROOT/secrets"
chmod 0750 "$APP_ROOT"
chmod 0770 "$APP_ROOT/state" "$APP_ROOT/state/ledger" "$APP_ROOT/state/governance" "$APP_ROOT/state/audit" "$APP_ROOT/state/runtime"
chmod 0700 "$APP_ROOT/secrets"
chmod 0750 "$BACKUP_ROOT"

echo "Prepared $APP_ROOT"
echo "Backup root: $BACKUP_ROOT"
echo "Next: stage the approved taskledger.sqlite3, create .env, and create the tunnel runtime key."
