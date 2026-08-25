@ready @qnap @mcp @production-acceptance @security-targeted
Feature: Mesh CoS MCP v4.1.8 production acceptance remediation
  The hosted Mesh CoS MCP must expose the request contract the runtime actually accepts,
  preserve canonical TaskLedger and authority semantics, and fail closed with useful safe errors.

  @QNAP-059 @request-contract
  Scenario: Published tool schemas match runtime request validation
    Given the canonical 27-tool CoS MCP contract and tool-input schema registry
    When a client lists tools and submits requests through the hosted MCP
    Then every exposed tool advertises its canonical object schema
    And the runtime validates the same schema before business dispatch
    And unknown fields are rejected where the schema is closed

  @QNAP-060 @validation @negative
  Scenario: Invalid structured input returns bounded field-level guidance
    Given a structured MCP request with a missing required field, malformed type, invalid enum, or unknown field
    When the request is validated
    Then the response error is validation_failed
    And the response contains bounded machine-readable field details
    And no stack trace, credential, secret, filesystem path, private data, or chain-of-thought is returned

  @QNAP-061 @task-ledger @lookup
  Scenario: Canonical task identifiers resolve consistently across task operations
    Given an existing canonical TaskLedger task identifier
    When task.get, task.decompose, task.check_in, task.transition, task.complete, and task.verify are exercised in lifecycle-valid states
    Then every operation resolves the same canonical task
    And a missing request field is validation_failed rather than not_found
    And a truly absent canonical task is not_found

  @QNAP-062 @skills @authorization
  Scenario: Declared governed Skills resolve through server registration and unauthorized Skills fail closed
    Given a Skill declared for an agent in the canonical registry
    When that agent invokes skills.invoke_governed
    Then the server returns a governed execution or external-Skill handoff record with agent and capability provenance
    And the invocation is auditable without persisting raw sensitive payloads
    But a globally undeclared Skill is not_found
    And a Skill declared only for another agent is forbidden
    And no client-supplied code, import path, callable, shell command, plugin executable, or Skill implementation is executed

  @QNAP-063 @agentops @validation
  Scenario: AgentOps recommendation uses the published structured request contract
    Given a valid agentops.recommend request
    When the CoS-bound MCP handles the request
    Then the recommendation succeeds
    But an invalid field or type returns validation_failed with bounded field guidance

  @QNAP-064 @identity @authorization
  Scenario Outline: Every Phase 1 agent runtime is immutably bound to its own identity
    Given an MCP process bound server-side as <agent>
    When its tool catalog and one allowed operation are exercised
    Then response agent_id is exactly <agent>
    And only that agent's canonical allowlist is exposed
    And human-only operations are absent
    And a client-supplied identity override cannot change the bound identity
    And a prohibited operation fails closed

    Examples:
      | agent                         |
      | cos                           |
      | agentops                      |
      | answer-desk                   |
      | cro                           |
      | cfo                           |
      | coo                           |
      | consultant-network-steward    |
      | cmo                           |
      | vp-content                    |
      | message-ops                   |

  @QNAP-065 @delegation @multi-agent
  Scenario: Multi-agent delegation preserves direct-child and terminal boundaries
    Given canonical synthetic acceptance work
    When CoS delegates marketing work to CMO and CMO delegates to VP Content
    And CoS delegates delivery work to COO and COO delegates to Consultant Network Steward
    Then both legal paths succeed with one accountable owner and inherited approval gates
    And VP Content and Consultant Network Steward cannot delegate further
    And authority widening and approval weakening fail closed
    And CRO, CFO, and COO recommendations do not become final pricing, discount, staffing, or irreversible client commitments

  @QNAP-066 @lifecycle @verification
  Scenario: Completion never implies verification
    Given a synthetic task progressed to a completion-eligible state
    When the accountable owner supplies a non-empty outcome and supporting evidence and calls task.complete
    Then the task status is COMPLETED
    And verified_at is null
    When an expressly authorized CoS verifier later supplies acceptance evidence and calls task.verify
    Then the task status may become VERIFIED
    And completion without outcome or evidence, verification before completion, unauthorized verification, verification without evidence, and child-to-parent verification propagation all fail closed

  @QNAP-067 @audit
  Scenario: Remediation preserves tamper-evident governance audit integrity
    Given the canonical governance audit chain is valid before acceptance writes
    When synthetic acceptance operations are executed
    Then material actions record server-derived actor identity and implementation provenance
    And the audit chain remains valid after the writes
    And private chain-of-thought is never persisted

  @QNAP-068 @release @hosted
  Scenario: Packaged and hosted v4.1.8 behavior agree
    Given the verified v4.1.8 QNAP release bundle is deployed through the existing Secure MCP Tunnel architecture
    When local post-deploy verification and hosted ChatGPT acceptance are executed
    Then successful hosted responses report mcp_version 4.0.0 and deployment_release 4.1.8
    And all original acceptance defects are green
    And no Severity 1, Severity 2, production-blocking, governance-blocking, or acceptance defect remains hidden
