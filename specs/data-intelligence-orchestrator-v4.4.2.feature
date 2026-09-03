@ready @data-intelligence @v4.4.2
Feature: Data Intelligence Orchestrator v4.4.2
  As Mesh Chief of Staff
  I want Data Intelligence work to be business-outcome-first, owner-correct, self-healing, and auditable
  So that prospect data remains trustworthy without hiding technical defects or weakening governance

  Scenario: DATA-442-001 Narrative prerequisites fail closed as dependencies
    Given a CRO child dependency contains narrative lock text rather than a task ID
    When the child attempts to enter IN_PROGRESS
    Then the runtime rejects the transition
    And the child remains ASSIGNED

  Scenario: DATA-442-002 Dependency-clean owner work advances
    Given a CRO child has no hard canonical predecessor
    And its dependency array is empty
    When the child advances through owner execution
    Then the child enters IN_PROGRESS

  Scenario: DATA-442-003 Real predecessor enforcement remains intact
    Given a CRO child depends on a canonical predecessor task
    And the predecessor is not VERIFIED
    When the child attempts to enter IN_PROGRESS
    Then the runtime rejects the transition
    When the predecessor becomes VERIFIED
    Then the dependent child may enter IN_PROGRESS

  Scenario: DATA-442-004 Caller action expansion is denied
    Given a caller supplies a delegation action outside the CRO registry allowlist
    When the delegation is created
    Then the runtime denies it
    And omitting caller actions causes the canonical allowlist to be inherited

  Scenario: DATA-442-005 September occurrence is recovered without false success
    Given the September 1 monthly occurrence wrote no Run Ledger lock and no prospect cell
    And its malformed CRO child is preserved and cancelled
    When one dependency-clean recovery successor completes
    Then the successor may be VERIFIED
    But the original monthly occurrence remains FAILED_OCCURRENCE_ISOLATED
    And no provider effect is replayed
    And the next logical due time is October 1 2026 at 00:01 ET

  Scenario: DATA-442-006 Business result is distinct from technical health
    Given canonical recovery is technically GREEN
    But the intended full-universe review did not occur
    Then the business outcome is not reported as successful
    And technical health is reported separately

  Scenario: DATA-442-007 Marketing context cannot overwrite Revenue Intelligence
    Given CMO receives LinkedIn Authority OS context
    When CMO prepares the executive brief
    Then the context is labeled as authority or relationship evidence
    And it cannot create account intent, budget, sponsor, lifecycle, priority, stage, or activation truth
    And Revenue Intelligence remains authoritative

  Scenario: DATA-442-008 Prospect mutation remains exact and fail-safe
    Given a prospect field is approved for internal maintenance
    When the field is changed
    Then the exact cell is pre-read
    And exactly one cell is written
    And that cell is immediately read back
    And the governed row is reconciled
    When the connector blocks or reconciliation fails
    Then later prospect writes stop
    And prior reconciled accounts remain committed
    And the lock is released

  Scenario: DATA-442-009 Scheduler state requires live provider evidence
    Given the repository and TaskLedger control plane are green
    When the external monthly wake is not enabled or cannot be read back
    Then scheduler activation is BLOCKED
    And unrelated eligible work remains green
    And production automation is not falsely claimed

  Scenario: DATA-442-010 Consequential external action remains prohibited
    Given there is no exact canonical human approval and provider reconciliation
    When the Data Intelligence loop runs
    Then it performs no outreach, publication, CRM write, pricing, scope, staffing, or commitment
