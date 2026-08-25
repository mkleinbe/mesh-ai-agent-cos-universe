# QNAP Production Preflight

The 2026-08-25 probe establishes linux/amd64, 4 cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, `192.168.7.0/24`, gateway `192.168.7.1`, ext4 storage, and no observed overlap with `172.30.60.0/29`.

## v4.1.1 automated preparation

`mesh-cos-mcp-prepare.sh` now performs all deterministic preparation before host preflight:

- creates the approved `/share/Docker/cos-mcp` state/secrets tree without changing backup-share root permissions;
- builds or reuses the release-bound `mesh-cos-mcp:qnap-v4.1.1` local image and records its Docker content-addressed image ID;
- reuses a previously pinned tunnel RepoDigest when present or pulls the exact versioned OpenAI tunnel-client source and resolves its immutable RepoDigest/image ID;
- preserves an existing canonical ledger, or stages an explicitly selected existing TaskLedger source only when the target is absent;
- validates the staged/existing ledger through canonical runtime preflight before deployment;
- captures the runtime API key with terminal echo disabled and writes only the approved 0400 secret file;
- generates the non-secret `.env` including prepared image identities and fixed resource/path values.

## Host preflight

`mesh-cos-mcp-preflight.sh` validates architecture, CPU/RAM headroom, Docker/Compose, qnet network shape, current Docker-side ownership of `192.168.7.60`, LAN conflict evidence where observable, target/backup paths, canonical ledger presence and permissions, tunnel secret ownership/mode, exact release identity, Mesh local-tag to recorded-image-ID equality, tunnel RepoDigest to image-ID equality, exact 2-CPU/24-GiB configuration, absence of a configured PID limit, at least 20 GiB free, and Compose rendering.

The application root is `/share/Docker/cos-mcp`; scripts run from `/share/Docker`; backups are written to the quoted path `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"`.

Runtime preflight independently validates amd64, non-root execution, immutable `cos`, tunnel auth mode, system time, no Docker socket, existing readable/writable canonical SQLite ledger, free-space threshold, SQLite integrity, active registry identity, canonical runtime availability, and governance audit-chain integrity.

A mandatory failure blocks deployment. The 96% utilization observed on the primary Docker volume remains an operational warning rather than an absolute-space blocker because the probe showed approximately 1.92 TiB free; the operator should continue monitoring storage and snapshot headroom.

`mesh-cos-mcp-deploy.sh` invokes preparation and preflight automatically, waits for both containers to become healthy, runs post-deploy verification, and creates a post-deploy backup. Running preflight separately is useful for diagnosis but is not required in the normal v4.1.1 operator path.
