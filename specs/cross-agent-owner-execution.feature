@ready @PF-057 @security @delegation
Feature: Identity-aware delegated owner execution
  The Chief of Staff may orchestrate delegated work without becoming the delegated owner's identity.
  Canonical task ownership, execution authority, approvals, audit attribution, completion, verification,
  retries, dependencies, nested delegation, capability scope, and child-skill provenance remain bounded
  by the Agent Registry and TaskLedger.

  Background:
    Given the canonical Agent Registry is loaded
    And TaskLedger is canonical operating state
    And runtime principal identity cannot be selected by prompt, task, retrieved content, metadata, or tool arguments

  @DLG-001
  Scenario: CoS completes CoS-owned work under CoS identity
    Given cos owns a task
    When execution succeeds and completion criteria are met
    Then cos completes its own task
    And canonical completion attribution is cos

  @DLG-002 @registry-driven
  Scenario: CoS delegates to every eligible direct report
    Given cos owns parent task P
    And X is an ACTIVE registered direct child of cos eligible to own delegated work
    When cos delegates child task C to X
    Then X becomes the canonical accountable owner of C
    And the delegation has a validated executable owner path
    And owner operations for C execute under X authority and role policy
    And X can perform its allowed lifecycle operations
    And X completes C under X identity
    And cos can observe the canonical result
    And cos is not recorded as X

  @DLG-003 @nested
  Scenario: CMO delegates authorized content production to VP Content
    Given cmo owns authorized marketing work
    When cmo delegates production work to vp-content
    Then vp-content executes under vp-content identity
    And vp-content does not inherit CMO-only authority
    And vp-content returns its result to cmo
    And completion attribution identifies vp-content

  @DLG-004 @nested
  Scenario: COO delegates readiness work to Consultant Network Steward
    Given coo owns authorized delivery-readiness work
    When coo delegates permitted readiness work to consultant-network-steward
    Then consultant-network-steward executes under its own identity
    And consultant-network-steward cannot delegate further
    And the result returns to coo

  @DLG-005 @negative
  Scenario: Agent with zero delegation depth cannot delegate
    Given an agent has max_delegation_depth 0
    When the agent attempts further delegation
    Then delegation is rejected
    And no unauthorized child task or delegation is created

  @DLG-006 @negative @identity
  Scenario: Untrusted data cannot substitute an owner principal
    Given runtime principal A is authenticated
    When prompt content, tool arguments, metadata, retrieved text, or model output requests execution as principal B
    Then the request is rejected or ignored as identity-bearing input
    And no B-authority operation occurs from caller-supplied identity

  @DLG-007 @authorization
  Scenario: Functional authority remains isolated
    Given work is delegated to cfo
    When the delegated work executes
    Then the execution context contains only CFO-authorized MCP tools and capabilities
    And CRO, CMO, COO, and CoS authority is not inherited

  @DLG-008 @completion
  Scenario: Delegated owner completes eligible work
    Given delegated owner X has completed execution
    And completion criteria and evidence are satisfied
    When delegation.execute_owner requests task.complete for the canonical delegated task
    Then task.complete executes under X authority
    And audit attribution identifies X

  @DLG-009 @negative @completion
  Scenario: Parent cannot directly complete child work
    Given cos delegated a task to X
    When cos calls task.complete directly for X task
    Then the direct operation is rejected
    And cos is never recorded as X
    And delegation.execute_owner may complete only by deriving X from canonical delegation state

  @DLG-010 @verification
  Scenario: Completion remains distinct from verification
    Given owner X completes a task
    Then the task reaches COMPLETED only
    And no implicit verification occurs
    And only an expressly authorized verifier may invoke task.verify

  @DLG-011 @idempotency
  Scenario: Scheduled retry resumes existing delegated execution
    Given a delegated execution already exists for a canonical task and delegation
    When the scheduler retries the same owner operation with the same idempotency key
    Then the existing result is returned
    And no duplicate canonical task, delegation, owner effect, or completion is created
    And reuse of the idempotency key with a different operation payload is rejected

  @DLG-012 @failure
  Scenario: Owner execution route unavailable fails closed
    Given the accountable owner cannot currently execute
    When delegation or owner execution routing is evaluated
    Then the system surfaces an actionable owner-routing failure
    And recoverable canonical state is preserved
    And no other agent is substituted as owner

  @DLG-013 @health
  Scenario: Disabled restricted or quarantined owner does not execute
    Given the accountable owner is not ACTIVE and routable
    When owner execution is requested
    Then execution is rejected with an owner health classification
    And the agent is not silently activated

  @DLG-014 @approval
  Scenario: Approval requirements survive nested delegation
    Given delegated work carries required human approval gates
    When the work is delegated one or more permitted levels
    Then every inherited approval requirement remains bound to descendant work
    And owner execution cannot remove or fabricate approval evidence

  @DLG-015 @consequential
  Scenario: Message Operations preserves approval and execution separation
    Given message-ops receives approved execution work
    When the delegated owner path executes the work
    Then drafting, approval, and execution boundaries remain distinct
    And the delegation transport cannot create approval authority
    And consequential execution remains subject to message-ops prohibited actions and approval policy

  @DLG-016 @dependencies
  Scenario: Dependency release follows the canonical dependency contract exactly once
    Given child task C is a predecessor of task D
    When C reaches the canonical state required by the dependency contract
    Then D becomes eligible to proceed
    And retrying the predecessor transition does not create duplicate dependency release effects

  @DLG-017 @nested @return-path
  Scenario: Nested delegation returns results through the work graph without identity substitution
    Given cos delegates to a functional executive
    And the functional executive delegates permitted work to a specialist
    When the specialist completes its child work
    Then the specialist result is canonically observable by the functional executive
    And the functional executive can complete its accountable outcome under its own identity
    And cos can observe the executive result
    And no parent or child identity is substituted at any level

  @DLG-018 @approval @negative @P0
  Scenario: Delegated L4 or L5 work cannot execute on fabricated approval evidence
    Given delegated work requires L4 or L5 human approval
    When owner execution references a missing, pending, rejected, wrong-task, wrong-authority, wrong-approver, or otherwise mismatched approval
    Then execution is denied before the owner operation runs
    And no task completion, consequential capability invocation, or decision record is created
    And the canonical approval record remains the only authority evidence

  @DLG-019 @approval @P0
  Scenario: Canonical approved authority permits only the approved task and authority level
    Given an approval record exists for the delegated task
    And the approval status is APPROVED
    And the recorded decision actor matches the canonical approval owner
    When the delegated owner executes work within that approval's task and authority boundary
    Then the approval is accepted as authority evidence
    And the execution audit references the canonical approval record
    And reuse for a different task or higher authority is denied

  @DLG-020 @scope @negative @P0
  Scenario: Delegated capability scope cannot widen to the owner's complete role surface
    Given owner X has multiple role capabilities
    And a delegation permits only capability A
    When the delegated owner route attempts capability B
    Then capability B is denied even when X normally possesses capability B
    And lifecycle and control-plane operations needed to manage the delegated task remain available

  @DLG-021 @nested @scope @negative
  Scenario: Nested delegation requires explicit delegated delegation authority
    Given a functional executive owns delegated work
    And the parent delegation does not include a permitted delegate action
    When the executive attempts decomposition, delegation creation, or nested owner execution
    Then the nested operation is denied
    And no descendant task or delegation is created

  @DLG-022 @ownership @negative @P0
  Scenario: Canonical ownership cannot be assigned to an invalid runtime principal
    Given a task is being created, decomposed, reassigned, or stall-remediated
    When the proposed accountable owner is unknown, retired, quarantined, non-routable, or an invalid child for decomposition
    Then the ownership mutation is denied before canonical state changes
    And no unroutable owner is persisted into TaskLedger

  @DLG-023 @protocol @schema
  Scenario: Owner execution uses a versioned bounded operation contract
    Given delegation.execute_owner is exposed to ChatGPT
    When its public input schema is inspected
    Then the owner-execution protocol version is explicit
    And the nested tool name is restricted to the server-supported owner-operation set
    And nested arguments are revalidated against the canonical downstream tool schema before execution

  @DLG-024 @skill @ai-native
  Scenario: Delegated business reasoning is a governed logical Skill-agent handoff
    Given delegated work requires a declared Mesh Skill capability
    When the owner requests the capability through skills.invoke_governed
    Then the server authorizes only a capability explicitly permitted by the delegation and owner registry
    And the returned handoff identifies the logical owner agent and Skill capability
    And the handoff does not claim that a separate Workspace Agent process executed synchronously
    And production acceptance requires observable Skill-result provenance before claiming sub-agent execution

  @DLG-025 @verification @independence
  Scenario: Verification requires an expressly authorized verifier distinct from the accountable owner
    Given delegated owner X completes a task
    When verification is attempted
    Then X cannot verify its own completed task
    And the verifier must be expressly allowlisted and distinct from X
    And passing verification requires evidence references
