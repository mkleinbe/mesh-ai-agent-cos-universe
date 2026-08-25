# QNAP Production Preflight

The 2026-08-25 probe establishes linux/amd64, 4 cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, `192.168.7.0/24`, gateway `192.168.7.1`, and no observed overlap with `172.30.60.0/29`.

Mandatory host checks before deployment are implemented by `deployment/qnap/scripts/mesh-cos-mcp-preflight.sh`. It validates architecture, CPU/RAM headroom, Docker/Compose, qnet network shape, Docker-side IP conflict, target/backup paths, canonical ledger presence and permissions, tunnel secret ownership/mode, immutable image digests, exact 2-CPU/24-GiB configuration, absence of a configured PID limit, free-space threshold, and Compose rendering.

The application root is `/share/Docker/cos-mcp`; scripts run from `/share/Docker`; backups are written to the quoted path `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"`.

Runtime preflight independently validates amd64, non-root execution, immutable `cos`, tunnel auth mode, system time, no Docker socket, existing readable/writable canonical SQLite ledger, at least 20 GiB free, SQLite integrity, active registry identity, canonical runtime availability, and governance audit-chain integrity.

A mandatory failure is a blocker. The 96% utilization of the primary Docker volume is an operational warning rather than an absolute-space blocker because the probe still showed approximately 1.92 TiB free; the operator must continue monitoring QNAP storage and snapshot headroom.

Live items still requiring operator confirmation are the Container Station application-package version, firewall/access-control posture, non-Docker ownership of `192.168.7.60`, outbound tunnel connectivity, and current backup/snapshot policy.
