# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

## 0.2.0 - 2026-08-17 - Phase 1 gap closure

### Remediated
- Completed the nine Phase 1 JSON contracts and aligned runtime models with contract validation before canonical persistence.
- Replaced the duplicate hardcoded runtime agent definition with the canonical JSON Agent Registry, including contract validation and durable audited health overrides.
- Expanded the SQLite control plane to first-class durable records for tasks, events, delegations, approvals, decisions, conflicts, performance events, scorecards, registry changes, acceptance verifications, Slack task/thread mappings, metrics, intake idempotency, and work leases.
- Added a durable CoS application service for intake, triage, planning, assignment, delegation, progress states, human approvals, remediation, reassignment, outcome verification, and closure.
- Added executed acceptance-test results so `VERIFIED` requires a persisted pass/fail evaluation rather than the mere presence of evidence.
- Completed delegation controls for parent-objective integrity, outcome integrity, approval inheritance, authority narrowing, circular prevention, active ownership, measurable acceptance, delegation depth, and CoS-controlled cross-functional routing.
- Added governed executable functional-agent adapters with invocation-time tool/source authorization and an explicit Message Operations approval gate for consequential external sends.
- Added a live-capable Slack Web API transport, signed inbound event receiver, durable event dedupe, one-task/one-thread mapping, approval notification, and Answer Desk channel boundary around `#mesh-agent-ops` (`C0BRL4GCL3A`).
- Added durable conflict/decision governance and a source-aware Answer Desk with all required dispositions and metric events.
- Added versioned AgentOps policy configuration, durable performance events/scorecards, workload and stalled-work signals, defect taxonomy, and the full portfolio recommendation set.
- Added bounded retries/timeouts, work leases/check-ins, duplicate-intake prevention, kill-switch enforcement, and audited execution failures.
- Added deterministic Phase 1 metric aggregation for CEO leverage, first-pass quality, rework, escalation quality, cycle/stalled work, outcomes, failure, approval cycle, conflict, conversation loops, contributors, and cost where telemetry exists.
- Added stateful end-to-end evaluation coverage for pursuit/proposal, engagement economics, staffing, marketing publication, Answer Desk, AgentOps failure, Slack security, authorization, approval, verification, and recovery paths.

### Engineering quality
- Added runtime `jsonschema` dependency because contract enforcement is now production behavior.
- Added Ruff, mypy, pytest coverage, pip-audit, and compileall CI quality gates.
- Set a 65% minimum coverage gate; the final remediation verification reached 82.67% coverage.

### Verified
- 9 contract schemas and fixtures validated successfully.
- 44 tests passed in the final remediation verification run.
- Ruff passed.
- mypy passed across the source package.
- pip-audit reported no known dependency vulnerabilities.
- Python compileall passed.

### Deployment configuration still required
These are external environment dependencies rather than unresolved engineering gaps:
- Slack bot token and signing secret.
- Team-facing Answer Desk Slack channel ID once selected.
- Approved real invokers/credentials for Mesh Revenue Intelligence, Engagement P&L, consultant tracking, AuthoredUp, LinkedIn, and existing Mesh skills.
- Production approval-owner configuration.

### Authority unchanged
- No autonomous pricing or discounts.
- No autonomous consequential external sends or public publishing.
- No enterprise-accounting CFO authority beyond Engagement Finance / FP&A scope.
- No autonomous legal, regulatory, security, privacy, personnel, or irreversible decision authority.
- No autonomous agent creation or material authority expansion.
- L5 remains Michael-exclusive unless explicitly changed later.

## 0.1.0 - 2026-08-17 - Phase 1 operating core

### Added
- Python 3.11+ modular-monolith control plane with SQLite-backed canonical task and event ledger.
- Versioned JSON contracts for agent records, tasks, delegations, agent events, decisions, conflicts, approvals, performance events, and performance scorecards.
- Canonical Phase 1 agent registry covering CoS, AgentOps, Answer Desk, CRO, CFO v1, COO v1, Consultant Network Steward, CMO, VP Content, Devil's Advocate, and Message Operations.
- Explicit L0-L5 decision-rights model with fail-closed human approval at L4 and Michael-exclusive authority at L5 unless explicitly delegated later.
- Task state machine separating artifact completion from verified business outcome.
- Delegation controls enforcing one accountable owner, bounded delegation depth, no circular delegation, no authority widening, and no delegated-away approval obligations.
- Audit/event envelope with idempotency support and consequential-action logging.
- Conflict arbitration preserving functional source authority while assigning cross-functional tradeoffs to CoS.
- AgentOps performance scorecard, health states, stalled-work detection, rework tracking, escalation-quality controls, and coordination-loop detection.
- Permission-aware Answer Desk routing and disposition model.
- Consultant staffing freshness and readiness controls, including `REQUIRES_REFRESH` behavior for stale availability.
- Slack structured-message protocol, one-task-per-thread mapping, duplicate-event protection, and explicit acting-agent labels.
- Prompt-injection boundary treating retrieved documents and messages as untrusted data rather than operating instructions.
- Emergency kill switch and quarantine controls for severe defects or unauthorized actions.
- Five architecture decision records covering runtime, ledger, structured messaging, Slack identity, and approval/external-action design.
- Contract, lifecycle, authority, security, idempotency, performance, and 13 required Phase 1 evaluation scenarios.

### Documentation finalization
- Expanded the canonical Phase 1 operating contract, repository guide, documentation index, AgentOps performance policy, agent-registry policy, Answer Desk protocol, delegation model, conflict/escalation policies, observability, security/governance, Slack protocol, task lifecycle, testing/evaluation guide, and operations runbook.
- Expanded `AGENTS.md` into repository-wide operating instructions for agent behavior and authority.
- Expanded `agents/registry.json` from an ID index into a machine-readable Phase 1 registry containing role, parent, domain, source authority, skills/tools, contracts, permitted/prohibited actions, decision authority, approvals, delegation permissions, performance policy, confidentiality class, and runtime health for every Phase 1 agent.

### Verified
- JSON Schema validation completed successfully for all 9 Phase 1 schemas and positive fixtures.
- Local `pytest` verification completed with 40 passing tests after two pressure-test defects were corrected.
- Local Python `compileall` verification completed successfully.
- GitHub Actions pre-merge CI for the Phase 1 implementation completed successfully, including dependency installation, contract validation, pytest, and compileall.

### Integration boundaries
The following were deliberately represented as governed adapters or authoritative-source boundaries rather than fabricated live integrations:
- Slack network calls
- Mesh Revenue Intelligence
- Mesh Proposals - Engagement P&L Tracker
- Capabilities Partner & Consultant Tracker
- AuthoredUp
- LinkedIn
- Existing Mesh agent skills and Message Operations execution

### Phase 1 limitations
- No autonomous pricing or discounts.
- No autonomous consequential external sends or public publishing.
- No enterprise-accounting CFO authority beyond Engagement Finance / FP&A scope.
- No autonomous legal, regulatory, security, privacy, personnel, or irreversible decision authority.
- No autonomous creation of agents or material expansion of agent authority.
- SQLite is the Phase 1/local persistence choice and should be revisited before multi-instance production deployment.
