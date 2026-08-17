# ADR-001: Phase 1 Runtime

- **Status:** Accepted
- **Date:** 2026-08-17

## Decision

Use Python 3.11+ as a modular monolith for the Phase 1 AI Chief of Staff operating core.

## Context

Phase 1 requires strong governance boundaries, deterministic tests, explicit contracts, and rapid iteration. It does not require the operational overhead of microservices, a broker, or an autonomous agent swarm.

## Consequences

- Services such as CoS orchestration, delegation, AgentOps, Answer Desk, Slack coordination, authorization, metrics, and functional adapters live in one deployable codebase.
- Internal boundaries remain explicit so persistence and integrations can evolve later.
- TDD and CI can exercise cross-cutting governance behavior without distributed-system noise.
- Multi-instance scale and production persistence are deferred until justified by operating evidence.
