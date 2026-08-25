# QNAP Production Preflight

The 2026-08-25 probe establishes linux/amd64, 4 cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, `192.168.7.0/24`, gateway `192.168.7.1`, ext4 storage, and no observed overlap with `172.30.60.0/29`.

## v4.1.4 transport boundary

v4.1.4 replaces the legacy server-managed MCP session lifecycle that caused valid modern `server/discover` requests to fail with `invalid_session`. Production readiness now requires the current MCP discovery path to succeed, not only Python/TaskLedger health.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger semantics, Secure MCP Tunnel source-IP gate, and runtime resource policy are unchanged.

## QNAP filesystem correction retained

The v4.1.2 operator trace proved that QNAP shared-folder ownership cannot be inferred from Docker authority. The v4.1.3 constrained helper design remains in v4.1.4: a short-lived Docker helper performs ownership/mode normalization on only the explicit state or secrets mount, with no network, no Docker socket, read-only root filesystem, validated numeric UID/GID, and a bounded capability set. The long-running application runtime remains UID/GID 65532.

## QNAP Docker operator privilege

The current SSH operator account requires `sudo` for Docker access. The supported operator path invokes the deployment/preflight orchestrator with `sudo`; child Docker/Compose commands inherit that host-side authority. This does not alter the long-running non-root runtime controls.

## Docker client configuration

Deployment initializes `/share/Docker/cos-mcp/.docker-cli` as `DOCKER_CONFIG`. This avoids the inaccessible Container Station QPKG-home Docker config warning captured in the earlier live trace.

## Automated preparation

`mesh-cos-mcp-prepare.sh` resolves Compose V2, initializes durable logging, builds or reuses `mesh-cos-mcp:qnap-v4.1.4`, records its image ID, normalizes runtime state through the constrained helper, preserves or explicitly streams the approved canonical TaskLedger, validates canonical runtime/SQLite integrity as UID 65532, pins the tunnel RepoDigest/image ID, preserves or captures the tunnel runtime key, applies file-only secret ownership/mode, generates non-secret `.env`, and invokes host preflight.

## Host preflight

Preflight validates architecture, CPU/RAM headroom, Docker, Compose V2, qnet shape, `192.168.7.60` ownership/conflict evidence, application/state/backup paths, deployment-local Docker config, canonical ledger owner/mode, actual ledger read/write access from runtime UID/GID 65532, tunnel-secret owner/mode, exact v4.1.4 release identity, image IDs, 2 CPU/24 GiB/no PID limit, free-space threshold, and Compose rendering.

Runtime preflight independently validates amd64, non-root execution, immutable `cos`, tunnel auth mode, system time, no Docker socket, existing readable/writable canonical SQLite ledger, free-space threshold, SQLite integrity, active registry identity, canonical runtime availability, and governance audit-chain integrity.

`/readyz` additionally proves modern MCP discovery serviceability so the service cannot report ready while rejecting the current ChatGPT MCP protocol path.

Any mandatory failure returns nonzero, appends bounded diagnostics to the run log, and prints the diagnostic log path. High filesystem utilization remains an advisory while the absolute free-space gate passes.
