@ready @qnap @slack @security @v4_1_18
Feature: QNAP Slack bot credential runtime ownership hotfix

  Background:
    Given Mesh CoS MCP runs on QNAP as UID 65532 and GID 65532
    And Slack HITL requires a protected xoxb bot OAuth token
    And protected Slack credentials are mode 0400

  @QNAP-129 @priority-critical @security @happy-path
  Scenario: Newly provisioned bot token is readable only by the runtime identity
    Given the Slack bot OAuth token is provisioned by a root deployment process
    When the constrained secret-permission helper normalizes governed secrets
    Then slack-bot-token is owned by UID 65532 and GID 65532
    And slack-bot-token remains mode 0400
    And canonical runtime preflight can read the xoxb credential
    And the credential value is never logged

  @QNAP-130 @priority-critical @security @regression
  Scenario: Existing bot token is repaired during normal deployment
    Given a valid slack-bot-token already exists with root ownership from v4.1.17 provisioning
    When v4.1.18 prepare or Slack HITL configuration applies secret permissions
    Then slack-bot-token ownership is normalized to UID 65532 and GID 65532
    And normal deployment can continue without re-entering the token
