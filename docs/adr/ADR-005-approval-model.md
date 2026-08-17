# ADR-005: Approval and Consequential External Actions

- **Status:** Accepted
- **Date:** 2026-08-17

## Decision

Fail closed on L4 actions until a qualified human approval is recorded. Keep L5 decisions Michael-exclusive unless the operating constitution is explicitly changed.

## Scope

Consequential external/public actions, pricing or discount commitments, material commercial obligations, personnel actions, destructive operations, and sensitive legal/regulatory/security/privacy conclusions require human authority in Phase 1.

## Consequences

- Approval obligations cannot be delegated away.
- Agents cannot infer approval from prior behavior or conversational context.
- Message Operations executes approved communications but does not create its own approval authority.
- Approval state is durable and must be inspectable independently of Slack/chat history.
- Monetary thresholds are not invented. Unconfigured threshold-sensitive actions remain approval-required.
