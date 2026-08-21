# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

## 1.1.0 - 2026-08-21 - Local ChatGPT MCP

### ChatGPT-local MCP runtime

- Refactored `mesh-cos-mcp` from a required remote HTTPS deployment into a bundled `LOCAL_STDIO` MCP runtime for ChatGPT, following the established Mesh Revenue Intelligence local-MCP pattern.
- Added the TypeScript MCP package under `mcp/` using the official Model Context Protocol SDK and `node mcp/dist/index.js` as the checked-in entry point.
- Added `mesh_cos.mcp_stdio_bridge` to bridge bounded JSON requests into the existing Python `mesh_cos.mcp_runtime.MCPRuntime` without duplicating business or governance logic.
- Added immutable per-process agent binding through `MESH_COS_AGENT_ID` and shared canonical state through `MESH_COS_LEDGER_PATH`.
- Removed the ChatGPT requirement for `MESH_COS_MCP_SERVER_URL`; managed remote transport is optional and non-authoritative.

### Security, authority, and reliability

- Preserved exact per-agent MCP allowlists and deny-by-default runtime authorization.
- Kept `approval.record_decision` and `reliability.human_override` human-only and excluded from all agent tool catalogs.
- Added bounded MCP argument handling, safe error categories, raw Python stderr suppression, and no client-supplied code/import/shell execution.
- Preserved L4 qualified-human approval, Michael-exclusive L5, `TaskLedger` canonical state, server-owned replay behavior, and separate `task.complete` / `task.verify` acceptance boundaries.

### TDD and release engineering

- Started the enhancement with acceptance tests before implementation and used repeated RED/GREEN loop engineering to close runtime, manifest, documentation, ordering, security, and drift defects.
- Added TypeScript build/tests, a real stdio MCP certification, canonical persistence checks across MCP calls, human-only exclusion tests, safe-denial tests, and npm audit to CI.
- Removed an unnecessary dependency after npm surfaced high/moderate vulnerability findings, returning the MCP package to zero reported npm vulnerabilities in CI.
- Preserved strict source Ruff, mypy, contract validation, runtime/documentation drift, Workspace Agent package drift, 100% branch-aware `mesh_cos` coverage, high-severity Bandit, and compileall release gates.

### Skills, Workspace Agents, and documentation

- Reconciled all 11 Workspace Agent manifests to release `1.1.0`, `LOCAL_STDIO`, exact per-agent identity binding, and shared canonical ledger configuration.
- Updated all role Skill production-readiness references for the bundled local MCP model.
- Updated the Builder handoff, production preflight, README, architecture, security/governance guide, runbook, ChatGPT package guide, MCP guide, release notes, and release record.

## 1.0.0 - 2026-08-17 - Production Readiness

### Stable production-readiness milestone

- Established `1.0.0` as the first stable semantic production-readiness release and `v1.0.0` as the release tag.
- Preserved the completed Phase 1 operating constitution while hardening the runtime, Workspace Agent deployment layer, Skills, MCP boundary, CI, preflight, and release process for production activation.
- Explicitly separated repository production readiness from environment-specific production activation.

### Release engineering and quality

- Raised branch-aware `mesh_cos` coverage to a required 100% release gate.
- Added strict source Ruff, mypy, dependency integrity, contract validation, runtime/documentation drift, Workspace Agent package drift, high-severity Bandit scanning, and compileall to the release path.
- Added `ProductionPreflight` and `scripts/production-preflight.py` to fail closed on kill-switch state, HTTPS MCP configuration, registry health, runtime bindings, serialized runtime composition, optional Slack/Answer Desk requirements, and optional audit-chain integrity.
- Added Dependabot coverage for Python quality dependencies and GitHub Actions.

### Runtime and MCP hardening

- Added serialized `mesh_cos.mcp_runtime.MCPRuntime` as the production MCP composition boundary with exact tool-surface validation.
- Split human-only MCP operations from agent operations. `approval.record_decision` and `reliability.human_override` require authenticated human principals.
- Derive agent identity, role, implementation provenance, and authority server-side from the canonical registry.
- Enforce L4 approval evidence and Michael-exclusive L5 semantics at the runtime boundary.
- Added server-owned replay executor registration. Client-supplied callables, module paths, shell commands, and executable source instructions are never replay mechanisms.
- Added governed `task.complete` for accountable owners while preserving separate `task.verify` acceptance verification.
- Made Slack event idempotency and governance-event idempotency atomic with canonical persistence.
- Preserved insertion chronology for consequential records and hardened timestamp compatibility across staffing, AgentOps, leases, Slack, and metrics.
- Fixed fail-closed source authorization when an explicit allowed-source list is empty, replay/override audit evidence, and atomic decomposition validation.

### Skills and Workspace Agents

- Added a common `references/production-readiness.md` contract to all 11 role Skills and revalidated/repackaged them.
- Aligned all 11 Workspace Agent manifests and the MCP contract to repository release `1.0.0`.
- Reconciled per-agent MCP allowlists, including `task.complete` for accountable worker roles and removal of human-only operations from agent allowlists.
- Hardened the Workspace Agent Builder handoff to require production preflight, 100% release CI, authority/evidence/permission tests, human-spoofing tests, kill-switch tests, replay-safety tests, and completion-versus-verification tests before publication.

### Documentation and release packaging

- Added `docs/release-1.0.0-production-readiness.md` with Mermaid release, execution, and activation diagrams.
- Updated the root README, documentation index, architecture, production-readiness guide, testing/evaluation guide, operations runbook, security/governance guidance, ChatGPT deployment documentation, MCP documentation, and Workspace Agent Builder handoff for `v1.0.0`.
- Added `RELEASE.md` as the canonical GitHub release-note source.
- Added a GitHub Actions release workflow that creates the semantic `v1.0.0` tag and `v1.0.0 Production Readiness` release on the merged `main` commit.

### Activation boundary

The repository does not fabricate live environment configuration. Production activation still requires the approved HTTPS `mesh-cos-mcp` endpoint, `MESH_COS_MCP_SERVER_URL`, Workspace authentication and app permissions, applicable Slack credentials, a dedicated Answer Desk channel, production approval-owner mappings, approved source/Skill credentials, secrets management, and runtime/deployment ownership.

## 0.2.0 - 2026-08-17 - ChatGPT Workspace Agent packages

### Workspace Agent deployment layer

- Added 11 OpenAI Skill source packages, one for each canonical Phase 1 agent: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, Devil's Advocate, and Message Operations.
- Added 11 exact Workspace Agent manifests with name/description, model preference and fallback, reasoning effort, knowledge files, role Skill, Workspace apps, channel configuration, starter prompts, write approval, Connector Action Constraints, and private-until-tested publication state.
- Preserved the canonical registry as organizational authority and `TaskLedger` as canonical operating state. ChatGPT, Slack, and the governance Sheets remain non-canonical surfaces.

### Mesh CoS MCP

- Added `chatgpt/mcp/mesh-cos-mcp.v1.json`, mapping Workspace Agent calls to the existing Phase 1 runtime rather than reimplementing business logic.
- Added per-agent least-privilege MCP tool allowlists for registry, task/work graph, delegation, approval, conflict, governance, AgentOps, Answer Desk, governed Skill invocation, metrics, replay, and human override.
- Added `WorkspaceAgentMCPPolicy` to enforce the checked-in allowlists server-side with deny-by-default behavior and runtime-binding validation.
- Added read-only `registry.list_agents` and `approval.get`; Message Operations can inspect approval state but cannot decide its own approval.
- Added MCP-safe `ChiefOfStaffService.record_verification_result()` requiring a named verifier and explicit evidence. Passing verification with no evidence fails closed without moving a task to `VERIFIED`.

### App and approval controls

- Workspace write actions default to **Always ask** as product-level defense in depth; this does not replace Mesh L4/L5 governance.
- Restricted CoS and AgentOps Slack writes to internal `#mesh-agent-ops` coordination.
- Kept Answer Desk Slack disabled until a dedicated channel ID is configured.
- Kept CRO Apollo research/enrichment only and Gmail/LinkedIn non-outbound.
- Kept CMO and VP Content LinkedIn non-publishing and AuthoredUp analytics/draft only.
- Kept CFO, COO, and Consultant Network Steward evidence access read-only.
- Kept Message Operations outbound execution approval-bound and materially immutable without reapproval.

### TDD and loop engineering

- Started with an intentionally failing Workspace Agent acceptance suite before implementation.
- Initial RED CI confirmed missing Skills, manifests, MCP contract, and builder handoff.
- Closed additional gaps discovered during the loop: registry discovery, approval-read access, server-side MCP enforcement, remote verification, exact raw-registry authority comparison, risky app constraints, and release provenance.
- Corrected a test defect that compared human-readable authority to normalized runtime authority, while retaining separate normalized-runtime coverage.
- Added `scripts/check-chatgpt-packages.py` and extended runtime/documentation drift validation to prevent registry, Skill, manifest, MCP, permission, release, or documentation drift.

### Documentation and deployment handoff

- Added `chatgpt/README.md`, MCP documentation, exact builder manifests, a TDD gap-assessment record, and `chatgpt/workspace-agent-builder-prompt.md`.
- Updated README, Agent Operating Instructions, architecture, registry, decision rights, explainable-decision/audit governance, security, testing, runbook, and documentation index.
- Added `MESH_COS_MCP_SERVER_URL` as a non-secret environment placeholder. The repository does not fabricate a deployed MCP endpoint or workspace credentials.

## 0.1.4 - 2026-08-17 - Canonical Phase 1 role model

- Standardized durable organizational identities as CRO, CFO, COO, Consultant Network Steward, CMO, and VP Content.
- Separated organizational naming from implementation versioning and added runtime/CI enforcement against version-bearing role names.
- Expanded the six functional role capability surfaces inside their existing Phase 1 authority boundaries.
- Preserved CFO as Engagement Finance / FP&A only, COO under CoS work-graph orchestration, and human-gated public/commercial consequence boundaries.
- Added the existing Client Servicing Messaging capability to CRO's governed Skill composition for expansion/client-servicing work.
- Reconciled role cards, registry, architecture, governance, tests, and release documentation.

## 0.1.3 - 2026-08-17 - Explainable decisions and auditable agent governance

- Added closed `mesh.cos.decision.v2` and `mesh.cos.agent-event.v2` contracts while preserving v1 compatibility.
- Added explainable decision provenance, alternatives, criteria, confidence, risk, reversibility, lineage, and outcome validation.
- Added fully auditable actor/action/result/event provenance and a tamper-evident SHA-256 audit chain.
- Applied `config/governance-policy.v1.json` to all registered agents and governed Skill/tool invocations.
- Initialized the CoS Decision Log and CoS Audit Log Google Sheets as human-readable operational mirrors while preserving `TaskLedger` as canonical state.
- Prohibited private chain-of-thought, hidden reasoning traces, secrets, credentials, tokens, and unnecessary personal data from governance records.

## 0.1.2 - 2026-08-17 - Final Phase 1 requirement closure

- Aligned runtime `TaskRecord`, `Delegation`, `AgentRecord`, conflict, approval, and audit behavior with canonical contracts.
- Completed CoS work decomposition, dependencies, check-ins, reassignment, stalled-work remediation, escalation, governed functional invocation, verification, closure, and supersession.
- Added Slack freshness/replay protection, structured messages, one-task/one-thread persistence, approval notifications, and separate Answer Desk channel configuration.
- Completed durable AgentOps rolling evidence, workload/SLA signals, recommendation vocabulary, replay/human override reliability, kill-switch enforcement, and the original Phase 1 metric set.
- Added dependency integrity, drift checks, Ruff critical linting, coverage enforcement, high-severity Bandit scanning, schema validation, pytest, and compileall to CI.

## 0.1.1 - 2026-08-17 - Phase 1 remediation and documentation alignment

- Replaced duplicate hardcoded registry state with canonical loading from `agents/registry.json`.
- Added durable consequential records for tasks, delegations, conflicts, approvals, verification, performance, Answer Desk, Slack mappings, idempotency, and audit.
- Strengthened delegation, authorization, AgentOps, Slack, reliability, metrics, and functional-adapter boundaries.
- Reconciled documentation and Mermaid architecture diagrams to the remediated runtime.

## 0.1.0 - 2026-08-17 - Phase 1 operating core

- Added the Python 3.11+ modular-monolith CoS control plane with SQLite-backed `TaskLedger`.
- Added versioned contracts, the canonical 11-agent registry, explicit L0-L5 decision rights, task lifecycle, delegation, approval, audit, conflict, AgentOps, Answer Desk, Slack protocol, and kill-switch controls.
- Preserved Phase 1 non-goals: no autonomous pricing/discounts, consequential external/public commitments, unrestricted enterprise finance, legal/regulatory/security/privacy/personnel conclusions, recursive swarms, autonomous agent creation, or self-expansion of authority.

<!-- mesh-cos-v2-shared-da -->
## v2.0.0 current architecture

The live Phase 1 runtime is a **10-agent** organization. The former repository-local Devil's Advocate agent and duplicate role Skill are removed. **Mesh Devil's Advocate** is an external **shared Skill** available only to Chief of Staff and CRO through governed Skill invocation. It is **advisory** only, cannot overwrite **canonical facts**, cannot execute external actions, and returns decision authority to the owning role or qualified human. `TaskLedger` remains canonical state; ChatGPT uses `LOCAL_STDIO` through `MCPRuntime` with deny-by-default allowlists, human-only approval/override paths, `check-chatgpt-packages.py` drift enforcement, and the 100% branch-aware coverage gate. Historical references to an 11-agent roster or a local Devil's Advocate role describe superseded releases only.

