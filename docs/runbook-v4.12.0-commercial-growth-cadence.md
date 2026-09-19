# Runbook v4.12.0: Commercial Growth Cadence

## Preflight

1. Verify exactly 10 ACTIVE Phase 1 agents and a valid governance audit chain.
2. Read `LOOP-COM-001` from TaskLedger and confirm it is the canonical commercial scheduled dispatcher.
3. Read the scheduler mirror and confirm weekdays 08:00, 10:00, 12:00, and 16:00 America/New_York.
4. Read `LOOP-COM-HITL-001` and confirm its provider-bound approval path is unchanged.
5. Reuse fresh Revenue Intelligence evidence before requesting broader research.

## Scheduled execution

At each wake, evaluate only logical due work. If nothing is due, return RESPONSIBLE_NO_ACTION. Do not report the wake as progress.

For monthly and quarterly periods, use deterministic period keys. When a quarterly review and monthly review collide, execute one quarterly review and mark both period keys complete only after the review itself completes. Verification remains separate.

## Event execution

Only classify a run as EVENT_TRIGGERED when a supported provider delivers a native event with verified provider binding and a stable event identifier. A recurring poll, even a condition watch, is scheduled polling and must not be labeled event driven.

Do not move buyer-response approvals, sends, Slack HITL, pricing, partner commitments, or public actions into the scheduler. Preserve existing provider and human gates.

## Recovery

Retries reuse the original logical occurrence and idempotency key. Do not create a second review or repeat a provider side effect. A source or execution-integrity problem is SYSTEM_FAILURE, not business progress.
