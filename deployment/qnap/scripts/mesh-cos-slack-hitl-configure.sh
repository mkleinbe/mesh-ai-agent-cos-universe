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
BOT_TOKEN_FILE=${QNAP_SLACK_BOT_TOKEN_FILE:-$SECRET_DIR/slack-bot-token}
DEFAULT_APPROVER_USER_ID=${MESH_COS_SLACK_APPROVER_USER_ID:-U01KG3CNYHK}
MESH_UID=${MESH_UID:-65532}
MESH_GID=${MESH_GID:-65532}
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
PERM_LIB="$SCRIPT_ROOT/mesh-cos-qnap-permissions.sh"
PROVISION_SCRIPT="$SCRIPT_ROOT/mesh-cos-slack-hitl-provision.sh"
MESH_COS_SCRIPT=mesh-cos-slack-hitl-configure.sh
export QNAP_SCRIPT_ROOT QNAP_BUNDLE_APP_ROOT QNAP_APP_ROOT MESH_UID MESH_GID MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init slack-hitl-configure || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }
[ -r "$PERM_LIB" ] || mesh_fail 1 bootstrap "runtime permission helper missing: $PERM_LIB"
. "$PERM_LIB"

fail() { mesh_fail 1 "${MESH_COS_STAGE:-slack_hitl_configure}" "$1"; }
info() { mesh_log INFO info "$1"; }

write_protected_file() {
  target=$1
  value=$2
  incoming="$target.incoming.$$"
  umask 077
  printf '%s' "$value" > "$incoming" || fail "unable to write protected runtime file"
  chmod 0400 "$incoming" 2>/dev/null || { rm -f "$incoming"; fail "unable to set protected runtime file mode"; }
  mv "$incoming" "$target" || { rm -f "$incoming"; fail "unable to install protected runtime file"; }
}

normalize_native_trigger_env() {
  incoming="$CANDIDATE_ENV_FILE.native.$$"
  sed \
    -e '/^QNAP_SLACK_SOCKET_APP_TOKEN_FILE=/d' \
    -e '/^MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE=/d' \
    -e '/^MESH_COS_SLACK_BRIDGE_TIMEOUT_MS=/d' \
    -e '/^MESH_COS_SLACK_HITL_MODE=/d' \
    "$CANDIDATE_ENV_FILE" > "$incoming" || fail "unable to normalize candidate Slack HITL environment"
  printf '%s\n' 'MESH_COS_SLACK_HITL_MODE=CHATGPT_NATIVE_EVENT_TRIGGER' >> "$incoming" || { rm -f "$incoming"; fail "unable to set native Slack HITL mode"; }
  chmod 0640 "$incoming" 2>/dev/null || { rm -f "$incoming"; fail "unable to protect normalized candidate environment"; }
  mv "$incoming" "$CANDIDATE_ENV_FILE" || { rm -f "$incoming"; fail "unable to install normalized candidate environment"; }
}

validate_approver_user_id() {
  APPROVER_VALUE_TO_VALIDATE=$1
  case "$APPROVER_VALUE_TO_VALIDATE" in
    D*) fail "Slack conversation/DM channel ID is not a user ID; expected a Slack user ID beginning with U or W" ;;
  esac
  printf '%s' "$APPROVER_VALUE_TO_VALIDATE" | grep -Eq '^[UW][A-Z0-9]+$' || fail "Slack approver user ID format is invalid; expected a Slack user ID beginning with U or W"
  unset APPROVER_VALUE_TO_VALIDATE
}

validate_bot_file() {
  [ -s "$BOT_TOKEN_FILE" ] || fail "Slack bot OAuth token file is missing; provision it with: sudo sh $PROVISION_SCRIPT"
  BOT_VALUE=$(cat "$BOT_TOKEN_FILE") || fail "unable to read existing Slack bot OAuth token file"
  case "$BOT_VALUE" in
    xoxb-*) ;;
    *) unset BOT_VALUE; fail "Slack bot OAuth token file is invalid; expected an xoxb token" ;;
  esac
  unset BOT_VALUE
}

mesh_set_stage prepared_release
[ -r "$CANDIDATE_ENV_FILE" ] || fail "prepared candidate release .env.runtime is required; run mesh-cos-mcp-prepare.sh first"
normalize_native_trigger_env
set -a
. "$CANDIDATE_ENV_FILE"
set +a
MESH_IMAGE=${MESH_COS_IMAGE:-}
[ -n "$MESH_IMAGE" ] || fail "prepared candidate release does not define MESH_COS_IMAGE"
docker image inspect "$MESH_IMAGE" >/dev/null 2>&1 || fail "prepared Mesh candidate release image is unavailable"
[ "${MESH_COS_SLACK_HITL_MODE:-}" = "CHATGPT_NATIVE_EVENT_TRIGGER" ] || fail "prepared release is not configured for ChatGPT native Slack event-triggered HITL"
[ -z "${MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE:-}" ] || fail "legacy Slack Socket Mode must not be configured for v4.2.0"
[ -z "${QNAP_SLACK_SOCKET_APP_TOKEN_FILE:-}" ] || fail "legacy QNAP Slack Socket Mode path must not remain after normalization"

mesh_set_stage filesystem
mkdir -p "$SECRET_DIR" || fail "unable to create Slack HITL secrets directory"
chmod 0700 "$SECRET_DIR" 2>/dev/null || fail "unable to set Slack HITL secrets directory mode"

if [ "${MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0}" = "1" ]; then
  fail "forced Slack credential reconfiguration is not allowed in the deploy path; run: sudo sh $PROVISION_SCRIPT"
fi

mesh_set_stage approver_identity
if [ ! -s "$APPROVER_FILE" ]; then
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

mesh_set_stage bot_oauth_token
validate_bot_file
info "preserving existing validated Slack bot OAuth token file"

mesh_set_stage permissions
mesh_apply_secret_permissions "$MESH_IMAGE" "$MESH_UID" "$MESH_GID" "$SECRET_DIR" || fail "unable to normalize Slack HITL secret ownership/modes"
[ -s "$APPROVER_FILE" ] || fail "Slack approver identity file is missing or empty"
[ -s "$BOT_TOKEN_FILE" ] || fail "Slack bot OAuth token file is missing or empty"
mesh_log INFO slack_hitl_permissions "owner=$MESH_UID:$MESH_GID mode=0400 values_logged=false socket_required=false bot_required=true"

mesh_set_stage complete
info "Slack HITL protected runtime configuration complete for ChatGPT native event-trigger mode"
mesh_log INFO slack_hitl_configure_complete "result=PASS values_logged=false non_interactive=true socket_required=false bot_required=true"
