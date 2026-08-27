#!/bin/sh
set -u

TMP=${TMPDIR:-/tmp}/mesh-promotion-test.$$
trap 'rm -rf "$TMP"' 0 1 2 15
APP="$TMP/app"
CANDIDATE="$TMP/candidate"
ROLLBACK="$TMP/rollback"
mkdir -p "$APP" "$CANDIDATE"

printf 'release=old\n' > "$APP/.env"
printf 'compose=old\n' > "$APP/compose.yaml"
# release-metadata.txt is intentionally absent to prove absence restoration.
printf 'release=new\n' > "$CANDIDATE/.env.runtime"
printf 'compose=new\n' > "$CANDIDATE/compose.yaml"
printf 'version=4.1.15\n' > "$CANDIDATE/release-metadata.txt"

SCRIPT_ROOT="$(CDPATH= cd "$(dirname "$0")/../scripts" 2>/dev/null && pwd -P)"
. "$SCRIPT_ROOT/mesh-cos-qnap-promotion.sh"

mesh_snapshot_active_configuration "$APP" "$ROLLBACK" || {
  echo 'FAIL unable to snapshot active configuration' >&2
  exit 1
}

mesh_promote_candidate_configuration \
  "$CANDIDATE/.env.runtime" \
  "$CANDIDATE/compose.yaml" \
  "$CANDIDATE/release-metadata.txt" \
  "$APP" || {
  echo 'FAIL successful candidate promotion was rejected' >&2
  exit 1
}

grep -q 'release=new' "$APP/.env"
grep -q 'compose=new' "$APP/compose.yaml"
grep -q 'version=4.1.15' "$APP/release-metadata.txt"

mesh_restore_active_configuration "$APP" "$ROLLBACK" || {
  echo 'FAIL unable to restore active configuration' >&2
  exit 1
}
grep -q 'release=old' "$APP/.env"
grep -q 'compose=old' "$APP/compose.yaml"
[ ! -e "$APP/release-metadata.txt" ] || {
  echo 'FAIL originally absent release metadata was not removed on restore' >&2
  exit 1
}

# Re-snapshot and force a failure after the first file has already promoted.
rm -rf "$ROLLBACK"
mesh_snapshot_active_configuration "$APP" "$ROLLBACK" || exit 1
rm -f "$CANDIDATE/compose.yaml"
if mesh_promote_candidate_configuration \
  "$CANDIDATE/.env.runtime" \
  "$CANDIDATE/compose.yaml" \
  "$CANDIDATE/release-metadata.txt" \
  "$APP"; then
  echo 'FAIL partial promotion failure was not detected' >&2
  exit 1
fi
grep -q 'release=new' "$APP/.env" || {
  echo 'FAIL test did not exercise a partial promotion' >&2
  exit 1
}
mesh_restore_active_configuration "$APP" "$ROLLBACK" || {
  echo 'FAIL partial promotion rollback did not restore snapshot' >&2
  exit 1
}
grep -q 'release=old' "$APP/.env"
grep -q 'compose=old' "$APP/compose.yaml"
[ ! -e "$APP/release-metadata.txt" ]

mesh_cleanup_configuration_snapshot "$ROLLBACK" || exit 1
[ ! -e "$ROLLBACK" ] || {
  echo 'FAIL rollback snapshot cleanup failed' >&2
  exit 1
}

if mesh_cleanup_configuration_snapshot ""; then
  echo 'FAIL empty rollback directory was accepted' >&2
  exit 1
fi
if mesh_cleanup_configuration_snapshot "/"; then
  echo 'FAIL filesystem root was accepted as rollback directory' >&2
  exit 1
fi

echo 'PASS QNAP release configuration promotion is snapshot-backed, recoverable, and cleanup-path constrained'
