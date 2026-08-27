#!/bin/sh
set -u

SCRIPT_ROOT=${QNAP_SCRIPT_ROOT:-}
if [ -z "$SCRIPT_ROOT" ]; then
  SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || { echo "ERROR: unable to resolve deployment bundle root" >&2; exit 1; }
fi
APP_ROOT=${QNAP_APP_ROOT:-/share/Docker/cos-mcp}
SECRET_DIR="$APP_ROOT/secrets"
VERIFIER_FILE=${QNAP_SLACK_VERIFIER_TOKEN_FILE:-$SECRET_DIR/slack-verifier-token}
SOCKET_APP_FILE=${QNAP_SLACK_SOCKET_APP_TOKEN_FILE:-$SECRET_DIR/slack-socket-app-token}
OBS_LIB="$SCRIPT_ROOT/mesh-cos-qnap-observability.sh"
MESH_COS_SCRIPT=mesh-cos-slack-hitl-provision.sh
export QNAP_SCRIPT_ROOT QNAP_APP_ROOT MESH_COS_SCRIPT

[ -r "$OBS_LIB" ] || { echo "ERROR: observability helper missing: $OBS_LIB" >&2; exit 1; }
. "$OBS_LIB"
mesh_obs_init slack-hitl-provision || { echo "ERROR: unable to initialize deployment logging" >&2; exit 1; }

fail() { mesh_fail 1 "${MESH_COS_STAGE:-slack_hitl_provision}" "$1"; }
info() { mesh_log INFO info "$1"; }

find_stty() {
  STTY_BIN=
  candidate=$(command -v stty 2>/dev/null || true)
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then
    STTY_BIN=$candidate
    return 0
  fi
  for candidate in /bin/stty /usr/bin/stty; do
    if [ -x "$candidate" ]; then
      STTY_BIN=$candidate
      return 0
    fi
  done
  return 1
}

shell_supports_silent_read() {
  (IFS= read -r -s _mesh_probe < /dev/null) 2>/dev/null
  rc=$?
  [ "$rc" -eq 0 ] || [ "$rc" -eq 1 ]
}

read_secret_tty() {
  prompt=$1
  label=$2
  [ -r /dev/tty ] && [ -w /dev/tty ] || fail "$label provisioning requires a readable and writable controlling TTY"
  printf '%s' "$prompt" > /dev/tty
  SECRET_VALUE=

  if shell_supports_silent_read; then
    IFS= read -r -s SECRET_VALUE < /dev/tty || fail "unable to read $label"
  elif find_stty; then
    trap '"$STTY_BIN" echo < /dev/tty >/dev/null 2>&1 || true' 0 1 2 15
    "$STTY_BIN" -echo < /dev/tty || fail "unable to disable terminal echo for $label"
    IFS= read -r SECRET_VALUE < /dev/tty || {
      "$STTY_BIN" echo < /dev/tty >/dev/null 2>&1 || true
      fail "unable to read $label"
    }
    "$STTY_BIN" echo < /dev/tty >/dev/null 2>&1 || true
    trap - 0 1 2 15
  else
    printf '\n' > /dev/tty
    fail "$label cannot be provisioned safely: this shell lacks silent read and no usable stty binary was found"
  fi

  printf '\n' > /dev/tty
  mesh_log INFO secret_input "kind=$label status=captured value_logged=false"
}

write_protected_file() {
  target=$1
  value=$2
  incoming="$target.incoming.$$"
  umask 077
  printf '%s' "$value" > "$incoming" || fail "unable to write protected runtime file"
  chmod 0400 "$incoming" 2>/dev/null || { rm -f "$incoming"; fail "unable to set protected runtime file mode"; }
  mv "$incoming" "$target" || { rm -f "$incoming"; fail "unable to install protected runtime file"; }
}

provision_verifier() {
  if [ -s "$VERIFIER_FILE" ] && [ "${MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0}" != "1" ]; then
    info "preserving existing Slack verifier token file"
    return 0
  fi
  read_secret_tty "Slack read-only verifier bot token (input hidden): " "Slack verifier token"
  [ -n "$SECRET_VALUE" ] || fail "Slack verifier token cannot be empty"
  case "$SECRET_VALUE" in
    xoxb-*) ;;
    *) unset SECRET_VALUE; fail "Slack verifier must use a bot token beginning with xoxb-" ;;
  esac
  write_protected_file "$VERIFIER_FILE" "$SECRET_VALUE"
  unset SECRET_VALUE
  mesh_log INFO slack_verifier_file "status=provisioned value_logged=false"
}

provision_socket() {
  if [ -s "$SOCKET_APP_FILE" ] && [ "${MESH_COS_FORCE_SLACK_HITL_RECONFIGURE:-0}" != "1" ]; then
    info "preserving existing Slack Socket Mode app token file"
    return 0
  fi
  read_secret_tty "Slack Socket Mode app-level token (input hidden): " "Slack Socket Mode app token"
  [ -n "$SECRET_VALUE" ] || fail "Slack Socket Mode app token cannot be empty"
  case "$SECRET_VALUE" in
    xapp-*) ;;
    *) unset SECRET_VALUE; fail "Slack Socket Mode requires an app-level token beginning with xapp-" ;;
  esac
  write_protected_file "$SOCKET_APP_FILE" "$SECRET_VALUE"
  unset SECRET_VALUE
  mesh_log INFO slack_socket_app_file "status=provisioned value_logged=false"
}

mesh_set_stage filesystem
mkdir -p "$SECRET_DIR" || fail "unable to create Slack HITL secrets directory"
chmod 0700 "$SECRET_DIR" 2>/dev/null || fail "unable to set Slack HITL secrets directory mode"

mesh_set_stage verifier_token
provision_verifier

mesh_set_stage socket_app_token
provision_socket

mesh_set_stage complete
info "Slack HITL protected credentials provisioned; rerun the normal deployment command"
mesh_log INFO slack_hitl_provision_complete "result=PASS values_logged=false"
