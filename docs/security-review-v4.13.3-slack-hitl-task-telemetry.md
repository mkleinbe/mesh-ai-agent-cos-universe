# Security Review: v4.13.3 Slack HITL Task Telemetry

Security applicability: TARGETED.

## Sensitive surfaces

- Slack provider input and human identity
- approval-adjacent reconciliation
- TaskLedger persistence
- replay/idempotency
- MCP/agent tool execution
- auditability

## Required security properties

1. Trigger-carried text, identity, approval, actor, decision, or task state is never trusted.
2. A touch can be recorded only after exact Slack provider reread and configured manual-human verification.
3. The task/thread binding must match canonical governed state before a touch is recorded.
4. The provider event can affect human_touches at most once.
5. Human interaction telemetry cannot itself create approval authority or advance task lifecycle.
6. Existing strict approval grammar and canonical approval state remain authoritative.
7. The locator-only dispatcher, Slack bot/app rejection, edit rejection, and audit chain remain unchanged.

## Review result

The change adds no new principal, transport, credential, network path, approval command, or external-action authority. The telemetry mutation occurs behind existing provider verification and governed binding checks. The atomic provider-event record plus TaskRecord increment prevents double counting after retry or process restart.

Residual production acceptance remains contingent on exact-source QNAP 4.4.2 deployment and live dispatcher-only UAT.
