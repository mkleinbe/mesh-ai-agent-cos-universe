#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
SECRET_DIR="$APP_ROOT/secrets"
SECRET_FILE=${QNAP_TUNNEL_API_KEY_FILE:-$SECRET_DIR/openai-tunnel-runtime-key}
RELEASE_METADATA="$BUNDLE_APP_ROOT/release-metadata.txt"
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
LAYOUT_LIB="$SCRIPT_ROOT/mesh-cos-qnap-layout.sh"
PERM_LIB="$SCRIPT_ROOT/mesh-cos-qnap-permissions.sh"
SECRET_INPUT_LIB="$SCRIPT_ROOT/mesh-cos-qnap-secret-input.sh"
MESH_COS_SCRIPT=mesh-cos-tunnel-key-provision.sh
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT QNAP_TUNNEL_API_KEY_FILE MESH_UID MESH_GID MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init tunnel-key-provision || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
[ -r "$LAYOUT_LIB" ] || mesh_fail 1 bootstrap "release layout helper missing: $LAYOUT_LIB"
. "$LAYOUT_LIB"
[ -r "$PERM_LIB" ] || mesh_fail 1 bootstrap "runtime permission helper missing: $PERM_LIB"
. "$PERM_LIB"
[ -r "$SECRET_INPUT_LIB" ] || mesh_fail 1 bootstrap "protected secret input helper missing: $SECRET_INPUT_LIB"
. "$SECRET_INPUT_LIB"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-tunnel_key_provision}" "$1"; }
info() { mesh_log INFO info "$1"; }

mesh_set_stage prepared_release
[ -r "$RELEASE_METADATA" ] || fail "release metadata is missing: $RELEASE_METADATA"
EXPECTED_RELEASE=$(mesh_candidate_release "$RELEASE_METADATA") || fail "release metadata version is not a valid runtime semantic version"
MESH_IMAGE_TAG=${MESH_COS_LOCAL_TAG:-mesh-cos-mcp:qnap-v${EXPECTED_RELEASE}}
docker image inspect "$MESH_IMAGE_TAG" >/dev/null 2>&1 || fail "prepared Mesh candidate release image is unavailable; run the normal deploy command once before provisioning"

mesh_set_stage filesystem
mkdir -p "$SECRET_DIR" || fail "unable to create protected secrets directory"
chmod 0700 "$SECRET_DIR" 2>/dev/null || fail "unable to set protected secrets directory mode"

if [ -s "$SECRET_FILE" ] && [ "${MESH_COS_FORCE_TUNNEL_KEY_RECONFIGURE:-0}" != "1" ]; then
  info "preserving existing OpenAI tunnel runtime key file"
else
  mesh_set_stage tunnel_key
  mesh_read_secret_tty "OpenAI tunnel runtime API key (input hidden): " "OpenAI tunnel runtime key" || fail "unable to capture tunnel runtime key securely"
  [ -n "$MESH_SECRET_VALUE" ] || fail "tunnel runtime key cannot be empty"
  incoming="$SECRET_FILE.incoming.$$"
  umask 077
  printf '%s' "$MESH_SECRET_VALUE" > "$incoming" || { unset MESH_SECRET_VALUE; fail "unable to write protected tunnel runtime key"; }
  unset MESH_SECRET_VALUE
  chmod 0400 "$incoming" 2>/dev/null || { rm -f "$incoming"; fail "unable to set protected tunnel runtime key mode"; }
  mv "$incoming" "$SECRET_FILE" || { rm -f "$incoming"; fail "unable to install protected tunnel runtime key"; }
  mesh_log INFO tunnel_key_file "status=provisioned value_logged=false"
fi

mesh_set_stage permissions
mesh_apply_secret_permissions "$MESH_IMAGE_TAG" "$MESH_UID" "$MESH_GID" "$SECRET_DIR" || fail "unable to normalize protected secret ownership/modes"
[ -s "$SECRET_FILE" ] || fail "OpenAI tunnel runtime key file is missing or empty after provisioning"
mesh_log INFO tunnel_key_permissions "owner=$MESH_UID:$MESH_GID mode=0400 value_logged=false"

mesh_set_stage complete
info "OpenAI tunnel runtime key provisioned; rerun the normal deployment command"
mesh_log INFO tunnel_key_provision_complete "result=PASS value_logged=false"
