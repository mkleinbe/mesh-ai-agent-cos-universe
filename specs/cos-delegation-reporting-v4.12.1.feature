Feature: Governed CoS delegation and agent reporting round trip

  The CoS delegates bounded work without impersonating the receiving agent.
  TaskLedger remains canonical, Skills remain capabilities rather than principals,
  parent acceptance stays separate, and L4/L5 actions remain human gated.

  Scenario: CDR-001 CoS delegates L2 work to CRO
    Given CoS owns a valid parent task
    And CRO is ACTIVE and registered directly under CoS
    When CoS creates a bounded L2 delegation
    Then the delegation is persisted for CRO
    And server-derived owner execution identifies CRO as the executing principal
    And CoS remains the orchestrating parent

  Scenario: CDR-002 Derived delegation assertions are not required client authority inputs
    Given canonical TaskLedger and registry state already determine parent authority, depth, ancestry, and owner
    When CoS creates a delegation without caller parent_authority or depth assertions
    Then the request is valid
    And omitted compatibility assertions cannot create authority

  Scenario: CDR-003 Caller delegation assertions cannot override canonical authority
    Given a valid delegated child
    When a caller supplies a conflicting authority, depth, ancestry, or active owner assertion
    Then delegation fails closed
    And a stable machine-readable reason code identifies the failure class
    And no partial ownership mutation occurs

  Scenario: CDR-004 Invalid target fails deterministically
    Given a canonical child task
    When CoS attempts to delegate it to an unauthorized or mismatched recipient
    Then the delegation is rejected
    And the error identifies recipient or ownership failure
    And TaskLedger ownership remains unchanged

  Scenario: CDR-005 CRO starts and checks in as CRO
    Given a valid CRO delegation
    When CoS invokes the server-owned owner execution route
    Then the runtime derives CRO from canonical delegation state
    And CRO can advance its lifecycle and record a check-in
    And CoS does not impersonate CRO

  Scenario: CDR-006 CRO records a governed recommendation within authority
    Given CRO is executing a valid L2 delegated task
    When CRO records an evidence-backed commercial recommendation
    Then the decision record is attributed to CRO
    And the evidence and provenance are persisted
    And the recommendation does not expand CRO authority

  Scenario: CDR-007 Skill invocation cannot masquerade as agent invocation
    Given CRO is a registered agent principal
    When skills.invoke_governed is called with mesh-cro as though it were a Skill
    Then the request fails with unsupported-capability-type
    And the response directs the caller to the delegated owner execution contract
    And no Skill becomes an agent principal

  Scenario: CDR-008 CRO completes and the parent receives a reconcilable result
    Given CRO-owned work is in QA
    When CRO completes through delegated owner execution
    Then completion is attributed to CRO
    And outcome evidence is persisted
    And the owner-execution response carries the child result back to CoS
    And CoS can record an explicit parent reconciliation check-in
    And the child does not automatically complete or verify the parent

  Scenario: CDR-009 Completion remains separate from verification
    Given CRO has completed delegated work
    When the owner completion is persisted
    Then the child is COMPLETED but not VERIFIED
    And only the authorized verifier may independently verify acceptance evidence

  Scenario: CDR-010 Consequential action remains human gated
    Given delegated work reaches an L4 or L5 action boundary
    When owner execution attempts the consequential action without canonical approval
    Then execution stops
    And approval-required is returned
    And no external action occurs

  Scenario: CDR-011 Complete CoS to agent to CoS round trip
    Given a harmless internal parent task
    When CoS delegates to CRO
    And CRO starts, checks in, records evidence, and completes
    And CoS reconciles the child result to the parent
    And an authorized verifier verifies the child
    Then the round trip is auditable end to end
    And authority and approval boundaries remain intact

  @CDR-012 @scheduled @recovery
  Scenario: Pre-persistence caller assertion failure can recover without replacing canonical work
    Given a scheduled CoS parent is blocked only because delegation.create supplied an incorrect active_owner compatibility assertion
    And the direct-owner child remains nonterminal
    And no delegation record or provider side effect was persisted
    When the scheduler rereads canonical parent and child state
    And retries the same delegation ID and work contract once without parent_authority, depth, ancestry, or active_owner
    Then the delegation is persisted for the canonical child owner
    And the same parent resumes from BLOCKED to IN_PROGRESS
    And the same child continues through delegation.execute_owner
    And no duplicate parent, child, delegation, or external effect is created

  @CDR-013 @scheduled @security
  Scenario: Canonical owner mismatch is never repaired by changing the child owner
    Given a scheduled child is canonically owned by AgentOps
    When a delegation body names CMO as the accountable owner
    Then delegation fails with ownership-conflict
    And no delegation record is persisted
    And recovery does not reassign the child or substitute another agent identity


  @CDR-014 @scheduled @security
  Scenario: An explicitly supplied empty ancestry is still a compatibility assertion
    Given canonical registry lineage for a direct CoS child is cos
    When a caller supplies ancestry as an empty list
    Then delegation fails with invalid-delegation-contract
    And the empty list is not treated as though ancestry were omitted
    And no delegation record is persisted
    And recovery may retry the same work once with ancestry omitted

  @CDR-015 @scheduled @nested @recovery
  Scenario: CMO to VP Content nested delegation uses the same recovery contract
    Given CMO is executing a valid CoS-delegated Marketing Authority task
    And CMO creates one canonical VP Content child
    When the nested delegation request supplies active_owner as CMO
    Then delegation fails with ownership-conflict
    And no nested delegation record is persisted
    When CMO retries the same nested delegation ID once without caller ownership assertions
    Then the canonical VP Content delegation is persisted
    And nested owner execution identifies VP Content as the executing principal
    And inherited CMO and human publishing gates remain intact
