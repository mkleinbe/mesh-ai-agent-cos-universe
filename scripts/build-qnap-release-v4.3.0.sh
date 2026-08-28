#!/usr/bin/env bash
set -euo pipefail

VERSION=4.3.0
ROOT=$(cd "$(dirname "$0")/.." && pwd -P)
cd "$ROOT"

GITHUB_SHA=${GITHUB_SHA:-$(git rev-parse HEAD)}
export GITHUB_SHA

bash scripts/build-qnap-release-bundle.sh "$VERSION"

RELEASE_DIR="dist/qnap-bundle/v${VERSION}"
APP_DIR="$RELEASE_DIR/cos-mcp"
ZIP="dist/mesh-cos-mcp-qnap-v${VERSION}.zip"

for required in \
  CHANGELOG-v4.3.0.md \
  deployment/qnap/slack-app-manifest.v4.2.3.json \
  specs/cross-agent-owner-execution.feature \
  docs/pf-057-cross-agent-owner-execution.md \
  docs/security-review-v4.3.0-cross-agent-owner-execution.md \
  docs/release-4.3.0-cross-agent-owner-execution.md \
  docs/verification-v4.3.0-cross-agent-owner-execution.md \
  docs/chatgpt-published-app-production-acceptance-v4.3.0.md \
  docs/chatgpt-native-slack-dispatcher-v4.2.3.md; do
  test -f "$required"
done

rm -f \
  "$APP_DIR/slack-app-manifest.v4.1.17.json" \
  "$APP_DIR/slack-app-manifest.v4.2.0.json" \
  "$APP_DIR/slack-app-manifest.v4.2.1.json" \
  "$APP_DIR/slack-app-manifest.v4.2.2.json"
cp CHANGELOG-v4.3.0.md "$APP_DIR/"
cp deployment/qnap/slack-app-manifest.v4.2.3.json "$APP_DIR/"
cp specs/cross-agent-owner-execution.feature "$APP_DIR/"
cp docs/pf-057-cross-agent-owner-execution.md "$APP_DIR/"
cp docs/security-review-v4.3.0-cross-agent-owner-execution.md "$APP_DIR/"
cp docs/release-4.3.0-cross-agent-owner-execution.md "$APP_DIR/"
cp docs/verification-v4.3.0-cross-agent-owner-execution.md "$APP_DIR/"
cp docs/chatgpt-published-app-production-acceptance-v4.3.0.md "$APP_DIR/"
cp docs/chatgpt-native-slack-dispatcher-v4.2.3.md "$APP_DIR/"

grep -q '^version=4.3.0$' "$APP_DIR/release-metadata.txt"
grep -q "^commit=$GITHUB_SHA$" "$APP_DIR/release-metadata.txt"
grep -q '^MESH_COS_DEPLOYMENT_RELEASE=4.3.0$' "$APP_DIR/.env.example"
grep -q '^MESH_COS_IMAGE=mesh-cos-mcp:qnap-v4.3.0$' "$APP_DIR/.env.example"
grep -q 'MESH_COS_SLACK_HITL_MODE: CHATGPT_NATIVE_EVENT_TRIGGER' "$APP_DIR/compose.yaml"
! grep -q 'MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE:' "$APP_DIR/compose.yaml"
! grep -q 'slack_socket_app_token' "$APP_DIR/compose.yaml"
! grep -q '/mesh-approval Socket Mode ingress' "$RELEASE_DIR/mesh-cos-mcp-deploy.sh"
grep -q 'MESH_COS_SLACK_APP_ID=A0B49RNE4K0' "$APP_DIR/.env.example"
grep -q 'delegation.execute_owner' "$APP_DIR/build-context/chatgpt/mcp/mesh-cos-mcp.v1.json"
grep -q 'delegation.execute_owner' "$APP_DIR/cross-agent-owner-execution.feature"
grep -q 'OWNER_EXECUTION_READINESS=PASS' "$APP_DIR/build-context/scripts/check-owner-execution-readiness.py"
test -f "$APP_DIR/CHANGELOG-v4.3.0.md"
test -f "$APP_DIR/slack-app-manifest.v4.2.3.json"
test -f "$APP_DIR/cross-agent-owner-execution.feature"
test -f "$APP_DIR/security-review-v4.3.0-cross-agent-owner-execution.md"
test -f "$APP_DIR/verification-v4.3.0-cross-agent-owner-execution.md"

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

unzip -Z1 "$ZIP" > /tmp/mesh-cos-v430.entries
if grep -Ev '^v4\.3\.0/' /tmp/mesh-cos-v430.entries; then
  echo 'ERROR: v4.3.0 archive contains entries outside the immutable release root' >&2
  exit 1
fi
grep -qx 'v4.3.0/cos-mcp/CHANGELOG-v4.3.0.md' /tmp/mesh-cos-v430.entries
grep -qx 'v4.3.0/cos-mcp/slack-app-manifest.v4.2.3.json' /tmp/mesh-cos-v430.entries
grep -qx 'v4.3.0/cos-mcp/cross-agent-owner-execution.feature' /tmp/mesh-cos-v430.entries
grep -qx 'v4.3.0/cos-mcp/security-review-v4.3.0-cross-agent-owner-execution.md' /tmp/mesh-cos-v430.entries
grep -qx 'v4.3.0/cos-mcp/release-4.3.0-cross-agent-owner-execution.md' /tmp/mesh-cos-v430.entries
grep -qx 'v4.3.0/cos-mcp/verification-v4.3.0-cross-agent-owner-execution.md' /tmp/mesh-cos-v430.entries
grep -qx 'v4.3.0/cos-mcp/chatgpt-published-app-production-acceptance-v4.3.0.md' /tmp/mesh-cos-v430.entries

echo "v4.3.0 QNAP release bundle packaged from $GITHUB_SHA"
