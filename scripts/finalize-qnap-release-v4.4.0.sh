#!/usr/bin/env bash
set -euo pipefail

VERSION=4.4.0
RELEASE_ROOT="dist/qnap-bundle/v${VERSION}"
DOC_ROOT="$RELEASE_ROOT/cos-mcp"
ZIP="dist/mesh-cos-mcp-qnap-v${VERSION}.zip"
CHECKSUM="${ZIP}.sha256"

if [ ! -d "$DOC_ROOT" ]; then
  echo "v4.4.0 QNAP bundle must be built before finalization" >&2
  exit 1
fi

required=(
  CHANGELOG-v4.4.0.md
  docs/material-turn-v4.4.0.md
  docs/architecture-v4.4.0-authority-execution.md
  docs/security-review-v4.4.0-authority-closure.md
  docs/runbook-v4.4.0-authority-execution.md
  docs/release-v4.4.0-authority-closure.md
  docs/chatgpt-published-app-production-acceptance-v4.4.0.md
  docs/skills-v4.4.0.md
)

for source in "${required[@]}"; do
  test -f "$source"
  cp "$source" "$DOC_ROOT/"
done

if [ -f docs/verification-v4.4.0-authority-closure.md ]; then
  cp docs/verification-v4.4.0-authority-closure.md "$DOC_ROOT/"
fi

rm -f "$ZIP" "$CHECKSUM"
(
  cd "$(dirname "$RELEASE_ROOT")"
  zip -qr "../../$(basename "$ZIP")" "$(basename "$RELEASE_ROOT")"
)
(
  cd dist
  sha256sum "$(basename "$ZIP")" > "$(basename "$CHECKSUM")"
)

for source in "${required[@]}"; do
  test -f "$DOC_ROOT/$(basename "$source")"
done

echo "finalized_bundle=$ZIP"
echo "checksum=$CHECKSUM"
