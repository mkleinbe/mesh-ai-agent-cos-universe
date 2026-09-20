# CHANGELOG v4.13.0

## Added

- Bidirectional Slack HITL interaction state for INFO, QUESTION, MANUAL_ACTION, BLOCKER, STATUS, INCIDENT, and APPROVAL threads.
- Governed `slack-adapter/post_interaction` for bot-authored operational messages with explicit intent, response instructions, authority statement, task binding, and completion condition.
- Provider-reread conversational reconciliation with same-thread bot acknowledgment.
- Direct `CHANGES: <details>` approval handling while retaining the two-step `CHANGE` flow.
- BDD and regression coverage for HITL-CHAT-001 through HITL-CHAT-015.

## Changed

- Approval messages now identify themselves as `APPROVAL REQUIRED` and state the exact explicit decision grammar.
- Exact Slack whole-message inline-code rendering such as `\`APPROVE\`` is normalized without broadening approval grammar.
- Native Slack reconciliation now distinguishes conversational evidence from authority-bearing decisions.
- Duplicate provider delivery is idempotent and does not create duplicate acknowledgments.

## Security

- Work remains a locator-only wake-up. It does not interpret decision text or assert identity.
- Slack provider state, configured human identity, thread binding, pending approval, immutable fingerprint, replay state, and TaskLedger remain authoritative.
- Natural language cannot create L4/L5 approval authority.
- Bot/app-authored, wrong-user, edited, missing, unbound, and provider-unavailable inputs fail closed.

## Compatibility

- Canonical authority/runtime contract remains 4.0.0.
- Production QNAP deployment identity remains 4.4.0. Repository release v4.13.0 requires promotion of the exact current-source 4.4.0 candidate before production activation is claimed.
- The existing `post_message` collaboration operation remains for compatibility. Governed HITL requests must use `post_interaction` or `post_approval`.
