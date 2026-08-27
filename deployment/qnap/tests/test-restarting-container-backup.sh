#!/bin/sh
set -eu

ROOT=${TMPDIR:-/tmp}/mesh-restarting-backup-$$
BIN="$ROOT/bin"
APP="$ROOT/app"
STATE="$APP/state"
BACKUPS="$ROOT/backups"
LOGS="$ROOT/logs"
COMMAND_LOG="$ROOT/docker-commands.log"
mkdir -p "$BIN" "$STATE/ledger" "$BACKUPS" "$LOGS" "$APP/.docker-cli"
trap 'rm -rf "$ROOT"' EXIT INT TERM

printf 'synthetic-ledger-state\n' > "$STATE/ledger/taskledger.sqlite3"
printf 'services: {}\n' > "$APP/compose.yaml"
printf 'MESH_COS_DEPLOYMENT_RELEASE=4.1.15\n' > "$APP/.env"
printf 'version=4.1.15\ncommit=ad6c5477b167c53cde7e9edac3ad2fd565759f6f\n' > "$APP/release-metadata.txt"

cat > "$BIN/docker" <<'EOF_DOCKER'
#!/bin/sh
set -u
printf '%s\n' "$*" >> "$MOCK_DOCKER_LOG"
case "${1:-}" in
  inspect)
    if [ "${2:-}" = "-f" ]; then
      fmt=${3:-}
      name=${4:-}
      case "$fmt:$name" in
        *State.Running*:mesh-cos-mcp) printf 'true\n' ;;
        *State.Status*:mesh-cos-mcp) printf 'restarting\n' ;;
        *State.Restarting*:mesh-cos-mcp) printf 'true\n' ;;
        *Image*:mesh-cos-mcp) printf 'sha256:active-mesh-image\n' ;;
        *Image*:mesh-cos-tunnel) printf 'sha256:active-tunnel-image\n' ;;
        *) printf 'unknown\n' ;;
      esac
      exit 0
    fi
    case "${2:-}" in
      mesh-cos-mcp|mesh-cos-tunnel) printf '{}\n'; exit 0 ;;
      *) exit 1 ;;
    esac
    ;;
  stop)
    [ "${@: -1}" = "mesh-cos-mcp" ] 2>/dev/null || true
    exit 0
    ;;
  start)
    [ "${2:-}" = "mesh-cos-mcp" ] || exit 3
    exit 0
    ;;
  run)
    if [ "${MOCK_HELPER_FAIL:-0}" = "1" ]; then
      exit 41
    fi
    dest=
    while [ "$#" -gt 0 ]; do
      if [ "$1" = "--destination" ] && [ "$#" -ge 2 ]; then
        dest=$2
        break
      fi
      shift
    done
    [ -n "$dest" ] || exit 42
    case "$dest" in
      /var/lib/mesh/*) rel=${dest#/var/lib/mesh/} ;;
      *) exit 43 ;;
    esac
    mkdir -p "$MOCK_STATE_ROOT/$(dirname "$rel")"
    cp "$MOCK_STATE_ROOT/ledger/taskledger.sqlite3" "$MOCK_STATE_ROOT/$rel"
    exit 0
    ;;
  exec)
    echo 'docker exec must not be used against a restarting runtime' >&2
    exit 97
    ;;
  cp)
    echo 'docker cp must not be used for quiesced host-state backup' >&2
    exit 98
    ;;
  ps|logs|--version)
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
EOF_DOCKER
chmod 0755 "$BIN/docker"

export PATH="$BIN:$PATH"
export MOCK_DOCKER_LOG="$COMMAND_LOG"
export MOCK_STATE_ROOT="$STATE"
export QNAP_APP_ROOT="$APP"
export QNAP_MESH_ROOT="$STATE"
export QNAP_BACKUP_ROOT="$BACKUPS"
export MESH_COS_LOG_ROOT="$LOGS"
export MESH_COS_DOCKER_CONFIG="$APP/.docker-cli"
export MESH_UID=65532
export MESH_GID=65532

SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd -P)
export QNAP_SCRIPT_ROOT="$SCRIPT_ROOT"

sh "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" pre-deploy > "$ROOT/success.out" 2>&1 || {
  cat "$ROOT/success.out" >&2
  echo 'FAIL restarting runtime was not backed up through the quiesced path' >&2
  exit 1
}

if grep -q '^exec ' "$COMMAND_LOG"; then
  echo 'FAIL docker exec was attempted against the restarting runtime' >&2
  exit 1
fi
grep -q '^stop .*mesh-cos-mcp' "$COMMAND_LOG" || {
  echo 'FAIL restarting runtime was not quiesced' >&2
  exit 1
}
grep -q '^run .*--network none .*sha256:active-mesh-image .*sqlite_backup.py .*--source /var/lib/mesh/ledger/taskledger.sqlite3 .*--destination /var/lib/mesh/runtime/' "$COMMAND_LOG" || {
  echo 'FAIL network-isolated SQLite helper was not used with the active image and canonical state' >&2
  cat "$COMMAND_LOG" >&2
  exit 1
}
grep -q '^start mesh-cos-mcp' "$COMMAND_LOG" || {
  echo 'FAIL prior running intent was not restored after backup' >&2
  exit 1
}
DEST=$(find "$BACKUPS" -mindepth 1 -maxdepth 1 -type d | head -n 1)
[ -n "$DEST" ] && [ -s "$DEST/taskledger.sqlite3" ] || {
  echo 'FAIL governed backup artifact was not exported' >&2
  exit 1
}
grep -q '^state_export_method=quiesced_helper$' "$DEST/deployment-state.txt" || {
  echo 'FAIL backup evidence does not identify the quiesced helper path' >&2
  exit 1
}

: > "$COMMAND_LOG"
rm -rf "$BACKUPS"/*
export MOCK_HELPER_FAIL=1
if sh "$SCRIPT_ROOT/mesh-cos-mcp-backup.sh" pre-deploy > "$ROOT/failure.out" 2>&1; then
  echo 'FAIL helper failure was incorrectly accepted' >&2
  exit 1
fi
grep -q '^stop .*mesh-cos-mcp' "$COMMAND_LOG" || exit 1
grep -q '^start mesh-cos-mcp' "$COMMAND_LOG" || {
  echo 'FAIL prior running intent was not restored after helper failure' >&2
  exit 1
}
if find "$BACKUPS" -mindepth 1 -maxdepth 1 -type d | grep -q .; then
  echo 'FAIL failed backup left a partial governed backup directory' >&2
  exit 1
fi

echo 'PASS restarting QNAP runtime uses quiesced helper backup, restores prior intent, and fails closed on helper error'
