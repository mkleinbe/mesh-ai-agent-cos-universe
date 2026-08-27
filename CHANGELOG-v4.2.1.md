# Changelog v4.2.1

## 4.2.1 - 2026-08-27 - Native Slack HITL Rendered Decision Compatibility

### Production acceptance defect remediation

- Reproduced the first live v4.2.0 ChatGPT Work HITL acceptance failure: the Slack event-triggered dispatcher fired and reached Mesh CoS MCP, but server reconciliation failed closed with `INVALID_ARGUMENT / execution_failed`.
- Confirmed Slack provider evidence returned the exact human reply as `*APPROVE*` while the v4.2.0 parser accepted only the bare `APPROVE` token.
- Preserved the correct fail-closed outcome: the canonical approval remained PENDING and no underlying consequential action executed.

### Causal correction

- Added a narrowly scoped provider-text normalization that removes exactly one whole-message Slack `*...*` wrapper before applying the existing exact APPROVE / DENY / CHANGE grammar.
- Added acceptance for provider forms `*APPROVE*`, `*DENY*`, `*CHANGE*`, and `*CHANGES: <detail>*`.
- Kept nested, partial, unknown, and natural-language variants such as `**APPROVE**`, `*APPROVE* extra`, `*looks good*`, and `please APPROVE` fail closed.
- Kept identity, manual-human authorship, channel/thread binding, edited-message rejection, immutable payload fingerprint, PENDING-state, owner, replay/idempotency, and TaskLedger authority checks unchanged.

### Dispatcher and QNAP operations

- Kept the existing single **Mesh Slack HITL Dispatcher** trigger unchanged: Slack, `#mesh-agent-ops`, author MK, `New messages and thread replies`.
- Kept the dispatcher locator-only. It still passes only `thread_ts` and `message_ts` and never interprets or forwards Slack decision text.
- Required only a prompt release-label update from `v4.2.0` to `v4.2.1` after QNAP deployment.
- Removed stale deployment completion guidance referring to `/mesh-approval Socket Mode ingress` and replaced it with the ChatGPT-native dispatcher acceptance instruction.
- Kept the Slack bot manifest scope set unchanged at `chat:write` and `groups:history`; no `xapp-` credential, Socket Mode listener, new OAuth scope, or Slack reauthorization is introduced.

### BDD, TDD, security, documentation, and release engineering

- Added ready scenarios `SLACK-NATIVE-421-001` through `SLACK-NATIVE-421-008` covering locator-only ingress, rendered decision forms, narrow formatting rejection, identity/state controls, replay, CHANGE, Socket Mode exclusion, and exact production incident replay.
- Added RED/regression tests at the decision parser and native provider-reconciliation layers.
- Classified security applicability as **FULL REVIEW** because parsing changes immediately precede canonical human approval mutation.
- Added v4.2.1 release, security, dispatcher, QNAP acceptance, and published-app production acceptance documentation.
- Added and validated Mermaid authority-flow, trust-boundary, and production-acceptance sequence diagrams using Mermaid Chart.
- Added the exact v4.2.1 QNAP bundle/checksum builder, current CI release gates, and immutable GitHub release workflow; retired v4.2.0 automatic publishing while preserving it as historical/manual evidence.

### Authority boundary

- Canonical Phase 1 authority/runtime contract remains `4.0.0`.
- Exactly 10 registered agents and 27 governed public CoS tools remain unchanged.
- Human-only operations remain human-only.
- OpenAI Secure MCP Tunnel remains the only remote MCP ingress.
- TaskLedger remains canonical approval state and `COMPLETED != VERIFIED` semantics remain unchanged.
