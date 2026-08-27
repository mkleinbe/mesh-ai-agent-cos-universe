# Security Review v4.1.16

Status: PASS
Applicability: FULL_REVIEW
Subject: QNAP restarting-runtime pre-deploy backup hotfix
Reviewed implementation/configuration revision: `1c4c6b6e2e01dd9fd00646c753fa9c0b7c05bc7c`

## Security properties verified

1. Canonical TaskLedger integrity is preserved; the hotfix does not bypass or raw-copy the live database.
2. A restarting container is not treated as a stable `docker exec` target merely because Docker reports `.State.Running=true`.
3. The fallback path quiesces a restarting writer before canonical SQLite state is read.
4. The one-shot helper uses the exact active Mesh image ID, `--network none`, runtime UID/GID, read-only root filesystem, all capabilities dropped, and `no-new-privileges`.
5. The helper receives the canonical state mount required to materialize the temporary SQLite backup and receives no protected Slack or tunnel credential mount.
6. `sqlite_backup.py` opens the source read-only, uses SQLite backup semantics, and requires `PRAGMA integrity_check=ok` before export.
7. Helper/export failure removes temporary and partial backup artifacts and returns failure.
8. Prior running intent is restored after both successful and failed quiesced backup attempts.
9. Deployment invokes the backup gate for any existing `mesh-cos-mcp`; only an absent container skips existing-runtime backup.
10. v4.1.15 authentication, approval, network-ingress, secret, and transactional-promotion controls remain unchanged.

## Trust boundaries reviewed

- QNAP root deployment process -> Docker daemon
- Docker daemon -> exact active Mesh image
- one-shot helper -> canonical TaskLedger state mount
- canonical state -> governed backup root
- deployment backup gate -> candidate preparation
- connected Slack collaboration -> non-authoritative collaboration only
- provider-authenticated Socket Mode -> canonical human approval ingress

## Evidence

- RED characterization: commit `84a4900a0ec199981dabfe558f44982b2c148c38`, CI run `33080019523`, where the new QNAP-112..QNAP-115 contract failed against the v4.1.15 backup selection behavior.
- Exact implementation/configuration CI: run `33081915546` PASS.
- Exact v4.1.16 release-candidate verification: run `33081915446`, verify job PASS.
- Python test suite: PASS at 100% coverage.
- TypeScript build/tests and npm high-severity audit: PASS.
- Contract, runtime-documentation, and ChatGPT package drift checks: PASS.
- Ruff, mypy, Bandit, compileall: PASS.
- QNAP POSIX regression suite: PASS, including `test-restarting-container-backup.sh` and transactional-promotion tests.
- Exact v4.1.16 bundle/checksum construction: PASS.
- QNAP Compose topology validation: PASS.
- Production container OCI version/revision provenance: PASS.
- Modern MCP discovery and sequential requests: PASS.

## Findings

No open CRITICAL or HIGH security finding was identified in the reviewed v4.1.16 candidate. No authority widening, new credential dependency, direct MCP ingress, secret exposure, or fallback-to-ordinary-Slack approval path was introduced.

## Residual boundary

Repository security verification does not prove the live QNAP state transition, Secure MCP Tunnel route, Slack provider availability, or a real provider-authenticated `/mesh-approval` interaction. Those remain mandatory live production-acceptance checks after deployment.

## Release decision

PASS for release engineering, subject to one final receipt-only exact-head CI/release-candidate verification after this evidence record is committed. Live production certification remains separate.