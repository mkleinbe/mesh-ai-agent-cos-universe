# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

## 4.1.5 - 2026-08-25 - QNAP Release Identity Preflight Reliability

### Live QNAP causal remediation

- Reproduced the v4.1.4 upgrade failure at the host-preflight release-identity gate: the v4.1.4 image built successfully and surrounding checks passed, but preflight still required `MESH_COS_DEPLOYMENT_RELEASE=4.1.3`.
- Confirmed the later `prepare failed` messages were propagation of that one stale release check, not independent Docker, TaskLedger, tunnel, resource, or MCP transport failures.
- Confirmed the failed upgrade stopped safely before Compose replacement, leaving the existing v4.1.3 application and tunnel healthy.

### TDD and release engineering

- Added regression RED proving preflight did not derive release identity from bundle metadata and still contained the stale v4.1.3 literal.
- Replaced the duplicated patch-release gate with comparison against the verified bundle's `release-metadata.txt` `version=` value.
- Added fail-closed handling for missing release metadata, missing version, and bundle/environment release mismatch.
- Added ready QNAP-048 through QNAP-050 behavior scenarios and CI inspection of the actual v4.1.5 release bundle for release-metadata correctness and stale-literal absence.
- Advanced QNAP bundle, image label, generated environment, workflow, deployment runbooks, acceptance procedures, and release assets to `4.1.5` / `v4.1.5`.

### Security and authority boundary

- Classified the deployment/runtime validation correction TARGETED and documented SEC-QNAP-024 through SEC-QNAP-026.
- Release metadata is parsed as data and is never sourced, evaluated, or used to expand Docker/MCP authority.
- Canonical Phase 1 authority/runtime contract remains `4.0.0`; exactly 10 agents, 27 governed CoS tools, human-only operations, Secure MCP Tunnel, canonical TaskLedger, v4.1.4 modern MCP transport, resource policy, and `COMPLETED != VERIFIED` semantics are unchanged.

## 4.1.4 - 2026-08-25 - QNAP Modern MCP Transport Reliability

### Production 502 causal remediation

- Reproduced the hosted-path failure at the MCP HTTP protocol boundary: valid modern `server/discover` requests were rejected by the v4.1.3 legacy server-managed session router with HTTP 400 `invalid_session`, which surfaced through the Secure MCP Tunnel path as a 502.
- Migrated remote MCP serving from the monolithic v1 SDK to pinned stable v2 split packages and stateless `createMcpHandler` handling.
- Removed the obsolete eight-entry protocol-session map and the requirement for legacy `Mcp-Session-Id` on current clients while retaining SDK-provided compatibility for older client flows.
- Preserved process-bound `cos` identity, the exact 27-tool CoS catalog, the 10-agent roster, human-only operations, canonical TaskLedger semantics, and the Secure MCP Tunnel source-IP gate.
- Strengthened `/readyz` so readiness requires successful modern MCP discovery in addition to bound-agent and audit-chain health.

### QNAP deployment and release engineering

- Advanced the QNAP deployment release, image label, release workflow, deterministic bundle builder, environment metadata, and acceptance procedures to `4.1.4` / `v4.1.4`.
- Added QNAP-042 through QNAP-047 behavior scenarios plus production-image modern discovery and ten-request sequential transport regression coverage.
- Updated the operator runbook for the current QNAP account where Docker access requires `sudo`; the host-side privileged invocation does not change the long-running non-root UID/GID 65532 runtime.
- Bundled the v4.1.4 debugging record, targeted security receipt, release notes, deployment guide, and sequential hosted-path acceptance instructions.

### Verification and security

- Exact-candidate gates cover npm build/tests/smoke/audit, Python contracts and drift checks, Ruff, mypy, Bandit, 100% branch-aware coverage, deterministic bundle/checksum generation, production image construction, modern MCP discovery, ten sequential requests, direct-ingress 403, real Docker permission handoff, hardened runtime controls, restart recovery, and Docker-mediated SQLite backup integrity.
- Security applicability remains TARGETED. SEC-QNAP-021 documents the obsolete protocol-session boundary and SEC-QNAP-022 documents the prior readiness false-positive. No authentication, authorization, tool, persistence, or human-principal boundary is expanded.

### Version boundary

- Repository/QNAP deployment release: `4.1.4` / tag `v4.1.4`.
- Canonical Phase 1 agent/runtime authority contract remains `4.0.0`; exactly 10 agents, 27 governed CoS tools, human-only operations, Secure MCP Tunnel, resource policy, and `COMPLETED != VERIFIED` semantics are unchanged.

## 4.1.3 - 2026-08-25 - QNAP Non-Root Deployment Reliability

### Live QNAP root-cause remediation

- Removed the invalid assumption that a Docker-authorized QNAP SSH user can host-`chown` shared-folder state to UID/GID 65532.
- Added constrained one-shot Docker helpers for runtime state and tunnel-secret ownership/mode handoff while preserving the long-running UID/GID 65532 runtime.
- Changed missing-ledger staging to stdin streaming through the runtime identity with atomic installation.
- Changed host preflight to validate canonical-state permissions as runtime UID/GID 65532 instead of the SSH user.
- Changed online backup export to `docker cp` plus in-container cleanup so host ownership of runtime-created state is unnecessary.
- Added deployment-local Docker CLI configuration to eliminate dependency on the unreadable Container Station QPKG-home config.

### Deployment and update observability

- Added a shared POSIX-shell observability library with a durable run ID, timestamped structured logs, stage and safe command labels, exact return-code preservation, bounded retention, and `DIAGNOSTIC_LOG` receipts.
- Added bounded failure diagnostics for operator/platform identity, Docker/Compose resolution, filesystem ownership/modes, capacity, relevant mounts, and Mesh container state.
- Explicitly excluded tunnel-secret contents, `.env` contents, process environments, credential-bearing argv, and tunnel-client logs from automated diagnostics; bounded Mesh application log tails are defensively redacted.
- Added a reusable QNAP Deployment and Update Script Observability Standard for future deployment, upgrade, rollback, backup, migration, and maintenance tooling.

### Verification and security

- Added ready BDD scenarios QNAP-038 through QNAP-041.
- Added shell regressions for observability, return-code preservation, secret non-collection, numeric UID/GID validation, and constrained Docker permission-helper arguments.
- Extended CI to require actual Docker bind-mount ownership handoff, runtime-identity state access, Docker-mediated backup export, SQLite integrity, release-bundle construction, production image/runtime security, readiness, direct MCP denial, and restart recovery.
- Classified the remediation TARGETED for Docker/filesystem/persistence/secret/logging security review without expanding MCP or network authority.

### Version boundary

- Repository/QNAP deployment release: `4.1.3` / tag `v4.1.3`.
- Canonical Phase 1 agent/runtime authority contract remains `4.0.0`; the 10-agent roster, human-only operations, tool allowlists, Secure MCP Tunnel, resource policy, and `COMPLETED != VERIFIED` semantics are unchanged.

## 4.1.2 - 2026-08-25 - QNAP Compose Discovery Fix

### Live deployment defect remediation

- Fixed the QNAP SSH case where Docker is available and Container Station has Compose V2 installed, but `docker compose` is not callable from the operator shell.
- Added bounded Compose V2 discovery through Docker client plugin metadata, standard Docker CLI-plugin paths, and the Container Station QPKG install path.
- Require a Compose V2 version response and reject Compose V1.
- Expanded the read-only QNAP environment probe to report the Container Station install path, Docker-reported Compose plugin path, and executable Compose candidates.

### Operator session safety

- Replaced the unsafe top-level copy/paste failure pattern with a subshell deployment wrapper so `exit` on a failed check terminates only the installer subshell and never the parent SSH login.
- Added QNAP-036 and QNAP-037 to codify Compose fallback and SSH-session preservation.
- Added a shell regression that reproduces the observed `docker compose` failure while a direct Compose V2 plugin remains available.

### Version boundary

- Repository/QNAP deployment release: `4.1.2` / tag `v4.1.2`.
- The canonical Phase 1 agent authority/runtime package contract remains `4.0.0`; the 10-agent roster, tool allowlists, human-only boundary, networking, TaskLedger authority, and `COMPLETED != VERIFIED` semantics are unchanged.

## 4.1.1 - 2026-08-25 - QNAP Deployment Automation

### Automated operator lifecycle

- Reduced first deployment to `cd /share/Docker && sh mesh-cos-mcp-deploy.sh` after bundle extraction.
- Automated release-bound local Mesh image build and content-addressed image-ID recording.
- Automated OpenAI tunnel-client version retrieval, immutable RepoDigest resolution, and image-ID recording.
- Automated deterministic `.env` generation with no runtime secret values.
- Automated pre-deploy backup, preflight, Compose deployment, bounded health waits, verification, direct non-tunnel denial checks, and post-deploy backup.

### Canonical state and secrets

- Added explicit-source canonical TaskLedger staging only when the target ledger is absent; an existing canonical target is preserved and never silently replaced.
- Added canonical runtime and SQLite integrity validation before deployment.
- Added hidden terminal input for the tunnel runtime API key and file-only storage at the approved secret path with owner `65532:65532`, mode `0400`.
- Kept tunnel runtime secret material out of `.env`, release assets, deployment receipts, and backups.

### Deterministic bundle and recovery

- Added a minimal release-bound Docker build context under `cos-mcp/build-context` so QNAP deployment requires no Git checkout and no separately published Mesh registry image.
- Set `pull_policy: never` on both prepared services and verify configured/running image IDs before and after deployment.
- Expanded backups to dated directories containing SQLite online backup, non-secret Compose/environment configuration, release metadata, image receipts, and `SHA256SUMS` while explicitly excluding `secrets/`.
- Added ChatGPT Secure MCP Tunnel connection, 27-tool catalog, read-only, and idempotent governed-write acceptance instructions.
- Added QNAP BDD scenarios QNAP-031 through QNAP-035 and CI validation of the actual release-bundle build context.

### Version boundary

- Repository/QNAP deployment release: `4.1.1` / tag `v4.1.1`.
- The canonical Phase 1 agent authority/runtime package contract remains `4.0.0`; the 10-agent roster, tool allowlists, human-only boundary, and `COMPLETED != VERIFIED` semantics are unchanged.

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
