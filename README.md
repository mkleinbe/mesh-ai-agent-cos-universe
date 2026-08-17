# Mesh AI Chief of Staff Agent Universe

Phase 1 operating core for Mesh Digital LLC's AI Chief of Staff. This is an executive operating control plane for a bounded agent workforce, not a chatbot.

## Operating objective
**Maximize the return on Michael's judgment, relationships, attention, and authority by independently resolving everything that does not require the CEO, and materially improving everything that does.**

## Phase 1 architecture
A Python modular monolith implements versioned contracts, agent registry, task/outcome ledger, explicit state machine, decision rights, delegation, approvals, audit events, conflict arbitration, AgentOps performance management, Answer Desk routing, staffing freshness, Slack event idempotency, and a kill switch. SQLite is the initial canonical ledger. Slack is human-visible collaboration only.

## Agent hierarchy
- CoS: executive control plane and cross-functional arbitration
- AgentOps: workforce observability and performance management
- Answer Desk: authorized team question resolution and routing
- CRO: commercial executive
- CFO v1: engagement finance / FP&A only
- COO v1: delivery feasibility and resource readiness
  - Consultant Network Steward
- CMO: marketing executive
  - VP Content
- Devil's Advocate: independent challenge
- Message Operations: controlled communication execution

Agents are operating identities. Skills are reusable capabilities and are referenced by the registry rather than reimplemented.

## Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest
python scripts/validate-contracts.py
```

## Configuration
Copy `.env.example` to `.env` and set runtime values. Slack channel IDs and credentials are configuration. Never commit secrets or personal Slack IDs.

## Governance
Decision rights are L0 through L5. L4 is human approval required. L5 is Michael-exclusive unless explicitly delegated later. Monetary thresholds are intentionally not invented. The CoS cannot silently rewrite functional truth.

## Slack model
One task maps to one Slack thread. Structured messages expose agent identity and state changes. The ledger remains canonical. Phase 1 uses one Slack integration with explicit agent labels, documented in ADR-004.

## Human approval
Pricing, discounts, material commercial terms, contractual language, final scope/staffing/delivery commitments, consequential external messages, public publishing/claims, legal/regulatory/security/privacy conclusions, capital/investor actions, personnel decisions, destructive operations, sensitive system changes, material CRM truth changes, and irreversible actions fail closed without approval.

## Development and testing
The suite includes contract validation, lifecycle tests, authority/escalation controls, security/prompt-injection tests, idempotency checks, deterministic AgentOps scoring, and 13 representative Phase 1 evaluations.

## Current limitations
External Mesh skills, Slack network calls, Revenue Intelligence, proposal P&L, consultant tracker, AuthoredUp, LinkedIn, and Message Operations are represented as governed integration boundaries/adapters, not live credentials or fabricated integrations. SQLite is suitable for Phase 1/local operation, not the final multi-instance persistence layer.

## Roadmap
Next increments should connect approved authoritative sources and Slack, add runtime agent adapters, introduce deployment/telemetry, then gather evidence before changing autonomy, thresholds, scorecard weights, or persistence.
