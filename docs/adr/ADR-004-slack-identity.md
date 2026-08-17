# ADR-004: Slack Identity and Coordination

- **Status:** Accepted, implementation boundary expanded by remediation
- **Date:** 2026-08-17

## Decision

Use one governed Slack integration for Phase 1 with explicit acting-agent labels rather than separate bot identities for every agent. Use `#mesh-agent-ops` (`C0BRL4GCL3A`) as the private agent-operations coordination channel.

## Controls

The Slack boundary verifies request signatures, persists event idempotency, persists one-task/one-thread mapping, renders structured message types, and exposes a live-capable Web API client boundary.

## Consequences

- Slack remains observable collaboration, not canonical state.
- Bot token and signing secret remain external configuration and must not be committed.
- A separate team-facing Answer Desk channel is required and must be configured explicitly.
- Per-agent visual identity can be represented in message labels without multiplying app credentials or authority surfaces.
