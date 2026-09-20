Feature: Bidirectional Slack HITL peer workflow
  The Slack operating surface must be clear, bot-owned, conversational, and fail-closed.

  Background:
    Given the governed Slack channel is C0BRL4GCL3A
    And Michael is provider user U01KG3CNYHK
    And TaskLedger is canonical
    And the ChatGPT Work dispatcher carries only thread and message locators

  @HITL-CHAT-001
  Scenario: Information message
    When CoS posts an INFO interaction through the governed Slack bot
    Then Slack attributes the root message to the configured bot identity
    And the message says no response is required
    And any human reply is acknowledged without authority mutation

  @HITL-CHAT-002
  Scenario: Manual action completion
    When CoS posts a MANUAL_ACTION interaction
    Then the message says no Slack approval is required
    And it tells Michael to reply DONE after the action
    When Michael replies DONE
    Then provider state is reread
    And the bot acknowledges completion in the same thread
    And verification remains a separate governed step

  @HITL-CHAT-003
  Scenario: Ordinary conversation
    Given a governed non-approval thread exists
    When Michael replies in normal language
    Then provider identity is verified
    And the bot returns bounded contextual feedback
    And no approval authority is created

  @HITL-CHAT-004
  Scenario: Explicit approval
    Given a canonical pending approval is bound to a governed Slack thread
    When Michael replies APPROVE
    Then Slack provider state is reread
    And the canonical approval is recorded
    And the bot acknowledges the resulting state in the same thread

  @HITL-CHAT-005
  Scenario Outline: Ambiguous approval language
    Given a canonical pending approval is bound to a governed Slack thread
    When Michael replies <reply>
    Then no approval mutation occurs
    And the bot requests an explicit APPROVE, DENY, or CHANGES command

    Examples:
      | reply      |
      | looks good |
      | confirmed  |
      | yes        |
      | thumbs-up  |

  @HITL-CHAT-006
  Scenario: Approval command on a non-approval thread
    Given a governed MANUAL_ACTION thread exists
    When Michael replies APPROVE
    Then no approval mutation occurs
    And the bot explains the thread is not awaiting approval

  @HITL-CHAT-007
  Scenario: Denial
    Given a canonical pending approval is bound to a governed Slack thread
    When Michael replies DENY
    Then the canonical approval is rejected
    And the bot acknowledges that no action is authorized

  @HITL-CHAT-008
  Scenario: Changes with detail
    Given a canonical pending approval is bound to a governed Slack thread
    When Michael replies CHANGES with bounded untrusted detail
    Then the prior approval is superseded
    And the detail is stored as untrusted change input
    And a new immutable approval is required before consequential action

  @HITL-CHAT-009
  Scenario: Duplicate delivery
    Given one Slack reply was already reconciled and acknowledged
    When the same provider locator is delivered again
    Then no duplicate authority or action occurs
    And no duplicate bot acknowledgment is posted

  @HITL-CHAT-010
  Scenario: Wrong Slack user
    When a different Slack user replies in a governed thread
    Then reconciliation fails closed
    And no authority mutation occurs

  @HITL-CHAT-011
  Scenario: Bot authored reply
    When an app or bot authors a reply in a governed thread
    Then it cannot become human authority
    And reconciliation fails closed

  @HITL-CHAT-012
  Scenario: Edited or unavailable provider message
    When the exact provider message is edited, deleted, missing, or ambiguous
    Then reconciliation fails closed
    And no authority mutation occurs

  @HITL-CHAT-013
  Scenario: Provider outage
    When Slack provider reread is unavailable
    Then no approval is inferred from the Work trigger
    And canonical TaskLedger state is preserved

  @HITL-CHAT-014
  Scenario: Bot identity
    When Mesh posts an operational HITL message
    Then the message is posted by the protected bot OAuth identity
    And no username or avatar override impersonates Michael

  @HITL-CHAT-015
  Scenario: Complete peer round trip
    Given a bot-owned governed interaction exists
    When Michael replies in its thread
    Then the Work dispatcher wakes with locators only
    And Mesh CoS MCP rereads Slack provider evidence
    And the server distinguishes conversation from authority
    And any permitted canonical state change occurs exactly once
    And the bot posts the resulting state in the same thread
    And TaskLedger and audit evidence agree
