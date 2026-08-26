#!/usr/bin/env bash
set -euo pipefail

VERSION=${1:-4.1.9}
TAG="v${VERSION}"
BUNDLE=${BUNDLE_DIR:-dist/qnap-bundle}
ASSET=${ASSET_PATH:-dist/mesh-cos-mcp-qnap-v${VERSION}.zip}
COMMIT=${GITHUB_SHA:-$(git rev-parse HEAD)}
BUILD_CONTEXT="$BUNDLE/cos-mcp/build-context"

rm -rf "$BUNDLE" "$ASSET" "$ASSET.sha256"
mkdir -p "$BUNDLE/cos-mcp" "$BUILD_CONTEXT/deployment/qnap"

cp deployment/qnap/compose.yaml "$BUNDLE/cos-mcp/compose.yaml"
cp deployment/qnap/.env.example "$BUNDLE/cos-mcp/.env.example"
cp deployment/qnap/README-QNAP.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/DEPLOYMENT-STEPS.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/CHATGPT-ACCEPTANCE.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/install-checklist.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/upgrade-checklist.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/rollback-checklist.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/backup-restore.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/qnap-environment-probe.sh "$BUNDLE/cos-mcp/"
cp deployment/qnap/scripts/*.sh "$BUNDLE/"
cp deployment/qnap-environment.md "$BUNDLE/cos-mcp/"
cp deployment/qnap/DEBUGGING-NOTES-v4.1.3.md "$BUNDLE/cos-mcp/"
cp docs/qnap-production-preflight.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review-v4.1.4.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review-v4.1.5.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review-v4.1.6.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review-v4.1.7.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review-v4.1.8.md "$BUNDLE/cos-mcp/"
cp docs/qnap-security-review-v4.1.9.md "$BUNDLE/cos-mcp/"
cp docs/qnap-deployment-observability-standard.md "$BUNDLE/cos-mcp/"
cp docs/qnap-mcp-502-debugging-v4.1.4.md "$BUNDLE/cos-mcp/"
cp docs/qnap-release-identity-debugging-v4.1.5.md "$BUNDLE/cos-mcp/"
cp docs/qnap-image-provenance-envelope-debugging-v4.1.7.md "$BUNDLE/cos-mcp/"
cp docs/chatgpt-published-app-production-acceptance-v4.1.6.md "$BUNDLE/cos-mcp/"
cp docs/chatgpt-published-app-production-acceptance-v4.1.8.md "$BUNDLE/cos-mcp/"
cp docs/chatgpt-published-app-production-acceptance-v4.1.9.md "$BUNDLE/cos-mcp/"
cp docs/release-4.1.4-qnap-modern-mcp-transport.md "$BUNDLE/cos-mcp/"
cp docs/release-4.1.5-qnap-release-identity.md "$BUNDLE/cos-mcp/"
cp docs/release-4.1.6-secure-mcp-published-app-identity.md "$BUNDLE/cos-mcp/"
cp docs/release-4.1.7-qnap-image-provenance-envelope.md "$BUNDLE/cos-mcp/"
cp docs/release-4.1.8-mcp-contract-acceptance.md "$BUNDLE/cos-mcp/"
cp docs/release-4.1.9-documentation-closeout.md "$BUNDLE/cos-mcp/"
cp specs/qnap-published-chatgpt-app-v4.1.6.feature "$BUNDLE/cos-mcp/"
cp specs/qnap-image-provenance-envelope-v4.1.7.feature "$BUNDLE/cos-mcp/"
cp specs/qnap-mcp-production-acceptance-v4.1.8.feature "$BUNDLE/cos-mcp/"
cp specs/qnap-release-closeout-v4.1.9.feature "$BUNDLE/cos-mcp/"
cp RELEASE.md "$BUNDLE/cos-mcp/"
printf 'tag=%s\nversion=%s\ncommit=%s\n' "$TAG" "$VERSION" "$COMMIT" > "$BUNDLE/cos-mcp/release-metadata.txt"

cp Dockerfile pyproject.toml .dockerignore "$BUILD_CONTEXT/"
cp -R agents chatgpt config contracts src mcp "$BUILD_CONTEXT/"
cp deployment/qnap/runtime_preflight.py "$BUILD_CONTEXT/deployment/qnap/runtime_preflight.py"
cp deployment/qnap/sqlite_backup.py "$BUILD_CONTEXT/deployment/qnap/sqlite_backup.py"
rm -rf "$BUILD_CONTEXT/mcp/node_modules" "$BUILD_CONTEXT/mcp/dist"
find "$BUILD_CONTEXT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$BUILD_CONTEXT" -type f -name '*.pyc' -delete

test ! -e "$BUNDLE/cos-mcp/.env"
test ! -e "$BUNDLE/cos-mcp/secrets"
test -f "$BUILD_CONTEXT/Dockerfile"
test -f "$BUILD_CONTEXT/mcp/package-lock.json"
test -f "$BUILD_CONTEXT/src/mesh_cos/mcp_runtime.py"
test -f "$BUILD_CONTEXT/src/mesh_cos/mcp_validation.py"
test -f "$BUILD_CONTEXT/chatgpt/mcp/tool-input-schemas.v1.json"
test -f "$BUILD_CONTEXT/deployment/qnap/runtime_preflight.py"
test -f "$BUNDLE/mesh-cos-qnap-compose.sh"
test -f "$BUNDLE/mesh-cos-qnap-observability.sh"
test -f "$BUNDLE/mesh-cos-qnap-permissions.sh"
test -f "$BUNDLE/mesh-cos-qnap-image-provenance.sh"
test -f "$BUNDLE/cos-mcp/qnap-security-review-v4.1.9.md"
test -f "$BUNDLE/cos-mcp/release-4.1.9-documentation-closeout.md"
test -f "$BUNDLE/cos-mcp/chatgpt-published-app-production-acceptance-v4.1.9.md"
test -f "$BUNDLE/cos-mcp/qnap-release-closeout-v4.1.9.feature"
test -f "$BUNDLE/cos-mcp/release-metadata.txt"

chmod +x "$BUNDLE"/*.sh "$BUNDLE/cos-mcp/qnap-environment-probe.sh"
mkdir -p "$(dirname "$ASSET")"
(cd "$BUNDLE" && zip -qr "$OLDPWD/$ASSET" .)
ASSET_BASENAME=$(basename "$ASSET")
ASSET_SHA256=$(sha256sum "$ASSET" | awk '{print $1}')
printf '%s  %s\n' "$ASSET_SHA256" "$ASSET_BASENAME" > "$ASSET.sha256"
echo "bundle=$ASSET"
echo "checksum=$ASSET.sha256"
