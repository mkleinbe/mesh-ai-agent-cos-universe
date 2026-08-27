# Verification Receipt v4.1.16

Status: PASS
Subject: QNAP restarting-runtime pre-deploy backup hotfix, QNAP-112 through QNAP-115
Verified implementation/configuration revision: `1c4c6b6e2e01dd9fd00646c753fa9c0b7c05bc7c`
Security applicability: FULL_REVIEW
Security receipt: `docs/security-review-v4.1.16.md` PASS

## Behavior verification

- `specs/qnap-restarting-backup-v4.1.16.feature` is `@ready` and defines QNAP-112 through QNAP-115.
- RED evidence at commit `84a4900a0ec199981dabfe558f44982b2c148c38`, CI run `33080019523`, demonstrates the v4.1.15 defect: `.State.Running=true` while `.State.Status=restarting` selected the unsafe online `docker exec` path.
- Stable running/non-restarting runtime retains the online SQLite backup path.
- Restarting runtime is not given `docker exec`; it is quiesced before canonical SQLite state is read.
- Quiesced backup uses the exact active Mesh image with `--network none`, non-root UID/GID, read-only root filesystem, dropped capabilities, and `no-new-privileges`.
- The helper receives no protected Slack/tunnel credential mount.
- SQLite source is opened read-only, copied through SQLite backup semantics, and integrity-checked.
- Helper/export failure restores prior running intent, removes partial backup state, and fails closed.
- Deployment backs up any existing `mesh-cos-mcp`; only absence of the container skips the existing-runtime pre-deploy backup.

## Engineering evidence

Exact implementation/configuration head `1c4c6b6e2e01dd9fd00646c753fa9c0b7c05bc7c`:

- CI run `33081915546`: PASS.
- v4.1.16 release-candidate run `33081915446`, verify job: PASS.
- Python tests: PASS, 100% coverage.
- TypeScript build/tests and npm security audit: PASS.
- contract/package/document drift checks: PASS.
- Ruff, mypy, Bandit, compileall: PASS.
- QNAP POSIX shell regressions: PASS, including the restarting-container behavioral mock and transactional promotion.
- exact v4.1.16 bundle/checksum: PASS.
- deterministic QNAP Compose topology: PASS.
- production container build and OCI version/revision provenance: PASS.
- modern MCP discovery and sequential requests: PASS.

## Drift review

No unresolved behavior/spec, test/code, security/code, release-version, operator-runbook, or authority-contract drift remains in the verified implementation/configuration revision.

## Residual boundary

Repository verification cannot prove the live QNAP Docker transition or external provider connectivity. Live deployment, Secure MCP Tunnel verification, hosted Mesh CoS MCP acceptance, and provider-authenticated Slack `/mesh-approval` acceptance remain required before production certification.

## Verification decision

PASS for integration and release engineering, subject to a final receipt-only exact-head rerun after this verification receipt and the security receipt are committed.