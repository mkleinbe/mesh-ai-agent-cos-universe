# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

## 0.1.3 - 2026-08-17 - Explainable decisions and auditable agent governance

### Governance contracts

- Added closed `mesh.cos.decision.v2` and `mesh.cos.agent-event.v2` JSON contracts while preserving v1 compatibility.
- Added explainable decision fields for authority, approval, concise decision basis, evidence/source provenance, alternatives, selection criteria, confidence, risk, affected entities, reversibility/reversal conditions, model/skill provenance, outcome validation, lineage, canonical reference, and integrity hash.
- Added fully auditable event fields for sequence/time, actor/action/result, task/correlation/decision/run links, authority/policy, capability/tool, target/source, summaries, evidence/approval, errors, model/skill provenance, risk/classification, retention, canonical reference, and a SHA-256 hash chain.
- Explicitly prohibited private chain-of-thought, hidden reasoning traces, secrets, credentials, tokens, and unnecessary personal data from governance records.

### Cross-agent governance

- Added `config/governance-policy.v1.json` and applied it to every registered agent at registry load.
- Added `governance-journal`, `decision.v2`, and `agent-event.v2` to the shared runtime governance surface without expanding functional authority.
- Added direct audit emission for governed skill/tool invocations.
- Added a compatibility bridge that dual-writes existing v1 audit events into the v2 governance stream.
- Added v2 explainable records for material conflict decisions while retaining the existing v1 decision record during migration.

### Governance registers

- Initialized and began using the CoS Decision Log Google Sheet (`1IJcwPuulqsNAa1lCW2MsmNgH6Vm5INPqTlcH4NR0xpw`).
- Initialized and began using the CoS Audit Log Google Sheet (`1T8vKx4gaUJdeG8kSc18MsBbXpY4EbDF3exZ0RGpvND0`).
- Added `Schema` and `Reference` tabs, field validation, filtering, frozen headers, governance controls, and bootstrap decision/audit records.
- Added `config/governance-logs.v1.json` to version non-secret mirror configuration.
- Preserved `TaskLedger` as canonical state with canonical-first write order and durable mirror-failure recording.

### Testing and documentation

- Added TDD acceptance tests for v2 contract closure, decision explainability, hash-chain integrity/tamper detection, cross-agent policy injection, and Sheet mirror configuration.
- Extended runtime/documentation drift checks to validate the governance contracts, policy, configured Sheet IDs, and documentation tokens.
- Added `docs/explainable-decisions-audit.md` and updated architecture, security, observability, decision rights, conflict resolution, testing, operations, repository instructions, and documentation index.

## 0.1.2 - 2026-08-17 - Final Phase 1 requirement closure

### Runtime integrity

- Aligned runtime `TaskRecord`, `Delegation`, `AgentRecord`, and `AuditEvent` shapes with canonical versioned JSON contracts.
- Expanded AgentRecord lifecycle metadata and the audit event envelope, including `event_version`.
- Expanded material conflict records to preserve source authority, facts, options, positions, confidence, reversibility, CoS recommendation, reversal condition, and decision owner.
- Added runtime/documentation drift validation across schemas, registry records, runtime objects, Slack configuration, and core documentation.

### Chief of Staff operating loop

- Extended `ChiefOfStaffService` with work decomposition, dependency checks, check-ins, reassignment, stalled-work remediation, escalation, governed functional invocation, verification, closure, and idempotent intake.
- Added `ChiefOfStaffWorkforceManager` for durable delegation, management cycles, task supersession, and bounded agent-portfolio recommendations.
- Added governed binding of existing Mesh skills to registered agents without duplicating skill logic.

### Slack and Answer Desk

- Added Slack request freshness/replay protection, structured message parsing, inbound event handling, top-level task-thread creation, and approval notifications for `#mesh-agent-ops` (`C0BRL4GCL3A`).
- Added a separate configurable Answer Desk Slack boundary.
- Added `ROUTED` and `APPROVAL_REQUIRED` dispositions, correction tracking, access-control telemetry, and resolution timing.

### AgentOps, reliability, and metrics

- Added durable rolling performance windows, workload/concurrency observations, missed-deadline and rework signals, rejection reasons, error taxonomy, repeated tool/evidence defect signals, high-cost/low-value signals, and the complete Phase 1 recommendation vocabulary.
- Added timeout handling, execution leases, durable failure records, explicit replay, human override, supersession, duplicate-intake protection, and kill-switch enforcement.
- Expanded metrics to the full original Phase 1 instrumentation set without fabricated baselines or targets.
- Expanded audit coverage across consequential management and governance actions.

### TDD and quality gates

- Added source-derived final-closure acceptance tests before the implementation that satisfies them.
- Added dependency integrity, runtime/documentation drift checks, critical Ruff linting, coverage enforcement, high-severity Bandit scanning, schema validation, pytest, and compileall to CI.
- Added `docs/phase-1-final-closure-2026-08-17.md` and reconciled historical remediation records to the final source-to-runtime audit.

### Production dependencies

- Slack bot token and signing secret.
- Team-facing Answer Desk Slack channel ID.
- Credentials and permissions for approved Mesh authoritative sources and existing skills.
- Production approval-owner configuration.
- Deployment/runtime infrastructure and any explicitly approved future monetary thresholds.

## 0.1.1 - 2026-08-17 - Phase 1 remediation and documentation alignment

### Remediated

- Replaced the duplicate hardcoded runtime registry with canonical loading from `agents/registry.json`.
- Extended SQLite persistence to durable consequential records, including delegations, decisions, conflicts, approvals, registry changes, performance events, scorecards, Answer Desk dispositions, verification records, Slack thread mappings, and idempotency claims.
- Added a Chief of Staff application service for intake, controlled lifecycle advancement, completion, acceptance-test execution, verification, rework, and audit events.
- Strengthened delegation enforcement for ownership, depth, authority, circularity, measurable acceptance, approval inheritance, and action-boundary conflicts.
- Added durable conflict and decision services with reversal conditions.
- Added durable Answer Desk service dispositions.
- Added Slack request-signature verification, durable event dedupe, durable task/thread mapping, structured messages, and a live-capable Web API client boundary for `#mesh-agent-ops` (`C0BRL4GCL3A`).
- Added thin functional adapter boundaries so governed Mesh skills and authoritative sources can be composed without reimplementation.
- Added invocation-time source, tool, and action authorization from registry policy.
- Added versioned AgentOps performance policy and evaluator behavior.
- Added bounded retry handling for transient failures.
- Added deterministic operating metrics for verified outcomes, CEO deflection, and methodologically supported CEO time avoided.
- Expanded stateful remediation tests across orchestration, persistence, verification/rework, delegation, conflicts, Answer Desk, Slack security/idempotency, AgentOps, reliability, metrics, and adapter governance.

### TDD evidence

The remediation increment was executed with test-first acceptance criteria and CI feedback loops. CI surfaced registry-normalization defects during the red/green cycle. They were corrected before merge. The final remediation PR passed contract validation, the complete pytest suite, and Python compileall.

### Documentation

- Reconciled repository documentation to the post-remediation runtime.
- Added Mermaid diagrams for system architecture, task lifecycle, delegation, conflict/decision flow, Agent Registry control, AgentOps, Slack coordination, Answer Desk, testing flow, and operations.
- Reclassified the August 17 gap assessment as historical and mapped each prior code gap to its then-current disposition.
- Refreshed all Phase 1 agent role cards to point to the canonical registry and current governance boundaries.

## 0.1.0 - 2026-08-17 - Phase 1 operating core

### Added

- Python 3.11+ modular-monolith control plane with SQLite-backed canonical task and event ledger.
- Versioned JSON contracts for agent records, tasks, delegations, agent events, decisions, conflicts, approvals, performance events, and performance scorecards.
- Canonical Phase 1 agent registry covering CoS, AgentOps, Answer Desk, CRO, CFO v1, COO v1, Consultant Network Steward, CMO, VP Content, Devil's Advocate, and Message Operations.
- Explicit L0-L5 decision-rights model with fail-closed human approval at L4 and Michael-exclusive authority at L5 unless explicitly delegated later.
- Task state machine separating artifact completion from verified business outcome.
- Delegation, approval, audit, conflict, AgentOps, Answer Desk, staffing-freshness, security, Slack-protocol, and kill-switch controls.
- Five architecture decision records covering runtime, ledger, structured messaging, Slack identity, and approval/external-action design.
- Contract, lifecycle, authority, security, idempotency, performance, and required Phase 1 evaluation scenarios.

### Phase 1 boundaries

- No autonomous pricing or discounts.
- No autonomous consequential external sends or public publishing.
- No enterprise-accounting CFO authority beyond Engagement Finance / FP&A scope.
- No autonomous legal, regulatory, security, privacy, personnel, or irreversible decision authority.
- No autonomous creation of agents or material expansion of agent authority.
- SQLite is the Phase 1/local persistence choice and should be revisited before multi-instance production deployment.
