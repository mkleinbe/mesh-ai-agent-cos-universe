#!/bin/sh
# Sourced helper for runtime ownership on QNAP where the SSH operator may use Docker
# but may not chown shared-folder paths directly.

mesh_validate_runtime_identity() {
  uid=$1
  gid=$2
  case "$uid" in ''|*[!0-9]*) return 1 ;; esac
  case "$gid" in ''|*[!0-9]*) return 1 ;; esac
  [ "$uid" -gt 0 ] 2>/dev/null || return 1
  [ "$gid" -gt 0 ] 2>/dev/null || return 1
}

mesh_apply_state_permissions() {
  image=$1
  uid=$2
  gid=$3
  state_root=$4

  mesh_validate_runtime_identity "$uid" "$gid" || return 64
  [ -d "$state_root" ] || return 66

  mesh_run runtime_permissions state-ownership-helper \
    docker run --rm \
      --network none \
      --read-only \
      --user 0:0 \
      --cap-drop ALL \
      --cap-add CHOWN \
      --cap-add FOWNER \
      --cap-add DAC_OVERRIDE \
      --security-opt no-new-privileges \
      -v "$state_root:/mesh-state:rw" \
      --entrypoint /bin/sh "$image" \
      -c '
        set -eu
        uid=$1
        gid=$2
        mkdir -p /mesh-state/ledger /mesh-state/governance /mesh-state/audit /mesh-state/runtime
        chown -R "$uid:$gid" /mesh-state
        find /mesh-state -type d -exec chmod 0711 {} \;
        find /mesh-state -type f -exec chmod 0660 {} \;
      ' sh "$uid" "$gid"
}

mesh_stage_ledger() {
  image=$1
  uid=$2
  gid=$3
  state_root=$4
  source_file=$5

  mesh_validate_runtime_identity "$uid" "$gid" || return 64
  [ -r "$source_file" ] || return 66
  [ -s "$source_file" ] || return 65

  mesh_run_stdin_file ledger_stage canonical-ledger-stream "$source_file" \
    docker run --rm -i \
      --network none \
      --read-only \
      --user "$uid:$gid" \
      --cap-drop ALL \
      --security-opt no-new-privileges \
      -v "$state_root:/var/lib/mesh:rw" \
      --entrypoint /bin/sh "$image" \
      -c '
        set -eu
        target=/var/lib/mesh/ledger/taskledger.sqlite3
        tmp="$target.incoming.$$"
        trap "rm -f \"$tmp\"" 0 1 2 15
        umask 077
        cat > "$tmp"
        test -s "$tmp"
        chmod 0660 "$tmp"
        mv "$tmp" "$target"
        trap - 0 1 2 15
      '
}

mesh_apply_secret_permissions() {
  image=$1
  uid=$2
  gid=$3
  secrets_root=$4

  mesh_validate_runtime_identity "$uid" "$gid" || return 64
  [ -d "$secrets_root" ] || return 66

  mesh_run runtime_permissions secret-ownership-helper \
    docker run --rm \
      --network none \
      --read-only \
      --user 0:0 \
      --cap-drop ALL \
      --cap-add CHOWN \
      --cap-add FOWNER \
      --cap-add DAC_OVERRIDE \
      --security-opt no-new-privileges \
      -v "$secrets_root:/mesh-secrets:rw" \
      --entrypoint /bin/sh "$image" \
      -c '
        set -eu
        uid=$1
        gid=$2
        secret=/mesh-secrets/openai-tunnel-runtime-key
        test -f "$secret"
        chown "$uid:$gid" "$secret"
        chmod 0400 "$secret"
      ' sh "$uid" "$gid"
}
