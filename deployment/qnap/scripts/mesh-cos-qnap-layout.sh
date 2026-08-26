#!/bin/sh

mesh_normalize_release() {
  case "${1:-}" in
    v*) printf '%s\n' "${1#v}" ;;
    *) printf '%s\n' "${1:-}" ;;
  esac
}

mesh_release_is_semver() {
  printf '%s\n' "${1:-}" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$'
}

mesh_release_metadata_value() {
  key=$1
  file=$2
  [ -r "$file" ] || return 1
  awk -F= -v key="$key" '$1 == key {print $2; exit}' "$file"
}

mesh_candidate_release() {
  metadata=$1
  raw=$(mesh_release_metadata_value version "$metadata") || return 1
  normalized=$(mesh_normalize_release "$raw")
  mesh_release_is_semver "$normalized" || return 1
  printf '%s\n' "$normalized"
}
