#!/bin/sh
# Shared QNAP/BusyBox-compatible no-echo secret input helper.
# Callers must define their own fail/logging behavior and must never log MESH_SECRET_VALUE.

mesh_find_stty() {
  MESH_STTY_BIN=
  mesh_stty_candidate=$(command -v stty 2>/dev/null || true)
  if [ -n "$mesh_stty_candidate" ] && [ -x "$mesh_stty_candidate" ]; then
    MESH_STTY_BIN=$mesh_stty_candidate
    return 0
  fi
  for mesh_stty_candidate in /bin/stty /usr/bin/stty; do
    if [ -x "$mesh_stty_candidate" ]; then
      MESH_STTY_BIN=$mesh_stty_candidate
      return 0
    fi
  done
  return 1
}

mesh_shell_supports_silent_read() {
  (IFS= read -r -s _mesh_secret_probe < /dev/null) 2>/dev/null
  mesh_read_rc=$?
  [ "$mesh_read_rc" -eq 0 ] || [ "$mesh_read_rc" -eq 1 ]
}

mesh_restore_tty_echo() {
  if [ -n "${MESH_STTY_BIN:-}" ]; then
    "$MESH_STTY_BIN" echo < /dev/tty >/dev/null 2>&1 || true
  fi
}

mesh_read_secret_tty() {
  mesh_secret_prompt=$1
  mesh_secret_label=$2
  MESH_SECRET_VALUE=

  if [ ! -r /dev/tty ] || [ ! -w /dev/tty ]; then
    printf 'ERROR: %s provisioning requires a readable and writable controlling TTY\n' "$mesh_secret_label" >&2
    return 1
  fi

  printf '%s' "$mesh_secret_prompt" > /dev/tty
  if mesh_shell_supports_silent_read; then
    if ! IFS= read -r -s MESH_SECRET_VALUE < /dev/tty; then
      printf '\nERROR: unable to read %s\n' "$mesh_secret_label" > /dev/tty
      return 1
    fi
  elif mesh_find_stty; then
    trap 'mesh_restore_tty_echo' 0 1 2 15
    if ! "$MESH_STTY_BIN" -echo < /dev/tty; then
      trap - 0 1 2 15
      printf '\nERROR: unable to disable terminal echo for %s\n' "$mesh_secret_label" > /dev/tty
      return 1
    fi
    if ! IFS= read -r MESH_SECRET_VALUE < /dev/tty; then
      mesh_restore_tty_echo
      trap - 0 1 2 15
      printf '\nERROR: unable to read %s\n' "$mesh_secret_label" > /dev/tty
      return 1
    fi
    mesh_restore_tty_echo
    trap - 0 1 2 15
  else
    printf '\nERROR: %s cannot be provisioned safely: shell silent-read support is unavailable and no usable stty binary was found\n' "$mesh_secret_label" > /dev/tty
    return 1
  fi

  printf '\n' > /dev/tty
  return 0
}
