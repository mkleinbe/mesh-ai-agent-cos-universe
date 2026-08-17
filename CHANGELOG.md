# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

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
