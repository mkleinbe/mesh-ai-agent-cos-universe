#!/usr/bin/env bash
set -euo pipefail

VERSION=4.4.2
RELEASE_ROOT="dist/qnap-bundle/v${VERSION}"
DOC_ROOT="$RELEASE_ROOT/cos-mcp"
ZIP="dist/mesh-cos-mcp-qnap-v${VERSION}.zip"
CHECKSUM="${ZIP}.sha256"

if [ ! -d "$DOC_ROOT" ]; then
  echo "v4.4.2 QNAP bundle must be built before finalization" >&2
  exit 1
fi

required=(
  CHANGELOG-QNAP-v4.4.2.md
  docs/release-qnap-v4.4.2-slack-hitl-telemetry.md
  docs/security-review-qnap-v4.4.2-slack-hitl-telemetry.md
  docs/verification-qnap-v4.4.2-slack-hitl-telemetry.md
  docs/chatgpt-published-app-production-acceptance-qnap-v4.4.2.md
  specs/slack-hitl-task-telemetry-v4.13.3.feature
)

for source in "${required[@]}"; do
  test -f "$source"
  cp "$source" "$DOC_ROOT/"
done

rm -f "$ZIP" "$CHECKSUM"
(
  cd "$(dirname "$RELEASE_ROOT")"
  zip -qr "../$(basename "$ZIP")" "$(basename "$RELEASE_ROOT")"
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
