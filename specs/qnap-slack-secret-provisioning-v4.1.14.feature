Feature: QNAP protected Slack credential deployment behavior

  Background:
    Given the canonical Phase 1 authority/runtime contract remains 4.0.0
    And the governed Slack human approver is U01KG3CNYHK

  Scenario: Upgrade preserves existing protected credentials without terminal interaction
    Given valid verifier and Socket Mode credential files already exist
    When the v4.1.14 Slack HITL configurator runs from the deployment path
    Then it validates and preserves both protected credential files
    And it does not prompt for a credential
    And it does not require stty
    And no protected value is logged

  Scenario: Missing verifier credential fails closed
    Given the verifier credential file is missing
    When the v4.1.14 Slack HITL configurator runs
    Then deployment fails before candidate promotion
    And the error directs the operator to mesh-cos-slack-hitl-provision.sh
    And the error is not stty is required for hidden secret input

  Scenario: Explicit first-time provisioning requires safe no-echo input
    Given a protected Slack credential is missing
    When the operator runs mesh-cos-slack-hitl-provision.sh
    Then the credential is read from the controlling TTY without echo
    And it is not placed in argv or logs
    And it is written only to the canonical protected runtime file
    And provisioning fails closed if terminal echo cannot be disabled safely

  Scenario: Slack conversation ID cannot become human approver
    Given a Slack identifier beginning with D
    When it is evaluated as the human approver principal
    Then configuration fails
    And the governed U or W user-principal requirement remains intact
