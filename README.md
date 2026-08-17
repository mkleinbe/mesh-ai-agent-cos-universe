# Mesh AI Chief of Staff Agent Universe

Phase 1 operating core for Mesh Digital LLC's AI Chief of Staff. This is an executive operating control plane for a bounded agent workforce, not a chatbot.

## Operating objective

**Maximize the return on Michael's judgment, relationships, attention, and authority by independently resolving everything that does not require the CEO, and materially improving everything that does.**

This objective governs architecture, authority, delegation, escalation, performance management, and future autonomy decisions.

## Phase 1 status

Version `0.2.0` closes the prioritized Phase 1 engineering gaps identified on 2026-08-17. The repository now contains an executable, contract-validated operating core with durable orchestration, canonical persistence, governed functional adapters, secure Slack coordination, outcome verification, AgentOps, Answer Desk workflows, reliability controls, success-metric aggregation, and stateful end-to-end evaluations.

External business systems and Mesh skills remain injected integration dependencies. The runtime does not fabricate connectivity when credentials or source adapters are absent.

## Architecture

Phase 1 uses a Python 3.11+ modular monolith. SQLite is the Phase 1 canonical ledger behind a narrow persistence boundary. The implementation includes:

- nine versioned JSON contracts with runtime validation
- canonical JSON-backed Agent Registry with audited runtime-health overrides
- durable tasks, events, delegations, approvals, decisions, conflicts, performance events, scorecards, verifications, metrics, Slack thread mappings, idempotency keys, and work leases
- CoS application service for intake, triage, planning, assignment, delegation, progress states, approval, remediation, outcome verification, reassignment, and closure
- explicit task state machine separating `COMPLETED` from `VERIFIED`
- L0-L5 decision-rights and human-approval controls
- complete delegation invariants, including objective integrity, bounded authority, approval inheritance, one active owner, no circular delegation, and CoS-controlled cross-functional routing
- cross-functional conflict and decision records preserving functional source authority
- governed functional agent adapters with invocation-time tool/source authorization
- Message Operations human-approval enforcement for consequential external sends
- durable AgentOps events, rolling scorecards, workload/stall signals, defect taxonomy, and portfolio recommendations
- source-aware Answer Desk dispositions and metrics
- Slack Web API transport, request-signature verification, durable event dedupe, one-task/one-thread mapping, approval notification boundary, and optional Answer Desk channel boundary
- bounded retry/timeout execution policy, work leases/check-ins, kill switch, duplicate-intake prevention, and auditable execution failures
- deterministic Phase 1 operating metrics without fabricated baselines or cost savings
- stateful evaluation coverage for pursuit/proposal, engagement economics, staffing, marketing publication, Answer Desk, AgentOps failure, Slack security, authorization, and recovery paths

Slack is an observable collaboration layer. It is never the system of record.

## Agent hierarchy

- **CoS**: executive control plane, outcome accountability, decomposition, delegation, arbitration, reallocation, escalation
- **AgentOps**: workforce observability, performance management, health, workload, stalled-work and defect detection
- **Answer Desk**: permission-aware team question resolution, routing, recommendation, approval routing, and escalation
- **CRO**: commercial executive
- **CFO v1**: Engagement Finance / FP&A only
- **COO v1**: delivery feasibility, capacity, resource readiness
  - **Consultant Network Steward**: consultant fit, freshness, rate, availability confidence, contracting readiness
- **CMO**: marketing executive
  - **VP Content**: editorial production pipeline
- **Devil's Advocate**: independent challenge, never final decision owner
- **Message Operations**: controlled execution boundary for approved communications

Agents are operating identities. Skills are reusable capabilities. Existing Mesh skills are injected through governed adapters rather than reimplemented.

## Decision rights

- **L0 Information**: authorized retrieval and factual synthesis may execute automatically.
- **L1 Established policy / precedent**: approved rules may execute automatically and are logged.
- **L2 Reversible operating judgment**: bounded internal decisions may execute within explicit guardrails.
- **L3 Material internal judgment**: agents recommend; CoS resolves only where explicitly delegated, otherwise Michael decides.
- **L4 Human approval required**: consequential commercial, external, public, legal, regulatory, security, privacy, personnel, destructive, sensitive system, and irreversible actions fail closed.
- **L5 Michael exclusive**: firm strategy, major pivots/capital decisions, material client/partner exceptions, senior personnel decisions, CoS authority, decision-rights policy, and material agent-authority expansion.

No monetary thresholds are invented. Until explicitly configured, threshold-sensitive actions remain approval-required.

## Outcome model

A produced file, model, or message is not completion. `COMPLETED` means execution is asserted complete. `VERIFIED` requires the configured acceptance evaluator to run, persist a pass/fail verification record, and supply evidence. Failed verification returns work to `REWORK`.

Every task has exactly one accountable owner, with contributors as needed. Normal delegation depth remains CoS -> functional executive -> specialist/worker.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python scripts/validate-contracts.py
ruff check src tests scripts
mypy src
pytest
python -m pip_audit
python -m compileall -q src
```

## Configuration

Copy `.env.example` to `.env` and set runtime values. Do not commit secrets or personal Slack IDs.

Current Slack coordination configuration:

- agent-operations channel: `#mesh-agent-ops`
- Channel ID: `C0BRL4GCL3A`
- configuration: `MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID=C0BRL4GCL3A`

Production activation still requires environment-specific configuration rather than code changes:

- Slack bot token and signing secret
- team-facing Answer Desk Slack channel ID when selected
- approved authoritative Mesh source/skill invokers and their credentials/permissions
- approval-owner configuration for the production environment
- any later monetary thresholds explicitly approved by Michael

Keep the automation kill switch available during rollout.

## Testing and CI

The TDD remediation branch was driven through red-green-refactor loops and stateful acceptance tests. The final pre-merge GitHub Actions run validates:

- all nine contracts and fixtures
- Ruff critical correctness checks
- mypy across the source package
- pytest with a 65% minimum coverage gate
- dependency vulnerability audit
- Python compileall

The latest green remediation run executed **44 tests with 82.67% total coverage** and reported **no known dependency vulnerabilities**.

## Documentation

Start with:

- `docs/phase-1-operating-contract.md` for the canonical human-readable operating specification
- `docs/phase-1-gap-assessment-2026-08-17.md` for the original gap audit and remediation closure
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

## Remaining deployment boundaries

These are environment/configuration dependencies, not unresolved Phase 1 engineering gaps:

- live Slack execution requires the bot token and signing secret
- the Answer Desk Slack interface requires its channel ID
- Mesh Revenue Intelligence, Engagement P&L, consultant tracker, AuthoredUp, LinkedIn, and existing Mesh skills require approved real invokers/credentials
- SQLite remains the Phase 1 persistence choice and should be revisited before multi-instance or horizontally scaled deployment

No broader autonomy, pricing authority, public publishing authority, material commercial commitment authority, or L5 authority was added by the remediation.
