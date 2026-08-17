# ADR-002: Canonical Task and Control Ledger

- **Status:** Accepted, expanded by Phase 1 remediation
- **Date:** 2026-08-17

## Decision

Use SQLite behind `TaskLedger` as the Phase 1 canonical persistence boundary.

## Context

The operating model requires durable task state, auditability, idempotency, verification, and reconstructable governance records. Slack and agent conversations are not reliable systems of record.

## Consequences

The ledger persists tasks plus consequential typed records, audit/events, idempotency claims, and task/thread mappings. Remediation expanded persistence beyond tasks/events to cover governance objects including delegations, decisions, conflicts, approvals, Answer Desk dispositions, verification, performance/scorecard records, and related control state where emitted.

SQLite is appropriate for Phase 1 and local/single-instance operation. Persistence should be revisited before multi-instance, high-availability, or materially larger production workloads.
