# ADR-003: Structured Agent Communication

- **Status:** Accepted
- **Date:** 2026-08-17

## Decision

Use structured task, delegation, event, decision, approval, conflict, performance, and Slack message contracts rather than free-form agent-to-agent chat as the operating interface.

## Rationale

Structured records preserve accountability, authority, evidence, acceptance criteria, idempotency, and auditability. Free-form conversation may support explanation, but it cannot be the canonical control mechanism.

## Consequences

- Canonical state is persisted independently of chat surfaces.
- Slack messages use named message types and task identifiers.
- Delegated work has explicit success criteria and acceptance tests.
- Future adapters must translate external interactions into governed records rather than bypassing the control plane.
