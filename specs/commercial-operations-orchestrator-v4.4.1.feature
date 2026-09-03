Feature: Commercial Operations orchestration correction v4.4.1

  Background:
    Given the current approved Mesh CoS MCP runtime is healthy
    And the canonical registry contains exactly 10 ACTIVE agents
    And the audit chain is valid
    And QNAP deployment release 4.4.0 remains unchanged

  Scenario: Narrative prerequisites are not canonical task dependencies
    Given a commercial child needs current authoritative evidence
    When the dispatcher constructs the child work package
    Then TaskRecord.dependencies contains only real canonical predecessor task IDs
    And source requirements and evidence labels are stored outside the dependency array
    And the child is not blocked by a descriptive dependency label

  Scenario: A real predecessor task remains fail closed
    Given a commercial child has a real canonical predecessor task ID
    And the predecessor is not verified
    When the child attempts to enter IN_PROGRESS
    Then execution remains blocked
    And the dependency gate is not weakened

  Scenario: Legacy malformed work is recovered once without replay
    Given a legacy child is blocked by narrative dependency metadata
    And no external provider effect needs replay
    When CoS performs bounded recovery
    Then the malformed child and its audit history are preserved
    And exactly one dependency-clean successor is used under the same parent and owner boundary
    And no provider side effect is replayed

  Scenario: Business block can coexist with technical green
    Given the canonical runtime, registry, audit, and connectors needed by the job are healthy
    And Revenue Intelligence evidence is insufficient for activation
    When the occurrence is evaluated correctly
    Then the business disposition is BUSINESS_BLOCKED or NOT_TRIGGERED
    And the technical health may remain GREEN
    And unrelated jobs are not downgraded

  Scenario: CMO and VP Content participate without commercial-truth transfer
    Given a commercial operating-model task requires authority and content context
    When CoS delegates to CMO and CMO delegates bounded production to VP Content
    Then owner execution follows canonical parentage
    And LinkedIn Authority OS evidence is context only
    And Revenue Intelligence remains sole account-level commercial-truth authority
    And public action remains human-gated

  Scenario: Scheduler configuration matches TaskLedger
    Given LOOP-COM-001 is ACTIVE in the TaskLedger operating-loop registry
    When live scheduler configuration is reconciled
    Then Commercial Operations Orchestrator is enabled
    And it wakes weekdays at 08:00, 10:00, 12:00, and 16:00 America/New_York
    And COM-EMAIL-SEND-DLY-001 remains event-driven rather than polled
