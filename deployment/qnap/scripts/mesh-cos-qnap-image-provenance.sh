#!/bin/sh

mesh_release_metadata_value() {
  key=$1
  metadata=$2
  sed -n "s/^${key}=//p" "$metadata" | head -n 1
}

mesh_image_label() {
  image=$1
  label=$2
  docker image inspect --format "{{ index .Config.Labels \"$label\" }}" "$image" 2>/dev/null || true
}

mesh_image_provenance_matches() {
  image=$1
  expected_version=$2
  expected_revision=$3

  actual_version=$(mesh_image_label "$image" org.opencontainers.image.version)
  actual_revision=$(mesh_image_label "$image" org.opencontainers.image.revision)

  [ "$actual_version" = "$expected_version" ] && [ "$actual_revision" = "$expected_revision" ]
}

mesh_image_provenance_fields() {
  image=$1
  version=$(mesh_image_label "$image" org.opencontainers.image.version)
  revision=$(mesh_image_label "$image" org.opencontainers.image.revision)
  printf '%s\n%s\n' "$version" "$revision"
}
