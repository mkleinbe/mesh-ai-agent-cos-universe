#!/bin/sh
set -eu

ROOT=${TMPDIR:-/tmp}/mesh-image-provenance-$$
BIN="$ROOT/bin"
META="$ROOT/release-metadata.txt"
mkdir -p "$BIN"
trap 'rm -rf "$ROOT"' EXIT INT TERM

cat > "$META" <<'EOF_META'
tag=v4.1.7
version=4.1.7
commit=0123456789abcdef0123456789abcdef01234567
EOF_META

cat > "$BIN/docker" <<'EOF_DOCKER'
#!/bin/sh
[ "$1" = image ] && [ "$2" = inspect ] || exit 2
case "$4" in
  *org.opencontainers.image.version*) printf '%s\n' "${MOCK_IMAGE_VERSION:-}" ;;
  *org.opencontainers.image.revision*) printf '%s\n' "${MOCK_IMAGE_REVISION:-}" ;;
  *) exit 3 ;;
esac
EOF_DOCKER
chmod 0755 "$BIN/docker"
PATH="$BIN:$PATH"
export PATH

SCRIPT_ROOT=$(CDPATH= cd "$(dirname "$0")/../scripts" && pwd)
. "$SCRIPT_ROOT/mesh-cos-qnap-image-provenance.sh"

test "$(mesh_release_metadata_value version "$META")" = 4.1.7
test "$(mesh_release_metadata_value commit "$META")" = 0123456789abcdef0123456789abcdef01234567

MOCK_IMAGE_VERSION=4.1.7-qnap
MOCK_IMAGE_REVISION=0123456789abcdef0123456789abcdef01234567
export MOCK_IMAGE_VERSION MOCK_IMAGE_REVISION
mesh_image_provenance_matches mesh-cos-mcp:qnap-v4.1.7 4.1.7-qnap 0123456789abcdef0123456789abcdef01234567

MOCK_IMAGE_VERSION=4.1.6-qnap
export MOCK_IMAGE_VERSION
if mesh_image_provenance_matches mesh-cos-mcp:qnap-v4.1.7 4.1.7-qnap 0123456789abcdef0123456789abcdef01234567; then
  echo 'FAIL stale image version was accepted' >&2
  exit 1
fi

MOCK_IMAGE_VERSION=4.1.7-qnap
MOCK_IMAGE_REVISION=ffffffffffffffffffffffffffffffffffffffff
export MOCK_IMAGE_VERSION MOCK_IMAGE_REVISION
if mesh_image_provenance_matches mesh-cos-mcp:qnap-v4.1.7 4.1.7-qnap 0123456789abcdef0123456789abcdef01234567; then
  echo 'FAIL stale image revision was accepted' >&2
  exit 1
fi

echo 'PASS QNAP image provenance matching rejects stale version/revision labels'
