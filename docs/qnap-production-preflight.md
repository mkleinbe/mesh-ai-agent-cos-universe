# QNAP Production Preflight

The 2026-08-25 probe establishes linux/amd64, 4 cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, `192.168.7.0/24`, gateway `192.168.7.1`, ext4 storage, and no observed overlap with `172.30.60.0/29`.

## Live permission-boundary correction

The v4.1.2 operator trace proved that a non-root QNAP SSH operator can use Docker while host `chown` to UID/GID 65532 on shared-folder paths returns `Operation not permitted`. v4.1.3 removes host ownership changes from the deployment contract.

A short-lived Docker helper performs runtime ownership/mode normalization on only the explicit state or secrets mount. The helper uses no network, no Docker socket, a read-only root filesystem, validated numeric UID/GID, and a bounded capability set. The long-running application runtime remains UID/GID 65532.

## Docker client configuration

Deployment initializes `/share/Docker/cos-mcp/.docker-cli` as `DOCKER_CONFIG`. This avoids the inaccessible Container Station QPKG-home Docker config warning captured in the live v4.1.2 trace.

## Automated preparation

`mesh-cos-mcp-prepare.sh` resolves Compose V2, initializes durable logging, builds or reuses `mesh-cos-mcp:qnap-v4.1.3`, records its image ID, normalizes runtime state through the constrained helper, preserves or explicitly streams the approved canonical TaskLedger, validates canonical runtime/SQLite integrity as UID 65532, pins the tunnel RepoDigest/image ID, captures the tunnel runtime key with terminal echo disabled, applies file-only secret ownership/mode, generates non-secret `.env`, and invokes host preflight.

## Host preflight

Preflight validates architecture, CPU/RAM headroom, Docker, Compose V2, qnet shape, `192.168.7.60` ownership/conflict evidence, application/state/backup paths, deployment-local Docker config, canonical ledger owner/mode, actual ledger read/write access from runtime UID/GID 65532, tunnel-secret owner/mode, exact v4.1.3 release identity, image IDs, 2 CPU/24 GiB/no PID limit, free-space threshold, and Compose rendering.

It does not require the SSH operator to read/write UID-65532 canonical state.

Runtime preflight independently validates amd64, non-root execution, immutable `cos`, tunnel auth mode, system time, no Docker socket, existing readable/writable canonical SQLite ledger, free-space threshold, SQLite integrity, active registry identity, canonical runtime availability, and governance audit-chain integrity.

Any mandatory failure returns nonzero, appends bounded diagnostics to the run log, and prints the diagnostic log path. High filesystem utilization remains an advisory while the absolute free-space gate passes.
