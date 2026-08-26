#!/bin/sh
set -u

ROOT=$(CDPATH= cd "$(dirname "$0")/../../.." 2>/dev/null && pwd -P) || exit 1
SCRIPTS="$ROOT/deployment/qnap/scripts"
LAYOUT="$SCRIPTS/mesh-cos-qnap-layout.sh"

[ -r "$LAYOUT" ] || { echo "missing layout helper" >&2; exit 1; }
. "$LAYOUT"

[ "$(mesh_normalize_release v4.1.11)" = "4.1.11" ] || { echo "v-prefix normalization failed" >&2; exit 1; }
[ "$(mesh_normalize_release 4.1.11)" = "4.1.11" ] || { echo "runtime release normalization failed" >&2; exit 1; }
mesh_release_is_semver 4.1.11 || { echo "valid semantic release rejected" >&2; exit 1; }
if mesh_release_is_semver v4.1.11; then echo "tag form accepted as runtime semver" >&2; exit 1; fi
if mesh_release_is_semver 4.1; then echo "invalid semantic release accepted" >&2; exit 1; fi

TMP=${TMPDIR:-/tmp}/mesh-cos-layout-$$
trap 'rm -rf "$TMP"' 0 1 2 15
mkdir -p "$TMP/cos-mcp"
printf 'tag=v4.1.11\nversion=4.1.11\ncommit=0123456789abcdef0123456789abcdef01234567\n' > "$TMP/cos-mcp/release-metadata.txt"
[ "$(mesh_candidate_release "$TMP/cos-mcp/release-metadata.txt")" = "4.1.11" ] || { echo "candidate metadata resolution failed" >&2; exit 1; }

for name in mesh-cos-mcp-deploy.sh mesh-cos-mcp-prepare.sh mesh-cos-mcp-preflight.sh mesh-cos-mcp-backup.sh mesh-cos-mcp-verify.sh mesh-cos-slack-hitl-configure.sh; do
  file="$SCRIPTS/$name"
  grep -q 'dirname "$0"' "$file" || { echo "$name does not self-resolve its bundle root" >&2; exit 1; }
  grep -q 'pwd -P' "$file" || { echo "$name does not canonicalize its bundle root" >&2; exit 1; }
  if grep -q 'QNAP_SCRIPT_ROOT:-/share/Docker' "$file"; then
    echo "$name still hard-codes /share/Docker as its helper root" >&2
    exit 1
  fi
done

grep -q 'RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"' "$SCRIPTS/mesh-cos-mcp-prepare.sh" || { echo "prepare does not bind staged metadata" >&2; exit 1; }
grep -q 'CANDIDATE_ENV="$BUNDLE_APP_ROOT/.env.runtime"' "$SCRIPTS/mesh-cos-mcp-prepare.sh" || { echo "prepare does not stage runtime env" >&2; exit 1; }
grep -q 'ACTIVE_ENV_FILE="$APP_ROOT/.env"' "$SCRIPTS/mesh-cos-mcp-preflight.sh" || { echo "preflight does not distinguish active env" >&2; exit 1; }
grep -q 'CANDIDATE_ENV_FILE="$BUNDLE_APP_ROOT/.env.runtime"' "$SCRIPTS/mesh-cos-mcp-preflight.sh" || { echo "preflight does not distinguish candidate env" >&2; exit 1; }

echo "PASS versioned release layout and normalization regression"
