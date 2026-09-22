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

## Delegated commercial execution

For non-CoS commercial-family work, create or reuse one canonical direct CRO child and one deterministic delegation under the CoS parent.

Call `delegation.create` with the delegation work contract only. Do not calculate, populate, or infer `parent_authority`, `depth`, `ancestry`, or `active_owner`. The server derives those values from TaskLedger and the Agent Registry. Never send `active_owner=cos` for a CRO-owned child.

When the selected occurrence requires bounded capability access, `permitted_capabilities` may contain only literal capabilities currently registered for CRO. For canonical commercial qualification and motion selection, the permitted subset may include `mesh-revenue-intelligence` and `mesh-gtm-orchestrator`. Omit caller `permitted_actions` unless every requested action is a literal CRO registry action.

Advance the CRO child, invoke governed Skills, check in, and complete only through `delegation.execute_owner`. Confirm the response identifies `executing_principal=cro` and `orchestrating_agent=cos`. Skill invocation is an authorization handoff with result provenance required and does not by itself establish Revenue Intelligence truth or complete the task.

## Event execution

Only classify a run as EVENT_TRIGGERED when a supported provider delivers a native event with verified provider binding and a stable event identifier. A recurring poll, even a condition watch, is scheduled polling and must not be labeled event driven.

Do not move buyer-response approvals, sends, Slack HITL, pricing, partner commitments, or public actions into the scheduler. Preserve existing provider and human gates.

## Recovery

Retries reuse the original logical occurrence and idempotency key. Do not create a second review or repeat a provider side effect. A source or execution-integrity problem is SYSTEM_FAILURE, not business progress.

If `delegation.create` returns `ownership-conflict` or `invalid-delegation-contract`, re-read the canonical parent, child, and existing delegation record before mutation. Recovery is allowed only when the intended child is still canonically CRO-owned, the parent remains CoS-owned, the deterministic delegation ID is not bound to different work, the child remains nonterminal, and no provider or external side effect occurred.

If the rejected request included caller-derived compatibility assertions, retry the same delegation ID and work contract exactly once with `parent_authority`, `depth`, `ancestry`, and `active_owner` omitted. Do not reassign the child or substitute another identity to make the retry pass.

When the parent is `BLOCKED` solely by the pre-persistence delegation failure and the corrected delegation succeeds, reuse the same work graph and resume the parent through `BLOCKED -> IN_PROGRESS`. Continue the existing child through `delegation.execute_owner`. Do not create a replacement parent, duplicate child, second delegation ID, duplicate commercial action, or repeated external effect.

If canonical ownership is inconsistent, side-effect state is ambiguous, the delegation ID is bound to different work, or the single corrected retry fails, preserve the current work graph and isolate the affected scope as SYSTEM_FAILURE for governed remediation.
