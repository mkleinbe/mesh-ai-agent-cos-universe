@ready @odd @marketing
Feature: Outcome-driven scheduled marketing orchestration

  Scenario: ODD-001 actionable evidence creates owned internal work
    Given a due marketing checkpoint with mature evidence supporting a bounded internal intervention
    When the accountable marketing owner evaluates the checkpoint
    Then the result is an outcome decision
    And one owned internal next action is created or advanced within existing authority
    And public external action remains human-gated

  Scenario: ODD-002 no action is a valid decision
    Given a due checkpoint whose decision rule does not justify intervention
    When the checkpoint is evaluated
    Then the outcome decision is NO_ACTION_WARRANTED
    And no filler action is created

  Scenario: ODD-003 evidence pending is not business success
    Given a governed intervention has been created
    And its evidence window has not matured
    When the checkpoint is reported
    Then the outcome decision is ACTION_TAKEN_EVIDENCE_PENDING
    And evidence_matures_at and next_measurement_at are recorded
    And technical health is reported separately

  Scenario: ODD-004 runtime health does not become marketing progress
    Given a runtime-health-only job completes successfully
    When executive reporting is produced
    Then business movement is NOT_EVALUATED
    And technical health may be GREEN
    And business GREEN or ADVANCE is not manufactured

  Scenario: ODD-005 AI effort escalates progressively
    Given a scheduler wake begins
    When eligibility can be decided from bounded canonical state
    Then T0_WAKE_SCAN is used first
    And deeper evidence or diagnostics are loaded only when a due job requires them

  Scenario: ODD-006 repeated instrumentation gaps create remediation
    Given the same evidence gap blocks two comparable business checkpoints
    When the second checkpoint is evaluated
    Then an owned instrumentation-remediation action is recommended or routed
