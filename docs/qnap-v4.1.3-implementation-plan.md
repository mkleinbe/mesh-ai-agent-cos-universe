# v4.1.3 QNAP Deployment Reliability Plan

## Goal and governing requirements

Repair the live v4.1.2 QNAP deployment failure without weakening the established Mesh CoS runtime, canonical TaskLedger boundary, Secure MCP Tunnel boundary, non-root runtime identity, or human approval model.

The deployment must:

1. run from a normal non-root QNAP SSH operator that already has Docker/Container Station access;
2. never require host `sudo`, host root, or host-side `chown` to arbitrary UID/GID values;
3. keep the application runtime at UID/GID `65532:65532`;
4. preserve the existing canonical TaskLedger and never silently replace it;
5. preserve tunnel-secret file-only handling and never log secret values;
6. produce durable, timestamped, redaction-safe diagnostics for every deployment/update failure;
7. preserve the existing QNAP network, image, CPU, RAM, no-PID-limit, least-privilege, and Secure MCP Tunnel controls;
8. make each stage and command failure observable with stage, command classification, return code, script, line when available, identity, and bounded environment evidence;
9. preserve the operator SSH session on failure.

## Ready behavior-spec baseline

`specs/qnap-deployment-remediation-v4.1.3.feature` defines the new ready scenarios:

- QNAP-038: non-root operator ownership handoff through a constrained Docker helper;
- QNAP-039: durable redaction-safe deployment diagnostics;
- QNAP-040: deployment-local Docker CLI configuration instead of the inaccessible Container Station QPKG home;
- QNAP-041: Docker-mediated SQLite backup export so the host operator does not need canonical-state file ownership.

Affected existing scenarios that must remain green: QNAP-003, QNAP-004, QNAP-005, QNAP-016, QNAP-021 through QNAP-035, QNAP-036, and QNAP-037.

## Security applicability

Security profile: `TARGETED`.

Sensitive surfaces:

- QNAP shared-folder filesystem authority;
- Docker process execution and capability boundaries;
- canonical TaskLedger persistence;
- tunnel-secret storage;
- deployment logs and diagnostics;
- release bundle and deployment runtime.

Required security properties:

- no secret values, `.env` contents, process environments, or credential-bearing argv in diagnostics;
- helper container is never privileged, has no Docker socket, uses `--network none`, read-only rootfs, and only the minimum capabilities needed for ownership/mode changes;
- runtime container remains UID/GID 65532 with all existing capability and namespace restrictions;
- canonical state bind mount is the only state path visible to the ownership helper;
- secret helper is limited to the secrets bind mount and never emits secret contents;
- ledger staging streams an operator-readable source through stdin to a UID-65532 container and does not place canonical data in shell arguments;
- no change to MCP tool authority, human-only operations, tunnel ingress, or agent roster.

## Repository baseline

Baseline release: v4.1.2 at merge commit `b4f121ddaddc8b0410c2418d4bce204369a959d8`.

Remediation branch: `fix/qnap-permissions-observability-v4.1.3`.

## File and interface map

### New shared shell interfaces

- `deployment/qnap/scripts/mesh-cos-qnap-observability.sh`: structured timestamped logging, shared run ID, streaming return-code preservation, deployment-local Docker config, bounded diagnostics, and retention.
- `deployment/qnap/scripts/mesh-cos-qnap-permissions.sh`: numeric identity validation, constrained state ownership, stdin-based ledger staging, and constrained secret ownership.

### Modified operator scripts

- `mesh-cos-mcp-deploy.sh`: stage orchestration, signal/failure diagnostics, shared log receipt.
- `mesh-cos-mcp-prepare.sh`: build before ownership normalization, no host chown, runtime-mediated ledger and secret preparation.
- `mesh-cos-mcp-preflight.sh`: validate runtime UID access rather than SSH-user access.
- `mesh-cos-mcp-backup.sh`: Docker-mediated export/remove of runtime-created SQLite backups.
- `mesh-cos-mcp-verify.sh`: shared instrumentation and failure diagnostics.

## Dependency and implementation order

1. Characterize live failure and freeze root-cause record.
2. Add observability library and unit regression.
3. Add constrained permission helper and unit regression.
4. Refactor prepare around build-before-permission-handoff and runtime-mediated state handling.
5. Refactor preflight and backup to remove SSH-user state-ownership assumptions.
6. Apply observability to deploy and verify.
7. Add BDD and Python evaluation coverage.
8. Add actual-container CI integration evidence.
9. Run targeted security review.
10. Run independent verification on the exact branch head and release bundle.
11. Open PR, inspect diff, merge only after gates pass, then bind v4.1.3 tag/assets to the verified main commit.

## TDD / evidence matrix

| Unit | RED / characterization | GREEN evidence | VERIFY evidence |
|---|---|---|---|
| QNAP ownership | Live `chown ... Operation not permitted` trace | permission helper mock test + no host `chown` assertion | actual Docker helper changes bind-mount state to 65532 in CI |
| Runtime ledger access | v4.1.2 host `[ -r ]/[ -w ]` contract is incompatible with UID-65532 state ownership | preflight validates owner/mode and runtime container access | runtime preflight and readiness against actual state |
| Backup export | host `cp` of UID-65532 runtime file is an ownership mismatch | backup uses `docker cp` + in-container cleanup | SQLite integrity + SHA-256 backup checks |
| Diagnostics | v4.1.2 only emits unstructured console errors | structured log test preserves rc=7 and captures command output | CI checks durable log receipt and secret non-collection |
| Docker config | live QPKG config permission warning | deployment-local `DOCKER_CONFIG` | shell regression + normal Docker/Compose/image CI |

## Recovery and release considerations

A failed v4.1.2 attempt shown in the live trace did not reach image build, ledger staging, secret capture, or service creation. Runtime state and secrets are never deleted as part of remediation. Every failure prints `DIAGNOSTIC_LOG=<path>` and leaves the SSH session active. Logs default to `/share/Docker/cos-mcp/logs/deployment` with bounded retention and mode 0640. Release requires fresh branch CI, exact-diff review, targeted security evidence, post-merge CI, release workflow success, artifact checksum validation, and live QNAP acceptance by the operator.
