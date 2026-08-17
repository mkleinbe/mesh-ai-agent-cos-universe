# Changelog

All notable changes to the Mesh AI Chief of Staff Agent Universe are documented here.

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

### Verified
- JSON Schema validation completed successfully for all 9 Phase 1 schemas and positive fixtures.
- Local `pytest` verification completed with 40 passing tests after two pressure-test defects were corrected.
- Local Python `compileall` verification completed successfully.

### Integration boundaries
The following are deliberately represented as governed adapters or authoritative-source boundaries rather than fabricated live integrations:
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
