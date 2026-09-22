Feature: Commercial Growth OS delegated-owner recovery v4.13.4
  Commercial work uses canonical server-derived ownership and recovers from stale caller compatibility assertions without duplicating work or widening authority.

  @COM-DEL-001 @delegation @security
  Scenario: Direct CRO delegation uses server-derived ownership
    Given CoS owns a canonical commercial parent
    And a nonterminal direct child is canonically owned by CRO
    When CoS creates the delegation with the canonical work contract only
    Then the server derives parent authority, depth, ancestry, and active owner
    And the owner execution route identifies CRO as the executing principal
    And CoS remains the orchestrating parent
    And no authority is widened

  @COM-DEL-002 @regression
  Scenario: Incorrect caller active owner fails closed
    Given a canonical CRO-owned commercial child
    When the caller supplies active_owner as cos
    Then delegation creation fails with ownership-conflict
    And no delegation record is persisted
    And canonical child ownership remains CRO

  @COM-DEL-003 @recovery
  Scenario: Pre-persistence ownership assertion failure recovers on the same work graph
    Given a commercial parent is blocked only by a pre-persistence caller ownership assertion
    And the CRO child remains nonterminal
    And no delegation record or provider side effect exists
    When CoS rereads canonical parent and child state
    And retries the same delegation ID and work contract once without parent_authority, depth, ancestry, or active_owner
    Then the delegation is persisted for CRO
    And the same blocked parent resumes to IN_PROGRESS
    And the same child continues through delegation.execute_owner
    And no duplicate parent, child, delegation, commercial action, or external effect is created

  @COM-DEL-004 @security
  Scenario: Canonical owner mismatch is not repaired by reassignment
    Given the canonical child owner differs from the requested delegation owner
    When delegation creation is attempted
    Then the request fails closed
    And recovery does not reassign the child or substitute another principal

  @COM-DEL-005 @capabilities
  Scenario: CRO capability handoffs preserve commercial source authority
    Given a valid CRO delegation grants the literal registered capabilities needed for the occurrence
    When CRO invokes mesh-revenue-intelligence and mesh-gtm-orchestrator through delegation.execute_owner
    Then the execution principal is CRO
    And each Skill result is an authorization handoff with provenance required
    And Revenue Intelligence remains canonical commercial truth
    And external action remains unauthorized
