#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
BUNDLE_APP_ROOT=${QNAP_BUNDLE_APP_ROOT:-"$SCRIPT_ROOT/cos-mcp"}
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
CANDIDATE_ENV_FILE=${QNAP_CANDIDATE_ENV_FILE:-"$BUNDLE_APP_ROOT/.env.runtime"}
SECRET_DIR="$APP_ROOT/secrets"
APPROVER_FILE=${QNAP_SLACK_APPROVER_USER_ID_FILE:-$SECRET_DIR/slack-approver-user-id}
VERIFIER_FILE=${QNAP_SLACK_VERIFIER_TOKEN_FILE:-$SECRET_DIR/slack-verifier-token}
SOCKET_APP_FILE=${QNAP_SLACK_SOCKET_APP_TOKEN_FILE:-$SECRET_DIR/slack-socket-app-token}
DEFAULT_APPROVER_USER_ID=${MESH_COS_SLACK_APPROVER_USER_ID:-U01KG3CNYHK}
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
PERM_LIB="$SCRIPT_ROOT/mesh-cos-qnap-permissions.sh"
MESH_COS_SCRIPT=mesh-cos-slack-hitl-configure.sh
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT MESH_UID MESH_GID MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init slack-hitl-configure || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
[ -r "$PERM_LIB" ] || mesh_fail 1 bootstrap "runtime permission helper missing: $PERM_LIB"
. "$PERM_LIB"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-slack_hitl_configure}" "$1"; }
info() { mesh_log INFO info "$1"; }

read_secret_tty() {
  prompt=$1
  label=$2
  [ -r /dev/tty ] || fail "$label input requires a TTY"
  command -v stty >/dev/null 2>&1 || fail "stty is required for hidden secret input"
  printf '%s' "$prompt" > /dev/tty
  trap 'stty echo < /dev/tty >/dev/null 2>&1 || true' 0 1 2 15
  stty -echo < /dev/tty || fail "unable to disable terminal echo"
  IFS= read -r SECRET_VALUE < /dev/tty || {
    stty echo < /dev/tty >/dev/null 2>&1 || true
    fail "unable to read $label"
  }
  stty echo < /dev/tty >/dev/null 2>&1 || true
  printf '\n' > /dev/tty
  trap - 0 1 2 15
  mesh_log INFO secret_input "kind=$label status=captured value_logged=false"
}

write_protected_file() {
  target=$1
  value=$2
  incoming="$target.incoming.$$"
  umask 077
  printf '%s' "$value" > "$incoming" || fail "unable to write protected runtime file"
  mv "$incoming" "$target" || fail "unable to install protected runtime file"
}

validate_approver_user_id() {
  APPROVER_VALUE_TO_VALIDATE=$1
  case "$APPROVER_VALUE_TO_VALIDATE" in
    D*) fail "Slack conversation/DM channel ID is not a user ID; expected a Slack user ID beginning with U or W" ;;
  esac
  printf '%s' "$APPROVER_VALUE_TO_VALIDATE" | grep -Eq '^[UW][A-Z0-9]+$' || fail "Slack approver user ID format is invalid; expected a Slack user ID beginning with U or W"
  unset APPROVER_VALUE_TO_VALIDATE
}

mesh_set_stage prepared_release
[ -r "$CANDIDATE_ENV_FILE" ] || fail "prepared candidate release .env.runtime is required; run mesh-cos-mcp-prepare.sh first"
set -a
. "$CANDIDATE_ENV_FILE"
set +a
MESH_IMAGE=${MESH_COS_IMAGE:-}
[ -n "$MESH_IMAGE" ] || fail "prepared candidate release does not define MESH_COS_IMAGE"
docker image inspect "$MESH_IMAGE" >/dev/null 2>&1 || fail "prepared Mesh candidate release image is unavailable"

mesh_set_stage filesystem
mkdir -p "$SECRET_DIR" || fail "unable to create Slack HITL secrets directory"
chmod 0700 "$SECRET_DIR" 2>/dev/null || fail "unable to set Slack HITL secrets directory mode"

mesh_set_stage approver_identity
if [ "${MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0}" = "1" ] || [ ! -s "$APPROVER_FILE" ]; then
  APPROVER_VALUE=$DEFAULT_APPROVER_USER_ID
  validate_approver_user_id "$APPROVER_VALUE"
  write_protected_file "$APPROVER_FILE" "$APPROVER_VALUE"
  unset APPROVER_VALUE
  mesh_log INFO slack_approver_identity "status=staged source=governed_default value_logged=false"
else
  APPROVER_VALUE=$(cat "$APPROVER_FILE") || fail "unable to read existing Slack approver identity file"
  validate_approver_user_id "$APPROVER_VALUE"
  unset APPROVER_VALUE
  info "preserving existing Slack approver identity file"
fi

mesh_set_stage verifier_token
if [ "${MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0}" = "1" ] || [ ! -s "$VERIFIER_FILE" ]; then
  read_secret_tty "Slack read-only verifier bot token (input hidden): " "Slack verifier token"
  [ -n "$SECRET_VALUE" ] || fail "Slack verifier token cannot be empty"
  printf '%s' "$SECRET_VALUE" | grep -Eq '^xoxb-' || { unset SECRET_VALUE; fail "Slack verifier must use a bot token"; }
  write_protected_file "$VERIFIER_FILE" "$SECRET_VALUE"
  unset SECRET_VALUE
  mesh_log INFO slack_verifier_file "status=staged value_logged=false"
else
  info "preserving existing Slack verifier token file"
fi

mesh_set_stage socket_app_token
if [ "${MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0}" = "1" ] || [ ! -s "$SOCKET_APP_FILE" ]; then
  read_secret_tty "Slack Socket Mode app-level token (input hidden): " "Slack Socket Mode app token"
  [ -n "$SECRET_VALUE" ] || fail "Slack Socket Mode app token cannot be empty"
  printf '%s' "$SECRET_VALUE" | grep -Eq '^xapp-' || { unset SECRET_VALUE; fail "Slack Socket Mode requires an app-level xapp token"; }
  write_protected_file "$SOCKET_APP_FILE" "$SECRET_VALUE"
  unset SECRET_VALUE
  mesh_log INFO slack_socket_app_file "status=staged value_logged=false"
else
  info "preserving existing Slack Socket Mode app token file"
fi

mesh_set_stage permissions
mesh_apply_secret_permissions "$MESH_IMAGE" "$MESH_UID" "$MESH_GID" "$SECRET_DIR" || fail "unable to normalize Slack HITL secret ownership/modes"
[ -s "$APPROVER_FILE" ] || fail "Slack approver identity file is missing or empty"
[ -s "$VERIFIER_FILE" ] || fail "Slack verifier token file is missing or empty"
[ -s "$SOCKET_APP_FILE" ] || fail "Slack Socket Mode app token file is missing or empty"
mesh_log INFO slack_hitl_permissions "owner=$MESH_UID:$MESH_GID mode=0400 values_logged=false"

mesh_set_stage complete
info "Slack HITL protected runtime configuration complete"
mesh_log INFO slack_hitl_configure_complete "result=PASS values_logged=false"
