@ready @security @slack @hitl @v4_2_2
Feature: ChatGPT-native Slack HITL provider transport repair
  The ChatGPT Work dispatcher is only a wake-up and locator source.
  Mesh CoS MCP must independently retrieve Slack provider evidence before human authority changes.

  Background:
    Given deployment release 4.2.2 uses canonical MCP runtime contract 4.0.0
    And the governed Slack channel is C0BRL4GCL3A
    And the configured human approver is canonical principal michael
    And the protected Slack bot credential is an xoxb token
    And the Slack bot has chat:write and groups:history for the governed private channel
    And Socket Mode is disabled

  Scenario: V422-SLACK-001 provider thread read uses GET query transport
    Given a qualifying dispatcher invocation contains only thread_ts and message_ts
    When Mesh CoS MCP retrieves the exact Slack thread reply
    Then conversations.replies is invoked with HTTP GET
    And channel, ts, oldest, latest, inclusive, and limit are sent as query parameters
    And the OAuth token is sent only in the Authorization header
    And no Slack message text from the trigger is used as authority

  Scenario: V422-SLACK-002 provider read failure is sanitized and fail closed
    Given Slack rejects a provider-read request with a provider error code
    When Mesh CoS MCP handles the Slack response
    Then the diagnostic may expose only a sanitized provider error code
    And provider response metadata is not exposed
    And no canonical approval state changes
    And no underlying consequential action executes

  Scenario: V422-SLACK-003 Slack write transport remains POST JSON
    When Mesh CoS MCP posts or updates an approval notice
    Then chat.postMessage and chat.update continue to use POST JSON
    And the dedicated Slack bot remains the collaboration identity

  Scenario: V422-SLACK-004 deployment verification proves live private-channel read access
    Given the production containers are healthy
    When the QNAP deployment verifier checks Slack provider-read readiness
    Then the running mesh-cos-mcp container uses its mounted bot credential
    And it calls conversations.history for C0BRL4GCL3A with limit 1
    And deployment verification fails if Slack returns missing_scope, invalid_auth, not_in_channel, channel_not_found, or another provider failure
    And the token value is never logged

  Scenario: V422-SLACK-005 verified Slack application identity is enforced
    When production readiness validates the dedicated Slack application
    Then MESH_COS_SLACK_APP_ID is A0B49RNE4K0
    And configuration using the incorrect prior ID A0B49RNF4K0 fails readiness

  Scenario: V422-SLACK-006 rendered bold APPROVE reaches canonical authority only after provider reread
    Given a PENDING L4 approval is bound to a governed Slack thread
    And MK manually replies with provider text *APPROVE*
    When the dispatcher passes only the exact thread and message locators
    And the QNAP runtime retrieves that exact provider message
    Then one whole-message bold wrapper is normalized
    And the exact APPROVE grammar is applied
    And provider identity and manual authorship are verified
    And the approval owner, PENDING state, payload fingerprint, and replay controls are verified
    And the approval becomes APPROVED exactly once
    And the task becomes READY_FOR_ACTION

  Scenario: V422-SLACK-007 duplicate delivery is idempotent
    Given a provider message has already created a canonical approval decision
    When the same channel, thread_ts, and message_ts are reconciled again
    Then the same canonical decision evidence is returned
    And no second decision is recorded

  Scenario Outline: V422-SLACK-008 invalid provider evidence never creates authority
    Given a PENDING governed approval
    When provider reconciliation observes <condition>
    Then the approval remains non-authoritative or unchanged as appropriate
    And no consequential action executes

    Examples:
      | condition |
      | a reply from the wrong Slack user |
      | a bot-authored reply |
      | an edited reply |
      | a root message rather than a thread reply |
      | an unbound thread |
      | a missing or unavailable exact provider message |
      | payload fingerprint drift |
      | nested decision formatting |
      | partial decision formatting |
      | unknown decision text |
