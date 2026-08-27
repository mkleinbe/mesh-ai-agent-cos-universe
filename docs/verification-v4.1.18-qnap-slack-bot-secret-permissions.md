# Verification: v4.1.18 QNAP Slack Bot Secret Permissions

## Production defect reproduced

v4.1.17 accepted a valid protected `xoxb-` bot OAuth token on the QNAP host, then failed canonical candidate runtime preflight because the runtime user could not read the mounted mode-0400 file. Transactional rollback restored the prior active release.

## Root-cause proof

The v4.1.17 `mesh_apply_secret_permissions` loop omitted `slack-bot-token`. The provisioner runs as root and installs new secret files with mode `0400`, while the production runtime runs as `65532:65532`. The resulting file was therefore present but unreadable to the candidate runtime.

## Required regression evidence

The v4.1.18 candidate is acceptable only when all of the following pass on the exact candidate head:

- QNAP-129 and QNAP-130 behavior specification coverage.
- `deployment/qnap/tests/test-runtime-permissions.sh` proves the permission helper includes `slack-bot-token`.
- QNAP shell syntax and regression suite.
- Python and TypeScript checks.
- Ruff and mypy.
- Full pytest suite with 100% required coverage.
- Bandit security gate.
- Exact `v4.1.18` release bundle with merge-SHA metadata and checksum verification.
- Packaged permission helper contains the `slack-bot-token` normalization path.
- Production image label is `4.1.18-qnap` and revision matches the exact commit.
- Modern MCP transport verification passes.
- Targeted security finding `SEC-4.1.18-001` is closed with no unresolved Critical or High finding.

## Live QNAP acceptance gate

Repository verification does not substitute for production acceptance. After the immutable v4.1.18 release is deployed to the QNAP:

1. Existing valid Slack Socket Mode and bot OAuth credential files are preserved.
2. `slack-bot-token` is normalized to runtime ownership `65532:65532` and mode `0400` without exposing its value.
3. Both `mesh-cos-mcp` and `mesh-cos-tunnel` become healthy.
4. Canonical runtime preflight returns `ok=true`, `slack_hitl_required=true`, and no Slack credential failure.
5. The deployment verifies the secure MCP runtime and preserves the 10-agent / 27-tool contract.
6. Synthetic Slack HITL acceptance proves bot-authored approval, provider-authenticated human decision, immutable fingerprint validation, replay protection, and TaskLedger reconciliation without a consequential real-world action.

Only after these live checks pass may v4.1.18 be called production-accepted.
