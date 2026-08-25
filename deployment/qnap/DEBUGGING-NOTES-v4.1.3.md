# v4.1.3 QNAP Deployment Debugging Record

Status: root cause established from the 2026-08-25 live QNAP console trace.

## Observed failure

The v4.1.2 deployment successfully verified the bundle, extracted it, located Docker, resolved QNAP Compose V2 at `/usr/local/lib/docker/cli-plugins/docker-compose`, and entered `mesh-cos-mcp-prepare.sh`. Preparation then failed on host-side ownership changes:

```text
chown: /share/Docker/cos-mcp/state/ledger: Operation not permitted
chown: /share/Docker/cos-mcp/state/governance: Operation not permitted
chown: /share/Docker/cos-mcp/state/audit: Operation not permitted
chown: /share/Docker/cos-mcp/state/runtime: Operation not permitted
chown: /share/Docker/cos-mcp/state: Operation not permitted
chown: /share/Docker/cos-mcp/secrets: Operation not permitted
```

A separate non-fatal Docker warning showed that Container Station mapped Docker's config home to a QPKG-owned path the SSH user could not read.

## Expected behavior

A normal non-root QNAP SSH operator with Docker access must be able to run the governed deployment without requiring host root or `sudo`, without weakening the container runtime UID 65532 boundary, and without losing canonical state or secrets.

Any failure must leave a durable, timestamped, redaction-safe diagnostic log showing the stage, command classification, return code, script/line when available, operator identity, Docker/Compose identity, filesystem ownership/mode evidence, and bounded container/network diagnostics.

## Root-cause hypothesis and proof

Root cause is the v4.1.2 assumption that Docker authority implies host filesystem ownership authority. The script used host `chown -R 65532:65532` against QNAP shared-folder paths before the release-bound image was built. The live QTS shell permits the operator to use Docker but rejects arbitrary host `chown`, so `set -e` terminates preparation immediately. The successful Docker/Compose discovery immediately before the first `chown` error, and the absence of later image-build/tunnel/ledger messages, bounds the failure to this ownership-preparation step.

The Docker config warning is independent: Docker is functional, but its default config path under the Container Station QPKG home is unreadable to the SSH operator. It should be replaced with an explicit writable deployment-local `DOCKER_CONFIG` to eliminate noisy, misleading warnings.

## Corrective design

1. Build/reuse the release-bound Mesh image before runtime ownership normalization.
2. Never require host `chown` for QNAP shared-folder runtime paths.
3. Apply the minimum ownership/mode changes through a one-shot, network-disabled Docker helper using the already verified release image, root only inside that helper, read-only rootfs, and only `CHOWN`/`FOWNER` capabilities over the explicit state/secrets bind mounts.
4. Validate numeric UID/GID inputs before they enter the helper command.
5. Keep `mesh-cos-mcp` runtime identity at UID/GID 65532 and preserve all existing least-privilege controls.
6. Use Docker-mediated copy/removal for container-created SQLite backup files so the SSH operator does not need direct ownership of runtime state.
7. Set a deployment-local `DOCKER_CONFIG` directory owned by the SSH operator.
8. Add a shared POSIX-shell observability library and use it across prepare, deploy, preflight, verify, and backup.
9. Automatically collect redaction-safe diagnostics on failure. Never dump `.env`, secret contents, process environments, or command arguments containing credentials.

## Regression scenarios

- QNAP-038: non-root operator cannot host-chown runtime directories, but constrained Docker helper applies UID/GID 65532 successfully.
- QNAP-039: deployment failure produces a durable redaction-safe log with stage, script, line/command classification, return code, operator/Docker/Compose facts, and filesystem ownership evidence.
- QNAP-040: deployment uses a writable deployment-local Docker config path and does not depend on the inaccessible Container Station QPKG home.
- QNAP-041: online backup can export and remove a container-created SQLite backup without requiring direct host-user access to the runtime directory.

## Security applicability

TARGETED. The change touches deployment/runtime filesystem authority, persistence, Docker execution, diagnostics/logging, and secret-adjacent paths. Required security properties are: no secret value in logs, no broad privileged container, no Docker socket exposure to the application container, helper network disabled, helper bind mounts limited to state/secrets, helper capabilities limited to ownership/mode operations, runtime UID 65532 unchanged, canonical TaskLedger preserved, and no weakening of MCP authority or network boundaries.
