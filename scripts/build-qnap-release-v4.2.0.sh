#!/usr/bin/env bash
set -euo pipefail

VERSION=4.2.0
ROOT=$(cd "$(dirname "$0")/.." && pwd -P)
cd "$ROOT"

GITHUB_SHA=${GITHUB_SHA:-$(git rev-parse HEAD)}
export GITHUB_SHA

bash scripts/build-qnap-release-bundle.sh "$VERSION"

RELEASE_DIR="dist/qnap-bundle/v${VERSION}"
APP_DIR="$RELEASE_DIR/cos-mcp"
ZIP="dist/mesh-cos-mcp-qnap-v${VERSION}.zip"

for required in \
  deployment/qnap/slack-app-manifest.v4.2.0.json \
  specs/native-slack-event-hitl-v4.2.0.feature \
  docs/security-review-v4.2.0.md \
  docs/release-4.2.0-native-slack-event-hitl.md \
  docs/chatgpt-native-slack-dispatcher-v4.2.0.md \
  docs/chatgpt-published-app-production-acceptance-v4.2.0.md; do
  test -f "$required"
done

rm -f "$APP_DIR/slack-app-manifest.v4.1.17.json"
cp deployment/qnap/slack-app-manifest.v4.2.0.json "$APP_DIR/"
cp specs/native-slack-event-hitl-v4.2.0.feature "$APP_DIR/"
cp docs/security-review-v4.2.0.md "$APP_DIR/"
cp docs/release-4.2.0-native-slack-event-hitl.md "$APP_DIR/"
cp docs/chatgpt-native-slack-dispatcher-v4.2.0.md "$APP_DIR/"
cp docs/chatgpt-published-app-production-acceptance-v4.2.0.md "$APP_DIR/"
if [ -f docs/verification-v4.2.0-native-slack-event-hitl.md ]; then
  cp docs/verification-v4.2.0-native-slack-event-hitl.md "$APP_DIR/"
fi

grep -q '^version=4.2.0$' "$APP_DIR/release-metadata.txt"
grep -q "^commit=$GITHUB_SHA$" "$APP_DIR/release-metadata.txt"
grep -q 'MESH_COS_SLACK_HITL_MODE: CHATGPT_NATIVE_EVENT_TRIGGER' "$APP_DIR/compose.yaml"
! grep -q 'MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE:' "$APP_DIR/compose.yaml"
! grep -q 'slack_socket_app_token' "$APP_DIR/compose.yaml"
test -f "$APP_DIR/slack-app-manifest.v4.2.0.json"
test ! -f "$APP_DIR/slack-app-manifest.v4.1.17.json"

rm -f "$ZIP" "$ZIP.sha256"
(
  cd dist/qnap-bundle
  zip -rq "../mesh-cos-mcp-qnap-v${VERSION}.zip" "v${VERSION}"
)
(
  cd dist
  sha256sum "mesh-cos-mcp-qnap-v${VERSION}.zip" > "mesh-cos-mcp-qnap-v${VERSION}.zip.sha256"
  sha256sum -c "mesh-cos-mcp-qnap-v${VERSION}.zip.sha256"
)

unzip -Z1 "$ZIP" > /tmp/mesh-cos-v420.entries
if grep -Ev '^v4\.2\.0/' /tmp/mesh-cos-v420.entries; then
  echo 'ERROR: v4.2.0 archive contains entries outside the immutable release root' >&2
  exit 1
fi
grep -qx 'v4.2.0/cos-mcp/slack-app-manifest.v4.2.0.json' /tmp/mesh-cos-v420.entries
grep -qx 'v4.2.0/cos-mcp/native-slack-event-hitl-v4.2.0.feature' /tmp/mesh-cos-v420.entries
grep -qx 'v4.2.0/cos-mcp/security-review-v4.2.0.md' /tmp/mesh-cos-v420.entries
grep -qx 'v4.2.0/cos-mcp/release-4.2.0-native-slack-event-hitl.md' /tmp/mesh-cos-v420.entries
grep -qx 'v4.2.0/cos-mcp/chatgpt-native-slack-dispatcher-v4.2.0.md' /tmp/mesh-cos-v420.entries
grep -qx 'v4.2.0/cos-mcp/chatgpt-published-app-production-acceptance-v4.2.0.md' /tmp/mesh-cos-v420.entries

echo "v4.2.0 QNAP release bundle packaged from $GITHUB_SHA"
