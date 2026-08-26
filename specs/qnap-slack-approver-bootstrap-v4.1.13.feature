@ready
Feature: QNAP Slack approver identity bootstrap without interactive user-ID entry

  Background:
    Given the canonical QNAP application root is "/share/Docker/cos-mcp"
    And the canonical release execution root is "/share/Docker/cos-mcp/releases"
    And the governed human approval principal is Michael/MK
    And the verified Slack user ID for Michael/MK is "U01KG3CNYHK"
    And Slack conversation IDs such as "D01K4CL2F8F" are not Slack user IDs

  Scenario: QNAP-092 bootstrap the governed approver identity non-interactively
    Given the protected Slack approver identity file does not exist
    When the Slack HITL configuration stage runs
    Then it writes "U01KG3CNYHK" to the protected approver identity file
    And it does not prompt the operator for a Slack user ID

  Scenario: QNAP-093 reject a Slack DM or conversation ID as an approver principal
    Given an approver identity override begins with "D"
    When the Slack HITL configuration stage validates that override
    Then configuration fails closed
    And the diagnostic explains that a Slack conversation or DM channel ID is not a user ID

  Scenario: QNAP-094 accept only Slack user-principal identifiers
    Given an approver identity override is provided
    When the Slack HITL configuration stage validates that override
    Then only identifiers beginning with "U" or "W" and containing Slack identifier characters are accepted

  Scenario: QNAP-095 preserve an existing valid protected approver identity
    Given the protected approver identity file already contains a valid Slack user ID
    And forced Slack HITL reconfiguration is not requested
    When the Slack HITL configuration stage runs
    Then the existing protected approver identity is preserved
    And no approver identity prompt occurs

  Scenario: QNAP-096 forced Slack HITL reconfiguration remains non-interactive for approver identity
    Given forced Slack HITL reconfiguration is requested
    When the Slack HITL configuration stage runs
    Then the governed Slack user ID "U01KG3CNYHK" is restaged
    And no approver identity prompt occurs

  Scenario: QNAP-097 secret Slack credentials remain outside the release artifact
    Given the QNAP release bundle is built
    Then the Slack verifier bot token is not embedded in the bundle
    And the Slack Socket Mode app token is not embedded in the bundle
    And those credentials remain protected runtime inputs or preserved protected files

  Scenario: QNAP-098 release path and authority boundaries remain unchanged
    Given v4.1.13 is deployed
    Then the operator continues to work from "/share/Docker/cos-mcp/releases"
    And the canonical SQLite TaskLedger remains under "/share/Docker/cos-mcp/state"
    And the Phase 1 authority/runtime contract remains "4.0.0"
    And exactly 10 agents and 27 governed CoS tools remain in force

  Scenario: QNAP-099 completion and verification remain separate
    Given a governed task reaches COMPLETED
    Then it is not treated as VERIFIED until the verification transition succeeds
