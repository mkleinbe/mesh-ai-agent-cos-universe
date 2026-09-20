#!/bin/sh
set -eu

ROOT=$(CDPATH= cd "$(dirname "$0")/../../.." 2>/dev/null && pwd -P) || exit 1
PREPARE="$ROOT/deployment/qnap/scripts/mesh-cos-mcp-prepare.sh"
DEPLOY="$ROOT/deployment/qnap/scripts/mesh-cos-mcp-deploy.sh"
VERIFY="$ROOT/deployment/qnap/scripts/mesh-cos-mcp-verify.sh"
TUNNEL_PROVISION="$ROOT/deployment/qnap/scripts/mesh-cos-tunnel-key-provision.sh"

grep -Fq 'EXPECTED_COMMIT_SHORT=$(printf' "$PREPARE" || { echo 'FAIL prepare does not derive commit-qualified image identity' >&2; exit 1; }
grep -Fq 'mesh-cos-mcp:qnap-v${RELEASE_VERSION}-${EXPECTED_COMMIT_SHORT}' "$PREPARE" || { echo 'FAIL prepare image tag is not commit-qualified' >&2; exit 1; }
grep -Fq -- '--force-recreate' "$DEPLOY" || { echo 'FAIL deploy does not force candidate recreation' >&2; exit 1; }
grep -Fq 'EXPECTED_SOURCE_COMMIT=' "$VERIFY" || { echo 'FAIL verifier does not bind active release source commit' >&2; exit 1; }
grep -Fq 'envelope.source_commit!==expectedCommit' "$VERIFY" || { echo 'FAIL governed MCP envelope source commit is not verified' >&2; exit 1; }
grep -Fq 'RUNNING_MESH_REVISION' "$VERIFY" || { echo 'FAIL running image OCI revision is not verified' >&2; exit 1; }
grep -Fq 'mesh-cos-mcp:qnap-v${EXPECTED_RELEASE}-${EXPECTED_COMMIT_SHORT}' "$TUNNEL_PROVISION" || { echo 'FAIL tunnel provisioner does not resolve commit-qualified image identity' >&2; exit 1; }

echo 'PASS QNAP deployment binds archive metadata, image identity, running container, and MCP source commit'
