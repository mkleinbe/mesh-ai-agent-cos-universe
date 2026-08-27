# Changelog v4.2.2

## Fixed

- Correct Slack provider reconciliation for ChatGPT-native HITL by sending `conversations.replies` as an authenticated GET with query parameters instead of the generic POST/JSON transport that Slack rejected with `invalid_arguments`.
- Preserve existing POST/JSON behavior for Slack write methods such as `chat.postMessage` and `chat.update`.
- Preserve only a sanitized Slack provider error code in runtime exceptions, preventing response metadata or credential-bearing request detail from entering diagnostics.
- Correct the production Slack App ID from `A0B49RNF4K0` to the provider-verified `A0B49RNE4K0` across runtime readiness, production preflight, QNAP environment generation, examples, and tests.
- Add a live QNAP deployment verification gate that proves the installed `xoxb-` bot can read `#mesh-agent-ops` before production acceptance begins. This catches missing `groups:history`, stale OAuth grants, invalid credentials, and channel-access failures earlier.

## Preserved

- Canonical MCP runtime contract remains `4.0.0`.
- Public governed MCP tool catalog remains unchanged.
- The single ChatGPT Work `Mesh Slack HITL Dispatcher` remains locator-only and non-authoritative.
- The dispatcher should remain version-family labeled `Mesh CoS MCP v4.x`; no patch-specific prompt or trigger change is required.
- Provider-retrieved Slack decision parsing remains the v4.2.1 strict grammar with one whole-message bold-wrapper compatibility rule.
- Human identity, channel/thread binding, edit-state, PENDING approval, owner, immutable fingerprint, replay/idempotency, and TaskLedger authority checks remain fail closed.
- No Socket Mode, `xapp-` credential, polling loop, or alternate approval path is introduced.

## Production incident evidence

The v4.2.1 production incident was reproduced with the same bot credential and exact message locators:

- GET/query to `conversations.replies` returned `ok:true` and the exact MK `*APPROVE*` reply.
- v4.2.1 POST/JSON to `conversations.replies` returned `invalid_arguments` with Slack reporting that required fields `channel` and `ts` were missing.
- Direct Python reconciliation therefore failed in `_default_transport` before decision parsing and left the canonical approval PENDING.

This evidence is the regression contract for v4.2.2.
