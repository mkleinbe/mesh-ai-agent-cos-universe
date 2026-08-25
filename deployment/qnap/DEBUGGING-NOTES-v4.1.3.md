# v4.1.3 QNAP Deployment Debugging Record

Status: root cause established from the 2026-08-25 live QNAP console trace.

## Observed failure

v4.1.2 successfully verified the release checksum, extracted the bundle, resolved Docker, resolved Compose V2 at `/usr/local/lib/docker/cli-plugins/docker-compose`, and entered preparation. It then failed on host ownership changes with `Operation not permitted` for the canonical state directories and secrets directory.

The same trace showed a non-fatal Docker warning because Container Station mapped Docker's default config home to a QPKG path the SSH operator could not read.

## Expected behavior

A normal non-root QNAP SSH operator with Docker access must be able to run governed deployment without host root or `sudo`, without weakening runtime UID/GID 65532, and without losing canonical state or secrets. Failure must leave durable, redaction-safe evidence describing stage, safe command classification, return code, script/line when available, platform identity, Docker/Compose identity, filesystem ownership/mode, and bounded container state.

## Root cause

**Root cause is the v4.1.2 assumption that Docker authority implies host filesystem ownership authority.** The live evidence predicts and demonstrates the failure: Docker and Compose operations succeed, then the first host `chown -R 65532:65532` operations fail before image build, tunnel setup, ledger staging, secret capture, or service creation.

Four coupled defects were identified:

1. host-side `chown` to runtime UID/GID is not a valid QNAP operator contract;
2. host preflight later checked ledger read/write as the SSH user instead of runtime UID/GID 65532;
3. backup later copied a UID-65532-created SQLite file directly as the SSH user;
4. Docker defaulted to an inaccessible Container Station QPKG config path.

Fixing only the visible `chown` would have moved the failure downstream.

## Corrective design

- Build/reuse the release-bound Mesh image before ownership normalization.
- Never require host `chown` for canonical runtime paths.
- Normalize state ownership with a one-shot Docker helper using root only inside the helper, `--network none`, read-only rootfs, no Docker socket, `--cap-drop ALL`, then `CHOWN`, `FOWNER`, and `DAC_OVERRIDE` only, over the explicit state bind mount.
- Apply the same bounded ownership helper to the secret file only after hidden capture; the helper sees only the secrets bind mount.
- Validate numeric UID/GID inputs before helper execution.
- Stage an approved missing ledger by streaming the source through stdin to a UID/GID-65532 container, then atomically install it.
- Validate canonical-state access from runtime UID/GID 65532 rather than the SSH user.
- Export online SQLite backups with `docker cp` and remove the temporary file through `docker exec`.
- Set deployment-local `DOCKER_CONFIG=/share/Docker/cos-mcp/.docker-cli`.
- Share a timestamped structured log across deploy, prepare, preflight, verify, and backup.
- Collect bounded diagnostics automatically on failure while excluding secret contents, `.env`, process environments, credential-bearing argv, and tunnel logs.

## Regression scenarios

- QNAP-038: non-root host ownership handoff through constrained Docker helper.
- QNAP-039: durable redaction-safe diagnostics and log receipt on failure.
- QNAP-040: deployment-local Docker config removes dependency on inaccessible QPKG home.
- QNAP-041: Docker-mediated online backup export avoids host ownership dependency.

## Security applicability

TARGETED because the remediation touches Docker execution, filesystem authority, persistence, secrets, diagnostics, and deployment runtime. The fix does not change MCP authority, agent identity, tool catalogs, network ingress, or the canonical-state semantic contract.
