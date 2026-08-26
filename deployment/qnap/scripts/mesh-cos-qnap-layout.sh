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

mesh_canonical_dir() {
  directory=$1
  [ -d "$directory" ] || return 1
  (CDPATH= cd "$directory" 2>/dev/null && pwd -P)
}

mesh_validate_release_root() {
  release_root=$1
  metadata=$2
  releases_root=${QNAP_RELEASES_ROOT:-/share/Docker/cos-mcp/releases}

  candidate=$(mesh_candidate_release "$metadata") || {
    echo "release metadata version is not a valid runtime semantic version" >&2
    return 1
  }
  release_name=${release_root##*/}
  expected_name="v${candidate}"
  if [ "$release_name" != "$expected_name" ]; then
    echo "release directory version does not match staged metadata: directory=$release_name metadata=$candidate" >&2
    return 1
  fi

  actual_parent=$(mesh_canonical_dir "$release_root/..") || {
    echo "unable to resolve release directory parent: $release_root" >&2
    return 1
  }
  expected_parent=$(mesh_canonical_dir "$releases_root") || {
    echo "canonical releases root is missing or unreadable: $releases_root" >&2
    return 1
  }
  if [ "$actual_parent" != "$expected_parent" ]; then
    echo "release directory must be under canonical releases root: expected=$expected_parent actual=$actual_parent" >&2
    return 1
  fi
  return 0
}
