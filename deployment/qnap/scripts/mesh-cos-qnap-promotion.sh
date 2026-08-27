#!/bin/sh
# Sourced helper for transactional promotion of active QNAP release configuration.

mesh_safe_rollback_dir() {
  rollback_dir=$1
  [ -n "$rollback_dir" ] || return 1
  [ "$rollback_dir" != "/" ] || return 1
  [ "$rollback_dir" != "." ] || return 1
  [ "$rollback_dir" != ".." ] || return 1
}

mesh_snapshot_path() {
  source=$1
  snapshot=$2
  absent_marker=$3
  rm -f "$snapshot" "$absent_marker" || return 1
  if [ -f "$source" ]; then
    cp "$source" "$snapshot" || return 1
  else
    : > "$absent_marker" || return 1
  fi
}

mesh_snapshot_active_configuration() {
  app_root=$1
  rollback_dir=$2

  mesh_safe_rollback_dir "$rollback_dir" || return 64
  mkdir -p "$rollback_dir" || return 1
  chmod 0700 "$rollback_dir" 2>/dev/null || { rm -rf "$rollback_dir"; return 1; }
  if ! mesh_snapshot_path "$app_root/.env" "$rollback_dir/.env" "$rollback_dir/.env.absent" \
    || ! mesh_snapshot_path "$app_root/compose.yaml" "$rollback_dir/compose.yaml" "$rollback_dir/compose.yaml.absent" \
    || ! mesh_snapshot_path "$app_root/release-metadata.txt" "$rollback_dir/release-metadata.txt" "$rollback_dir/release-metadata.txt.absent"; then
    rm -rf "$rollback_dir"
    return 1
  fi
}

mesh_promote_one() {
  source=$1
  target=$2
  mode=$3
  incoming="$target.incoming.$$"

  rm -f "$incoming" || return 1
  cp "$source" "$incoming" || return 1
  chmod "$mode" "$incoming" 2>/dev/null || { rm -f "$incoming"; return 1; }
  mv "$incoming" "$target" || { rm -f "$incoming"; return 1; }
}

mesh_promote_candidate_configuration() {
  candidate_env=$1
  candidate_compose=$2
  candidate_metadata=$3
  app_root=$4

  mesh_promote_one "$candidate_env" "$app_root/.env" 0640 || return 1
  mesh_promote_one "$candidate_compose" "$app_root/compose.yaml" 0644 || return 1
  mesh_promote_one "$candidate_metadata" "$app_root/release-metadata.txt" 0644 || return 1
}

mesh_restore_one() {
  snapshot=$1
  absent_marker=$2
  target=$3
  mode=$4

  if [ -f "$absent_marker" ]; then
    rm -f "$target" || return 1
    return 0
  fi
  [ -f "$snapshot" ] || return 1
  mesh_promote_one "$snapshot" "$target" "$mode"
}

mesh_restore_active_configuration() {
  app_root=$1
  rollback_dir=$2

  mesh_safe_rollback_dir "$rollback_dir" || return 64
  [ -d "$rollback_dir" ] || return 66
  mesh_restore_one "$rollback_dir/.env" "$rollback_dir/.env.absent" "$app_root/.env" 0640 || return 1
  mesh_restore_one "$rollback_dir/compose.yaml" "$rollback_dir/compose.yaml.absent" "$app_root/compose.yaml" 0644 || return 1
  mesh_restore_one "$rollback_dir/release-metadata.txt" "$rollback_dir/release-metadata.txt.absent" "$app_root/release-metadata.txt" 0644 || return 1
}

mesh_cleanup_configuration_snapshot() {
  rollback_dir=$1
  mesh_safe_rollback_dir "$rollback_dir" || return 64
  rm -rf "$rollback_dir"
}
