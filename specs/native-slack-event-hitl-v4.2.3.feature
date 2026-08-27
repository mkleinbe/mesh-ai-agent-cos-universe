@ready @security @slack @hitl @qnap @v4_2_3
Feature: ChatGPT-native Slack HITL qnet egress readiness
  The ChatGPT Work dispatcher is only a wake-up and locator source.
  Mesh CoS MCP must independently retrieve Slack provider evidence before human authority changes.
  QNAP deployment must tolerate only bounded pre-provider network readiness failures.

  Background:
    Given deployment release 4.2.3 uses canonical MCP runtime contract 4.0.0
    And the governed Slack channel is C0BRL4GCL3A
    And the configured human approver is canonical principal michael
    And the protected Slack bot credential is an xoxb token
    And the Slack bot has chat:write and groups:history for the governed private channel
    And Socket Mode is disabled

  Scenario: V423-SLACK-001 provider thread read retains GET query transport
    Given a qualifying dispatcher invocation contains only thread_ts and message_ts
    When Mesh CoS MCP retrieves the exact Slack thread reply
    Then conversations.replies is invoked with HTTP GET
    And channel, ts, oldest, latest, inclusive, and limit are sent as query parameters
    And the OAuth token is sent only in the Authorization header
    And no Slack message text from the trigger is used as authority

  Scenario: V423-SLACK-002 deployment provider read retries a network exception only
    Given the freshly recreated mesh-cos-mcp container is locally healthy
    And its qnet namespace has not yet established external Slack egress
    When conversations.history raises a network exception before any provider response
    Then deployment verification retries the provider read
    And no more than six total attempts are made
    And retries wait five seconds between attempts
    And no approval authority is created by the retry

  Scenario: V423-SLACK-003 provider authorization failure does not retry
    Given Slack returns an ok false provider response
    When the QNAP deployment verifier evaluates that response
    Then verification fails immediately
    And only a sanitized provider error code may be logged
    And provider response metadata is not exposed
    And no retry converts the provider failure into success

  Scenario: V423-SLACK-004 malformed provider response does not retry
    Given Slack returns a response that cannot be parsed as the expected provider JSON
    When the QNAP deployment verifier evaluates that response
    Then verification fails immediately with a sanitized invalid_response classification
    And no approval authority changes

  Scenario: V423-SLACK-005 exhausted qnet readiness rolls back
    Given all six Slack provider fetch attempts fail before a provider response is obtained
    When the bounded readiness window is exhausted
    Then post-deploy verification fails
    And transactional deployment rollback restores the previously active release
    And no consequential action executes

  Scenario: V423-SLACK-006 stable network namespace proves image and credential validity
    Given the exact v4.2.3 candidate image uses the protected Slack bot token
    And it shares an already-stable mesh-cos-mcp network namespace
    When it calls conversations.history for C0BRL4GCL3A
    Then Slack returns ok true
    And the result distinguishes qnet readiness from image, token, scope, membership, or API-contract defects

  Scenario: V423-SLACK-007 verified Slack application identity remains enforced
    When production readiness validates the dedicated Slack application
    Then MESH_COS_SLACK_APP_ID is A0B49RNE4K0
    And configuration using the incorrect prior ID A0B49RNF4K0 fails readiness

  Scenario: V423-SLACK-008 rendered bold APPROVE reaches canonical authority only after provider reread
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

  Scenario: V423-SLACK-009 duplicate delivery is idempotent
    Given a provider message has already created a canonical approval decision
    When the same channel, thread_ts, and message_ts are reconciled again
    Then the same canonical decision evidence is returned
    And no second decision is recorded

  Scenario Outline: V423-SLACK-010 invalid provider evidence never creates authority
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
