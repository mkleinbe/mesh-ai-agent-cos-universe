Feature: Commercial Growth OS canonical cadence v4.12.0
  The existing Commercial Operations control plane absorbs Commercial Growth cadence without creating a parallel scheduler.

  Scenario: LOOP-COM-001 remains the canonical scheduled dispatcher
    Given scheduled commercial work is evaluated
    When the dispatcher wakes
    Then TaskLedger remains canonical operating state
    And LOOP-COM-001 is the single scheduled Commercial Growth OS dispatcher

  Scenario: Scheduler wake is not business progress
    Given a technically healthy dispatcher wake
    And no commercial review or action is due
    When the checkpoint is classified
    Then the result is RESPONSIBLE_NO_ACTION
    And it is not BUSINESS_PROGRESS

  Scenario: Monthly review is logical due work
    Given the first eligible weekday of a month has arrived
    When LOOP-COM-001 evaluates due work
    Then exactly one MONTHLY review is due until completed

  Scenario: Quarterly review subsumes colliding monthly review
    Given the first eligible weekday of a quarter has arrived
    And the monthly and quarterly review are both due
    When LOOP-COM-001 evaluates due work
    Then exactly one QUARTERLY review is dispatched
    And the same completion satisfies the monthly period key

  Scenario: Scheduled retry is idempotent
    Given an existing logical commercial occurrence
    When LOOP-COM-001 retries the same occurrence
    Then the idempotency key is unchanged
    And duplicate canonical work is not created

  Scenario: Native event is distinct from scheduled polling
    Given a provider-bound native event with a stable event identifier
    When Commercial Growth OS is invoked as EVENT_TRIGGERED
    Then the trigger class is NATIVE_EVENT
    And the same commercial decision rules apply

  Scenario: Polling cannot claim event-triggered compliance
    Given native event delivery is unavailable
    When a time-based poll evaluates the source
    Then it is not classified as a native event
    And the limitation is explicit

  Scenario: Existing HITL event authority is preserved
    Given a buyer-response or external-action event reaches an approval boundary
    When action would become consequential
    Then LOOP-COM-HITL-001 retains provider-bound authority
    And scheduled cadence cannot bypass it

  Scenario: Fresh prior evidence is reused
    Given verified fresh Revenue Intelligence evidence already exists
    When a monthly or quarterly review is due
    Then the review reuses that evidence before deeper research

  Scenario: Four business states remain operator facing
    Given a commercial checkpoint completes evaluation
    When Chief of Staff reports it
    Then it leads with BUSINESS_PROGRESS, RESPONSIBLE_NO_ACTION, BUSINESS_FAILURE, or SYSTEM_FAILURE

  Scenario: Completion remains distinct from verification
    Given a commercial occurrence is completed
    When acceptance evidence is assessed
    Then completion does not imply verification

  Scenario: Phase 1 authority remains unchanged
    Given the cadence remediation is active
    When agent and authority state is checked
    Then exactly 10 Phase 1 agents remain registered
    And Revenue Intelligence remains canonical commercial truth
    And mesh-gtm-orchestrator remains the commercial-family front door
