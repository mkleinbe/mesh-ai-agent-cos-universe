#!/bin/sh
set -u

ROOT=$(CDPATH= cd "$(dirname "$0")/../../.." 2>/dev/null && pwd -P) || exit 1
SCRIPTS="$ROOT/deployment/qnap/scripts"
LAYOUT="$SCRIPTS/mesh-cos-qnap-layout.sh"

[ -r "$LAYOUT" ] || { echo "missing layout helper" >&2; exit 1; }
. "$LAYOUT"

[ "$(mesh_normalize_release v4.1.12)" = "4.1.12" ] || { echo "v-prefix normalization failed" >&2; exit 1; }
[ "$(mesh_normalize_release 4.1.12)" = "4.1.12" ] || { echo "runtime release normalization failed" >&2; exit 1; }
mesh_release_is_semver 4.1.12 || { echo "valid semantic release rejected" >&2; exit 1; }
if mesh_release_is_semver v4.1.12; then echo "tag form accepted as runtime semver" >&2; exit 1; fi
if mesh_release_is_semver 4.1; then echo "invalid semantic release accepted" >&2; exit 1; fi

TMP=${TMPDIR:-/tmp}/mesh-cos-layout-$$
trap 'rm -rf "$TMP"' 0 1 2 15
mkdir -p "$TMP/releases/v4.1.12/cos-mcp" "$TMP/releases/v4.1.99/cos-mcp"
printf 'tag=v4.1.12\nversion=4.1.12\ncommit=0123456789abcdef0123456789abcdef01234567\n' > "$TMP/releases/v4.1.12/cos-mcp/release-metadata.txt"
printf 'tag=v4.1.12\nversion=4.1.12\ncommit=0123456789abcdef0123456789abcdef01234567\n' > "$TMP/releases/v4.1.99/cos-mcp/release-metadata.txt"
[ "$(mesh_candidate_release "$TMP/releases/v4.1.12/cos-mcp/release-metadata.txt")" = "4.1.12" ] || { echo "candidate metadata resolution failed" >&2; exit 1; }
QNAP_RELEASES_ROOT="$TMP/releases"
export QNAP_RELEASES_ROOT
mesh_validate_release_root "$TMP/releases/v4.1.12" "$TMP/releases/v4.1.12/cos-mcp/release-metadata.txt" || { echo "valid canonical release root rejected" >&2; exit 1; }
if mesh_validate_release_root "$TMP/releases/v4.1.99" "$TMP/releases/v4.1.99/cos-mcp/release-metadata.txt" >/dev/null 2>&1; then
  echo "mismatched release directory accepted" >&2
  exit 1
fi

for name in mesh-cos-mcp-deploy.sh mesh-cos-mcp-prepare.sh mesh-cos-mcp-preflight.sh mesh-cos-mcp-backup.sh mesh-cos-mcp-verify.sh mesh-cos-slack-hitl-configure.sh; do
  file="$SCRIPTS/$name"
  grep -q 'dirname "$0"' "$file" || { echo "$name does not self-resolve its bundle root" >&2; exit 1; }
  grep -q 'pwd -P' "$file" || { echo "$name does not canonicalize its bundle root" >&2; exit 1; }
  if grep -q 'QNAP_SCRIPT_ROOT:-/share/Docker' "$file"; then
    echo "$name still hard-codes /share/Docker as its helper root" >&2
    exit 1
  fi
  if grep -Eq 'realpath|readlink -f' "$file"; then
    echo "$name requires a non-BusyBox path helper" >&2
    exit 1
  fi
done

grep -q 'RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"' "$SCRIPTS/mesh-cos-mcp-prepare.sh" || { echo "prepare does not bind staged metadata" >&2; exit 1; }
grep -q 'CANDIDATE_ENV="$BUNDLE_APP_ROOT/.env.runtime"' "$SCRIPTS/mesh-cos-mcp-prepare.sh" || { echo "prepare does not stage runtime env" >&2; exit 1; }
grep -q 'ACTIVE_ENV_FILE="$APP_ROOT/.env"' "$SCRIPTS/mesh-cos-mcp-preflight.sh" || { echo "preflight does not distinguish active env" >&2; exit 1; }
grep -q 'CANDIDATE_ENV_FILE="$BUNDLE_APP_ROOT/.env.runtime"' "$SCRIPTS/mesh-cos-mcp-preflight.sh" || { echo "preflight does not distinguish candidate env" >&2; exit 1; }
grep -q 'mesh_validate_release_root "$SCRIPT_ROOT"' "$SCRIPTS/mesh-cos-mcp-deploy.sh" || { echo "deploy does not validate release root before mutation" >&2; exit 1; }

# Verify the actual current artifact creates one versioned directory when unzipped
# from the canonical releases root. Historical releases retain their published layout.
(
  cd "$ROOT" || exit 1
  bash scripts/build-qnap-release-bundle.sh 4.1.12 >/dev/null
  unzip -Z1 dist/mesh-cos-mcp-qnap-v4.1.12.zip > "$TMP/v4112.entries"
) || exit 1
[ -s "$TMP/v4112.entries" ] || { echo "current release archive is empty" >&2; exit 1; }
if grep -Ev '^v4\.1\.12/' "$TMP/v4112.entries" >/dev/null; then
  echo "current release archive contains entries outside v4.1.12/" >&2
  exit 1
fi
grep -qx 'v4.1.12/mesh-cos-mcp-deploy.sh' "$TMP/v4112.entries" || { echo "current archive missing versioned deploy entry" >&2; exit 1; }
grep -qx 'v4.1.12/cos-mcp/release-metadata.txt' "$TMP/v4112.entries" || { echo "current archive missing versioned release metadata" >&2; exit 1; }

echo "PASS versioned release root, archive bootstrap, and normalization regression"
