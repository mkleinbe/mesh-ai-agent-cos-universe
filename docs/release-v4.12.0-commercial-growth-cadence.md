# Mesh CoS v4.12.0 Commercial Growth Cadence

## Outcome

v4.12.0 integrates monthly, quarterly, scheduled, ad hoc, and supported native-event Commercial Growth execution into the existing TaskLedger-controlled Commercial Operations model without creating a second scheduler, commercial source of truth, or principal agent.

## Behavior

- `LOOP-COM-001` remains the single scheduled commercial dispatcher.
- The weekday 08:00, 10:00, 12:00, and 16:00 America/New_York schedule remains the wake cadence.
- A scheduler wake is only an eligibility check and never counts as business progress.
- Monthly reviews are logical due work on the first eligible weekday of each month.
- Quarterly reviews are logical due work on the first eligible weekday of January, April, July, and October.
- A due quarterly review subsumes the colliding monthly review and completes both period keys from one evidence load.
- Retries are idempotent by logical occurrence.
- Fresh verified prior evidence is reused before deeper research.
- A time-based poll is never represented as a native event trigger.
- Native events require actual event delivery, provider-bound identity, and a stable event identifier.
- `LOOP-COM-HITL-001` remains unchanged for provider-bound approval and consequential external action.
- BUSINESS_PROGRESS, RESPONSIBLE_NO_ACTION, BUSINESS_FAILURE, and SYSTEM_FAILURE remain the operator-facing business states.
- Completion remains distinct from verification.

## Authority

Revenue Intelligence remains canonical commercial truth. `mesh-gtm-orchestrator` remains the sole commercial-family front door. CRO, CFO, COO, Buyer Psychology, Message Operations, and qualified-human boundaries are unchanged. Phase 1 remains exactly 10 agents.

## Compatibility

This is a backward-compatible MINOR operating-model release. The canonical Phase 1 runtime authority contract remains 4.0.0 and production QNAP remains 4.4.0. No MCP tool, runtime identity, database schema, credential, provider permission, or external-action authority changes.
