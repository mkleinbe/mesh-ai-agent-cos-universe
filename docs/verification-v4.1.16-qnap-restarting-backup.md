# Verification Receipt v4.1.16

Status: PENDING EXACT-CANDIDATE VERIFICATION

## Subject

QNAP restarting-runtime pre-deploy backup hotfix, including QNAP-112 through QNAP-115.

## Required verification

- BDD feature is `@ready` and scenario IDs QNAP-112..QNAP-115 are present.
- RED evidence proves v4.1.15 fails the new acceptance contract for restarting-container backup selection.
- Stable running container retains online SQLite backup behavior.
- Restarting container does not receive `docker exec`; it is quiesced first.
- Quiesced backup helper is network-isolated, non-root, read-only, capability-dropped, and uses the exact active Mesh image.
- Helper failure restores prior running intent, removes partial backup state, and fails closed.
- Deployment backs up any existing `mesh-cos-mcp` container regardless of `.State.Running` value.
- QNAP shell regression suite passes, including `test-restarting-container-backup.sh`.
- Python coverage remains 100%; TypeScript, contract, drift, Ruff, mypy, Bandit, and dependency gates pass.
- Exact v4.1.16 QNAP bundle, checksum, Compose topology, production image provenance, and MCP transport tests pass.
- Security review v4.1.16 is PASS for the exact candidate.

## Residual boundary

Repository verification cannot prove the live QNAP Docker transition or external provider connectivity. Live deployment and hosted acceptance remain required after release publication.
