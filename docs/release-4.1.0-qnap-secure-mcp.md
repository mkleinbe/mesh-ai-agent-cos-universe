# v4.1.0 QNAP Secure MCP Transport Verification Record

## Scope

This release adds persistent QNAP Container Station production infrastructure for `mesh-cos-mcp` without changing the Phase 1 business-authority contract.

## QNAP evidence

Probe date: 2026-08-25. Target: `mdk-qnap6782xt`, QTS TS-X72 family, linux/amd64, 4 CPU cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2. Primary network path is `eth1` through `qvs0`; the external container network `lan7` uses QNAP `qnet` on `192.168.7.0/24` with gateway `192.168.7.1`.

Existing probed private networks occupy 172.29.0.0/20 in three /22 blocks plus QNAP 10.0.x bridge networks. `172.30.60.0/29` is non-overlapping at the captured point in time.

Primary Docker storage is ext4 and retained approximately 1.92 TiB free while 96% utilized. This remains an operational warning.

## Implemented topology

- `mesh-cos-mcp`: private `172.30.60.2`; LAN `192.168.7.60`; 2 CPUs; 24 GiB RAM; no PID limit.
- `mesh-cos-tunnel`: private `172.30.60.3`; 0.25 CPU; 256 MiB RAM; no PID limit.
- No published host ports.
- `/mcp` reserved to the tunnel-sidecar private source address.
- Canonical state bind-mounted from `/share/Docker/cos-mcp/state`.
- Scripts execute from `/share/Docker`.
- Backups target the safely quoted `/share/QNAP NAS/Mike Home/MCP/CoS/Backups` path.

## Security review receipt

Applicability: FULL_REVIEW.

Trust boundaries reviewed: ChatGPT to OpenAI tunnel; tunnel to MCP private bridge; MCP transport to immutable CoS identity; Node to Python bridge; Python runtime to TaskLedger; container to QNAP filesystem; operator scripts to QNAP shared folders; backup copies to operator-managed storage.

Controls include non-root runtime, read-only rootfs, all capabilities dropped, no-new-privileges, no Docker socket, no host network, no arbitrary replay execution, immutable identity, canonical allowlists, bounded payload/session/bridge behavior, secret-file mount, sanitized structured logging, single writable SQLite boundary, existing-ledger requirement, online backup, and fail-closed readiness/preflight.

The preparation script intentionally preserves permissions on the operator-managed backup root. It only validates writability and manages permissions under `/share/Docker/cos-mcp`.

## Remaining live acceptance

Repository verification cannot certify actual QNAP Container Station deployment, non-Docker ownership of `192.168.7.60`, current firewall policy, tunnel runtime connectivity, QNAP reboot recovery, or ChatGPT end-to-end governed writes until the operator deploys the release bundle. Those are deployment acceptance checks, not hidden code PASS claims.

## Release decision

The human owner explicitly authorized commit, push, merge, semantic tag, and release creation for this candidate. Production activation on QNAP remains a separate operator action performed from the release bundle.
