# Commercial Growth OS Operating Cadence v4.12.0

## Canonical control plane

`TaskLedger` remains canonical operating state. `LOOP-COM-001` is the single scheduled Commercial Growth OS dispatcher. Scheduler state, spreadsheets, provider queues, and ChatGPT automation metadata are mirrors or trigger surfaces, not competing commercial control planes.

The central wake cadence remains weekdays at 08:00, 10:00, 12:00, and 16:00 America/New_York. A wake is only an eligibility check. It is never itself business progress.

## Invocation equivalence

Ad hoc, scheduled, and genuinely event-triggered work use the same commercial decision rules and the same Revenue Intelligence, `mesh-gtm-orchestrator`, authority, Product Independence, Message Operations, and approval boundaries.

- **AD_HOC**: operator starts the run.
- **SCHEDULED**: `LOOP-COM-001` wakes and evaluates only logically due work.
- **EVENT_TRIGGERED**: a supported provider delivers a native event with provider-bound identity and a stable event identifier.

A time-based poll is not an event trigger. If native event delivery is unavailable for a source, document the limitation and use scheduled eligibility without claiming event-driven compliance.

`LOOP-COM-HITL-001` remains separate for provider-bound approval/external-action paths. Do not weaken, replace, or poll around its controls.

## Delegated commercial execution

When CoS routes non-CoS commercial-family work to CRO, reuse one canonical CoS parent, one deterministic CRO child, and one deterministic delegation for the logical occurrence.

Call `delegation.create` with the canonical delegation body only. Do not calculate, populate, or infer the outer compatibility assertions `parent_authority`, `depth`, `ancestry`, or `active_owner`. The Mesh CoS server derives them from TaskLedger and the Agent Registry. In particular, never send `active_owner=cos` for a CRO-owned child.

Use `permitted_capabilities` only as an explicit literal subset of the CRO registry when the occurrence requires bounded capability access, such as `mesh-revenue-intelligence` and `mesh-gtm-orchestrator`. Omit caller `permitted_actions` unless every requested action is an exact subset of the CRO registry.

All CRO-owned child lifecycle, check-in, governed Skill handoff, and completion operations execute through `delegation.execute_owner`, which derives `cro` server-side. CoS remains the parent orchestrator and performs separate verification. A Skill authorization handoff does not itself establish commercial truth or satisfy the child acceptance test.

## Bounded delegation recovery

If `delegation.create` returns `ownership-conflict` or `invalid-delegation-contract`, first re-read the existing canonical parent and child. Confirm the child `accountable_agent` is CRO, the parent remains CoS-owned, the deterministic delegation ID is not bound to different work, and no provider or external side effect occurred.

When the rejected request contained caller-derived compatibility assertions, retry the same delegation ID, parent, child, owner, authority, and work contract exactly once with `parent_authority`, `depth`, `ancestry`, and `active_owner` omitted. Never reassign the child or substitute another principal to make the retry pass.

If the same parent is `BLOCKED` solely because of that pre-persistence delegation failure, the child remains nonterminal, and the corrected delegation succeeds, reuse the existing work graph. Resume the parent through `BLOCKED -> IN_PROGRESS` and continue the existing child through `delegation.execute_owner`. Do not create a replacement parent, duplicate child, second delegation ID, or duplicate commercial action.

If canonical ownership is actually inconsistent, the delegation ID is bound to different work, the single corrected retry fails, or side-effect state is ambiguous, preserve the existing work graph and classify the affected scope as `SYSTEM_FAILURE`.

## Monthly and quarterly reviews

Monthly and quarterly reviews are logical due work inside `LOOP-COM-001`, not separate schedulers.

- Monthly review becomes due on the first weekday of the month and remains due until its period key is completed.
- Quarterly review becomes due on the first weekday of January, April, July, and October and remains due until its quarter key is completed.
- When a quarterly review is due, it subsumes the same run's monthly review. One evidence load, one decision packet, and one completion can satisfy both period keys.
- Reuse verified fresh prior evidence before new research. Escalate research depth only when a material decision cannot be made from current evidence.
- A retry uses the same logical occurrence key. Duplicate execution must converge on the same canonical work rather than creating a second review.

## Business-state reporting

Every evaluated checkpoint leads with exactly one:

- `BUSINESS_PROGRESS`
- `RESPONSIBLE_NO_ACTION`
- `BUSINESS_FAILURE`
- `SYSTEM_FAILURE`

A technically healthy wake with no due work is `RESPONSIBLE_NO_ACTION`, not `BUSINESS_PROGRESS`. A source, provider, authorization, freshness, or execution-integrity failure is `SYSTEM_FAILURE`. A material commercial regression is `BUSINESS_FAILURE`.

## Evidence and outcomes

Revenue Intelligence owns canonical commercial, account, relationship, partner, and outcome evidence. Reuse current evidence across daily, monthly, and quarterly checkpoints to avoid duplicate research. Record observed AI/tool cost and research effort only when available. Never invent token, cost, outcome, intent, urgency, or economic values.

## External action

A cadence result may recommend or prepare work. Consequential external action still requires its existing provider-bound approval path and Message Operations. Completion and verification remain separate.
