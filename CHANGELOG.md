# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

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
- Reclassified the August 17 gap assessment as historical and mapped each prior code gap to its current disposition.
- Clarified the remaining production dependencies as configuration and external integration work rather than unresolved Phase 1 control-plane code.
- Refreshed all Phase 1 agent role cards to point to the canonical registry and current governance boundaries.

### Remaining production dependencies

- Slack bot token and signing secret.
- Team-facing Answer Desk Slack channel ID.
- Credentials and permissions for approved Mesh authoritative sources and skills.
- Production approval-owner configuration.
- Deployment/runtime infrastructure and any explicitly approved future monetary thresholds.

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
