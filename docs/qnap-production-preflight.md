# QNAP Production Preflight

The 2026-08-25 probe establishes linux/amd64, 4 cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, `192.168.7.0/24`, gateway `192.168.7.1`, ext4 storage, and no observed overlap with `172.30.60.0/29`.

## v4.1.2 QNAP CLI correction

A live operator run showed that the installed Compose V2 package was not callable as `docker compose` from that SSH session. v4.1.2 treats package presence and CLI resolution as separate facts. `mesh-cos-qnap-compose.sh` first tests `docker compose`, then discovers the executable Compose V2 plugin through Docker client plugin metadata, standard Docker plugin locations, and the Container Station QPKG install path. Compose V1 is rejected.

The environment probe now records the Container Station install path, Docker-reported Compose plugin path, and executable Compose candidates so future QNAP upgrades can be diagnosed without inferring PATH behavior.

## Automated preparation

`mesh-cos-mcp-prepare.sh` creates the approved state/secrets tree, builds or reuses `mesh-cos-mcp:qnap-v4.1.2`, records its image ID, pins the tunnel RepoDigest/image ID, preserves or explicitly stages the canonical TaskLedger, runs canonical runtime/SQLite integrity preflight, captures the tunnel runtime key with terminal echo disabled, and generates the non-secret `.env`.

## Host preflight

`mesh-cos-mcp-preflight.sh` validates architecture, CPU/RAM headroom, Docker, resolvable Compose V2, qnet network shape, Docker-side ownership of `192.168.7.60`, target/backup paths, canonical ledger permissions, tunnel-secret ownership/mode, exact release identity, image identities, exact 2-CPU/24-GiB configuration, absence of a PID limit, at least 20 GiB free, and Compose rendering.

The application root is `/share/Docker/cos-mcp`; scripts run from `/share/Docker`; backups are written to the quoted path `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"`.

Runtime preflight independently validates amd64, non-root execution, immutable `cos`, tunnel auth mode, system time, no Docker socket, existing readable/writable canonical SQLite ledger, free-space threshold, SQLite integrity, active registry identity, canonical runtime availability, and governance audit-chain integrity.

A mandatory failure blocks deployment. The primary Docker volume utilization warning remains advisory while the absolute free-space gate passes.
