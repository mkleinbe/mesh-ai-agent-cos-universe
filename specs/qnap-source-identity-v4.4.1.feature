Feature: QNAP deployment source identity is exact and non-ambiguous

  Scenario: Distinct deployment patch artifact
    Given QNAP deployment release 4.4.1
    Then the archive and extracted release directory are versioned 4.4.1
    And they cannot be confused with the prior 4.4.0 artifact

  Scenario: Candidate image is source-bound
    Given release metadata contains an exact Git commit
    When the QNAP candidate image is prepared
    Then its tag includes the deployment release and source commit prefix
    And its OCI revision label equals the full source commit

  Scenario: Candidate runtime is recreated
    When the deployment activates the candidate stack
    Then Compose forces container recreation

  Scenario: Stale runtime fails verification
    Given active release metadata differs from the running image revision or governed MCP source_commit
    When post-deploy verification runs
    Then verification fails
    And promotion cannot commit

  Scenario: Exact runtime passes
    Given release metadata, OCI revision, and governed MCP source_commit equal the authorized commit
    When post-deploy verification runs
    Then the source identity gate passes
