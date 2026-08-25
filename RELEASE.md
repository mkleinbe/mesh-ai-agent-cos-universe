# v4.1.0 QNAP Secure MCP Transport

`v4.1.0` packages the existing governed Mesh Chief of Staff operating core for persistent QNAP Container Station production use through OpenAI Secure MCP Tunnel. It adds the production remote MCP transport, deterministic container, verified QNAP configuration, deployment automation, backup/restore, security controls, and acceptance evidence without changing Phase 1 role authority.

## Verified target environment

The 2026-08-25 probe of `mdk-qnap6782xt` verified x86_64/linux-amd64, 4 CPU cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, and `lan7` as QNAP `qnet` on `eth1` with subnet `192.168.7.0/24` and gateway `192.168.7.1`.

The production service is assigned `192.168.7.60`. Internal tunnel traffic uses non-overlapping bridge `172.30.60.0/29`.

## Fixed QNAP layout

- Scripts run from `/share/Docker`.
- Application root: `/share/Docker/cos-mcp`.
- Canonical state root: `/share/Docker/cos-mcp/state`.
- Ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`.
- Tunnel runtime secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`.
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`.

The backup path contains spaces and all release scripts pass it as one quoted shell argument.

## Resource policy

`mesh-cos-mcp` is limited to 2 CPUs and 24 GiB RAM with no PID limit. The OpenAI tunnel sidecar is separately limited to 0.25 CPU and 256 MiB RAM with no PID limit.

## Security boundary

The application runs non-root with a read-only application filesystem, all Linux capabilities dropped, no-new-privileges, no Docker socket, no host networking, no broad NAS mounts, and no published MCP host port. `/mcp` accepts only the tunnel sidecar's private address in tunnel mode. The service remains immutably bound to `MESH_COS_AGENT_ID=cos`.

Production refuses to create a missing TaskLedger and serializes Node-to-Python runtime calls at the single SQLite write boundary. Human-only functions remain absent from the CoS catalog and `COMPLETED != VERIFIED` remains enforced by the unchanged 4.0.0 authority/runtime contract.

## Persistence and recovery

SQLite online backup is used rather than copying an actively written database. The release bundle includes prepare, preflight, deploy, verify, and backup scripts plus installation, upgrade, rollback, and restore checklists.

The configured backup target is on the same NAS, so it protects against application/configuration failure but not total NAS loss. QNAP snapshots and an independent second copy remain recommended defense in depth.

## Storage observation

The primary Docker data filesystem was 96% utilized at probe time but retained approximately 1.92 TiB free. The release treats this as an operational capacity warning, not an immediate absolute-capacity blocker. Preflight requires at least 20 GiB free.

## Release quality gates

The candidate must pass Python package integrity, TypeScript build, Node MCP tests, stdio smoke certification, npm audit, schema validation, runtime/document drift validation, Workspace package validation, Ruff, mypy, 100% branch-aware Python coverage, Bandit, compileall, QNAP shell syntax checks, Compose rendering, production image build, container least-privilege assertions, resource-limit assertions, health/readiness, LAN `/mcp` denial, SQLite online-backup integrity, and restart recovery.

## Release assets

The release workflow creates:

- `mesh-cos-mcp-qnap-v4.1.0.zip`, designed to be unpacked into `/share/Docker`;
- `mesh-cos-mcp-qnap-v4.1.0.zip.sha256`.

The bundle contains deployment configuration, runbooks, and operator scripts. It does not contain secrets and does not publish a container image. Build/pull the approved Mesh image separately and record its immutable digest in `.env`.

## Version identity

- Repository/QNAP deployment release: `4.1.0`
- Semantic tag: `v4.1.0`
- Container image label default: `4.1.0-qnap`
- Canonical Phase 1 agent/runtime authority contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 registered agents
- Message Operations remains the tenth registered agent.
- Mesh Devil's Advocate remains the external governed shared Skill, not an agent principal.
- Production connectivity: OpenAI Secure MCP Tunnel
- Local engineering transport: stdio retained

See `docs/release-4.1.0-qnap-secure-mcp.md` and `deployment/qnap/README-QNAP.md` for the detailed deployment and evidence record.
