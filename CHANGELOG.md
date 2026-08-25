# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

## 4.1.0 - 2026-08-25 - QNAP Secure MCP Transport

### Production transport and containerization

- Added MCP SDK Streamable HTTP production transport with `/mcp`, `/healthz`, and `/readyz` while preserving the existing local stdio certification path.
- Packaged the canonical Node/Python MCP runtime in a deterministic non-root Docker image for QNAP Container Station.
- Added the official OpenAI Secure MCP Tunnel client as a least-privilege sidecar on a dedicated private Docker bridge; no public MCP port, router forwarding, UPnP, or QNAP administration exposure is required.
- Fixed the production CoS identity to `MESH_COS_AGENT_ID=cos` and retained canonical registry-derived tool authority.

### Verified QNAP configuration

- Bound the deployment to the 2026-08-25 probe of `mdk-qnap6782xt`: x86_64/linux-amd64, 4 CPU cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, and QNAP `lan7` qnet on `eth1`.
- Set service IP `192.168.7.60`, private subnet `172.30.60.0/29`, application root `/share/Docker/cos-mcp`, and deployment script root `/share/Docker`.
- Set the main container limit to 2 CPUs and 24 GiB RAM with no PID limit; the tunnel sidecar is separately constrained to 0.25 CPU and 256 MiB RAM.
- Added explicit high-utilization storage warning while retaining a 20-GiB absolute free-space preflight threshold.

### Persistence, backup, and recovery

- Production now refuses a missing or in-memory TaskLedger and serializes the Node-to-Python bridge at the single writable SQLite boundary.
- Added SQLite online backup tooling and a QNAP backup wrapper targeting the safely quoted path `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`.
- Added upgrade, rollback, restore, restart, application-recreation, and NAS-reboot acceptance procedures.
- Preserved existing permissions on the operator-managed backup share rather than modifying the share root during application preparation.

### Security and verification

- Added non-root, read-only root filesystem, all-capabilities-dropped, no-new-privileges, no-Docker-socket, no-host-network, bounded request/session/bridge controls, and log rotation.
- Added QNAP BDD scenarios through QNAP-030, including fixed deployment roots, 2-CPU/24-GiB/no-PID resource policy, and safe handling of backup paths containing spaces.
- Extended CI to render Compose, build the production image, test container security/readiness/restart/backup, verify resource controls, and syntax-check QNAP BusyBox-compatible scripts.

### Version boundary

- Repository/QNAP deployment and container-image release: `4.1.0` / tag `v4.1.0`.
- The Phase 1 agent authority/runtime package contract remains `4.0.0` because this release does not alter the 10-agent roster, role authority, or tool allowlists.

## 4.0.0 - 2026-08-21 - Chief of Staff Delegation Contract Remediation

### Breaking topology correction

- Restored the canonical Phase 1 workforce to **10 registered agents**, with Message Operations as the tenth registered agent.
- Preserved **Mesh Devil's Advocate** as the sole external governed shared Skill, available only to Chief of Staff and CRO and never counted as an agent principal.
- Marked the v3.0.0 9-agent topology as historical and superseded for current operation.

### Authority isolation

- Removed stale human-only operations from the Chief of Staff role contract and enforced exact role-contract/MCP allowlist equality in CI.
- Kept `approval.record_decision` and `reliability.human_override` exclusively in the authenticated human-principal catalog.
- Added all-agent negative authorization coverage, positive human-path coverage, and prompt/task identity spoofing regression tests.

### Completion and verification

- Confirmed `task.complete` as the canonical accountable-owner completion operation.
- Hardened completion so a non-empty outcome and supporting evidence are required before `COMPLETED` can be persisted.
- Kept `task.verify` separate and exposed it only to Chief of Staff in the Phase 1 agent catalog.
- Added regression coverage for missing evidence, duplicate completion, unauthorized self-verification, parent/child isolation, and `COMPLETED != VERIFIED`.

### Delegation and end-to-end certification

- Preserved direct-child delegation, non-expanding authority, inherited approval gates, one accountable owner, and depth ceilings.
- Certified `Michael -> CoS -> COO -> Consultant Network Steward` as the legal depth-2 specialist path and denied further Steward delegation.
- Added a synthetic end-to-end scenario spanning CoS, CRO, CFO, COO, Consultant Network Steward, AgentOps, governed Devil's Advocate challenge, owner completion, CoS synthesis/verification, and audit-chain validation.
- Added stale-consultant-readiness and child-failure parent-bypass negative tests.

### Documentation and release engineering

- Reconciled role Skills, Workspace manifests, registry, MCP contract, runtime certification, architecture, lifecycle, decision rights, delegation model, security, testing, runbook, Builder handoff, release notes, and Mermaid diagrams.
- Added stronger roster, role-contract, human-tool, verifier, identity, and documentation drift gates.
- Bumped Python package, MCP package/lock, manifests, and runtime contract to `4.0.0`.
- Preserved the full release suite including 100% branch-aware Python coverage.

### Release identity

- Semantic version: `4.0.0`
- Semantic tag: `v4.0.0`
- Release title: `v4.0.0 Chief of Staff Delegation Contract Remediation`

## 3.0.0 - 2026-08-21 - Shared Mesh Message Operations

Historical release. Reduced the then-current workforce from 10 registered agents to 9 and externalized Mesh Message Operations as a shared approval-bound execution Skill. Preserved human-only approval/reliability operations, TaskLedger canonical state, completion/verification separation, local stdio MCP, TDD/loop engineering, and release gates. This topology is superseded by v4.0.0.

## 2.0.0 - 2026-08-21 - Shared Mesh Devil's Advocate

Removed the repository-local Devil's Advocate principal from the former 11-agent model, resulting in 10 registered agents. Added Mesh Devil's Advocate as an external `EXTERNAL_SHARED_SKILL` for Chief of Staff and CRO with `ADVISORY_ONLY` authority, no canonical-fact mutation, and no external-action authority. Reconciled registry, Workspace manifests, local role Skills, MCP allowlists, certification, documentation, and release metadata.

## 1.1.0 - 2026-08-21 - Local ChatGPT MCP

Moved ChatGPT execution to the bundled `LOCAL_STDIO` MCP path using `node mcp/dist/index.js`, `mesh_cos.mcp_stdio_bridge`, and the canonical Python `MCPRuntime`. Added immutable `MESH_COS_AGENT_ID`, shared `MESH_COS_LEDGER_PATH`, Node build/test/smoke/security certification, and removed the requirement for a remote MCP URL.

## 1.0.0 - 2026-08-17 - Production Readiness

Established the first stable production-readiness release with 100% branch-aware coverage, strict lint/type/schema/security gates, `ProductionPreflight`, serialized `MCPRuntime`, human-only approval/reliability operations, governed `task.complete`, separate `task.verify`, server-owned replay, Workspace Agent package hardening, and release automation.

## 0.2.0 - 2026-08-17 - ChatGPT Workspace Agent packages

Added the initial 11 Workspace Agent/role Skill projection, MCP contract, deny-by-default allowlists, product-level Always Ask controls, approval-read access, remote-safe verification, Builder handoff, and package/runtime drift validation.

## 0.1.4 - 2026-08-17 - Canonical Phase 1 role model

Standardized stable organizational role names and separated role identity from implementation versioning. Expanded CRO, CFO, COO, Consultant Network Steward, CMO, and VP Content capability surfaces within existing authority boundaries.

## 0.1.3 - 2026-08-17 - Explainable decisions and auditable agent governance

Added closed `decision.v2` and `agent-event.v2` contracts, explainable provenance, alternatives, confidence/risk/reversibility, tamper-evident audit-chain records, governance Sheet mirrors, and private-reasoning/secrets prohibitions.

## 0.1.2 - 2026-08-17 - Final Phase 1 requirement closure

Completed task/delegation/conflict/approval/runtime contract alignment, Slack idempotency and thread mapping, AgentOps evidence and recommendations, reliability replay/override, kill-switch enforcement, metrics, dependency checks, drift validation, security scanning, and coverage enforcement.

## 0.1.1 - 2026-08-17 - Phase 1 remediation and documentation alignment

Replaced duplicate hardcoded registry state with canonical loading, added durable consequential records, strengthened delegation/authorization/AgentOps/Slack/reliability/metrics boundaries, and reconciled documentation and Mermaid architecture.

## 0.1.0 - 2026-08-17 - Phase 1 operating core

Added the modular Python CoS control plane, SQLite-backed `TaskLedger`, versioned contracts, the original 11-agent registry, L0-L5 decision rights, task lifecycle, delegation, approval, audit, conflict, AgentOps, Answer Desk, Slack protocol, and kill-switch controls.
