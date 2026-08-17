# Mesh AI Chief of Staff Agent Universe

Phase 1 operating core for Mesh Digital LLC's AI Chief of Staff. This is an executive operating control plane for a bounded agent workforce, not a chatbot.

## Operating objective

**Maximize the return on Michael's judgment, relationships, attention, and authority by independently resolving everything that does not require the CEO, and materially improving everything that does.**

This objective governs architecture, authority, delegation, escalation, performance management, and future autonomy decisions.

## Phase 1 status

Version `0.1.0` implements the control foundation, management layer, Phase 1 functional-agent definitions, Slack coordination protocol, and evaluation harness. External business-system integrations remain governed boundaries until credentials, source permissions, and production configuration are supplied.

## Architecture

Phase 1 uses a Python 3.11+ modular monolith. SQLite is the initial canonical task/event ledger behind a narrow persistence boundary. The implementation includes:

- versioned JSON contracts
- canonical Agent Registry
- Task and Outcome Ledger
- explicit task state machine
- L0-L5 decision-rights engine
- delegation and approval controls
- audit/event model with idempotency
- cross-functional conflict arbitration
- CoS orchestration and escalation
- AgentOps performance management
- Answer Desk routing
- consultant-network freshness controls
- Slack thread/task mapping and duplicate-event protection
- prompt-injection and source-permission boundaries
- emergency kill switch

Slack is an observable collaboration layer. It is not the system of record.

## Agent hierarchy

- **CoS**: executive control plane, outcome accountability, decomposition, delegation, arbitration, reallocation, escalation
- **AgentOps**: workforce observability, performance management, health, workload, stalled-work and defect detection
- **Answer Desk**: permission-aware team question resolution, routing, recommendation, and escalation
- **CRO**: commercial executive
- **CFO v1**: Engagement Finance / FP&A only
- **COO v1**: delivery feasibility, capacity, resource readiness
  - **Consultant Network Steward**: consultant fit, freshness, rate, availability confidence, contracting readiness
- **CMO**: marketing executive
  - **VP Content**: editorial production pipeline
- **Devil's Advocate**: independent challenge, never final decision owner
- **Message Operations**: controlled execution boundary for approved communications

Agents are operating identities. Skills are reusable capabilities. Existing Mesh skills are referenced by the registry rather than reimplemented.

## Decision rights

- **L0 Information**: authorized retrieval and factual synthesis may execute automatically.
- **L1 Established policy / precedent**: approved rules may execute automatically and are logged.
- **L2 Reversible operating judgment**: bounded internal decisions may execute within explicit guardrails.
- **L3 Material internal judgment**: agents recommend; CoS resolves only where explicitly delegated, otherwise Michael decides.
- **L4 Human approval required**: consequential commercial, external, public, legal, regulatory, security, privacy, personnel, destructive, sensitive system, and irreversible actions fail closed.
- **L5 Michael exclusive**: firm strategy, major pivots/capital decisions, material client/partner exceptions, senior personnel decisions, CoS authority, decision-rights policy, and material agent-authority expansion.

No monetary thresholds are invented. Until explicitly configured, threshold-sensitive actions remain approval-required.

## Outcome model

A produced file or message is not completion. Tasks progress through explicit states and only reach `VERIFIED` when the defined acceptance test confirms the intended outcome. Verification failure returns work to remediation.

Every task has exactly one accountable owner, with contributors as needed. Normal delegation depth is limited to CoS -> functional executive -> specialist/worker.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/validate-contracts.py
pytest
python -m compileall -q src
```

## Configuration

Copy `.env.example` to `.env` and set runtime values. Do not commit secrets or personal Slack IDs.

Required production configuration includes:

- private agent-operations Slack channel ID
- team-facing Answer Desk channel ID
- Slack bot token and signing secret
- authoritative source connector credentials/permissions
- approval-owner configuration
- any later monetary thresholds explicitly approved by Michael

Keep the automation kill switch available during rollout.

## Testing

The Phase 1 suite covers contract validation, lifecycle transitions, authority, escalation, source permissions, prompt injection, idempotency, deterministic AgentOps scoring, staffing freshness, publication gating, QA failure, quarantine, coordination loops, and missing-source authority.

Pre-merge local verification recorded for `0.1.0`:

- 9 JSON schemas and positive examples validated
- 40 `pytest` tests passed
- Python `compileall` passed
- 13 required Phase 1 evaluation scenarios are represented

GitHub Actions is configured in `.github/workflows/ci.yml`. Do not treat the absence of a surfaced remote workflow result as a passing remote CI run.

## Documentation

Start with:

- `docs/phase-1-operating-contract.md` for the canonical human-readable operating specification
- `docs/architecture.md` for system diagrams and source-of-truth boundaries
- `docs/decision-rights.md` for L0-L5 authority
- `docs/delegation-model.md` for work-contract rules
- `docs/task-lifecycle.md` for state transitions
- `docs/agent-registry.md` for workforce definitions
- `docs/agent-performance.md` for AgentOps scorecards and health states
- `docs/conflict-resolution.md` and `docs/escalation-policy.md` for arbitration and CEO routing
- `docs/slack-agent-protocol.md` and `docs/answer-desk.md` for Slack behavior
- `docs/security-governance.md` for security controls
- `docs/testing-evaluation.md` for verification coverage
- `docs/runbook.md` for operational procedures
- `docs/adr/` for architectural decisions

## Current limitations

The following are governed integration boundaries, not fabricated live integrations:

- Slack network calls
- Mesh Revenue Intelligence
- Mesh Proposals - Engagement P&L Tracker
- Capabilities Partner & Consultant Tracker
- AuthoredUp
- LinkedIn
- existing Mesh skills and Message Operations execution

SQLite is suitable for Phase 1/local operation and should be revisited before multi-instance production deployment.

## Roadmap

Next increments should connect approved authoritative sources and Slack, add runtime agent adapters and deployment telemetry, then gather evidence before changing autonomy, thresholds, scorecard weights, or persistence. Phase 2 practice-specific and industry-specific agents remain out of scope for this release.
