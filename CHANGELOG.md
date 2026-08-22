# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

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

Historical release. Reduced the then-current workforce from 10 registered agents to 9 and externalized Mesh Message Operations as a shared approval-bound execution Skill. Preserved human-only approval/reliability operations, TaskLedger canonical state, completion/verification separation, local stdio MCP, TDD loop engineering, and release gates. This topology is superseded by v4.0.0.

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