Feature: Slack peer-HITL canonical task telemetry

  Background:
    Given TaskLedger is the canonical task authority
    And Slack provider state is the authority for message identity and human authorship
    And the dispatcher carries only provider locators

  @HITL-TELEM-001
  Scenario: Provider-confirmed root post binds the canonical task
    When a governed Slack interaction is posted for a canonical task
    And Slack returns the configured channel and a root message timestamp
    Then task.get persists slack_channel_id and slack_thread_ts

  @HITL-TELEM-002
  Scenario: Verified DONE increments a human touch
    Given human_touches is 0
    When the configured human replies DONE in the governed thread
    And the exact provider message is reread and verified as manual human input
    Then human_touches is 1

  @HITL-TELEM-003
  Scenario: Provider event replay is telemetry-idempotent
    Given a verified provider event has already been reconciled
    When the same provider event locator is reconciled again
    Then human_touches remains unchanged
    And no second bot acknowledgment is posted

  @HITL-TELEM-004
  Scenario: A second distinct verified human interaction counts once
    Given one provider-authenticated human interaction has been recorded
    When a second distinct valid human reply is reconciled in the same governed task thread
    Then human_touches increments exactly once more

  @HITL-TELEM-005
  Scenario: Bot acknowledgment is not a human touch
    When Mesh posts a same-thread bot acknowledgment
    Then the bot message does not increment human_touches

  @HITL-TELEM-006
  Scenario: Rejected provider events do not count
    When a wrong-user, app-authored, bot-authored, edited, unbound, or invalid-thread message is processed
    Then human_touches does not increment

  @HITL-TELEM-007 @authority
  Scenario: APPROVE on a nonapproval thread has no authority
    When the configured human replies APPROVE in a nonapproval governed thread
    Then the verified interaction may increment human_touches
    But approval_status remains NOT_REQUIRED
    And no approval authority is created

  @HITL-TELEM-008 @authority
  Scenario: Approval telemetry remains independent of approval authority
    Given a canonical pending approval is bound to a governed Slack thread
    When the configured human provides a strict valid approval command
    Then the verified human interaction increments human_touches once
    And approval state changes only through the existing approval authority path

  @HITL-TELEM-009
  Scenario: Telemetry never advances task lifecycle
    When Slack task telemetry is recorded
    Then task status, completion, verification, and outcome evidence do not advance

  @HITL-TELEM-010
  Scenario: task.get exposes canonical persisted telemetry
    After a verified provider-authenticated human reply is reconciled
    Then task.get returns persisted slack_channel_id
    And task.get returns persisted slack_thread_ts
    And task.get returns the persisted human_touches value
