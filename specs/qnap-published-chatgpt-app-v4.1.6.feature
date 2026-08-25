Feature: QNAP Secure MCP published ChatGPT app production identity
  The published Mesh CoS MCP app must preserve the canonical Phase 1 authority contract
  while making the serving QNAP deployment release observable and fail closed.

  Scenario: QNAP-051 remote runtime requires deployment release identity
    Given the remote MCP process is configured for Secure MCP Tunnel transport
    And MESH_COS_DEPLOYMENT_RELEASE is missing or blank
    When the remote process starts
    Then startup fails before listening for MCP traffic
    And no tool authority is expanded

  Scenario: QNAP-052 health and readiness expose non-secret dual release identity
    Given the remote MCP process is release 4.1.6
    And the canonical Phase 1 MCP authority contract is 4.0.0
    When /healthz or a successful /readyz is read
    Then the response reports mcp_version 4.0.0
    And the response reports deployment_release 4.1.6
    And the response reports agent_id cos
    And the response reports transport SECURE_MCP_TUNNEL
    And no secret material is returned

  Scenario: QNAP-053 governed tool responses expose deployment release separately
    Given the published Mesh CoS MCP app invokes an allowed CoS tool
    When the tool succeeds through the Secure MCP Tunnel
    Then the tool envelope reports mcp_version 4.0.0
    And the tool envelope reports deployment_release 4.1.6
    And the tool envelope reports agent_id cos
    And existing result semantics are unchanged

  Scenario: QNAP-054 published ChatGPT app remains stable across sequential calls
    Given the published Mesh CoS MCP app is connected through the OpenAI Secure MCP Tunnel
    When registry, governance, metrics, agent lookup, and task reads are called sequentially ten times
    Then every call succeeds without HTTP 502
    And no invalid_session error is returned
    And no reconnect or container restart is required
    And the roster remains exactly 10 registered agents

  Scenario: QNAP-055 production catalog preserves the authority boundary
    Given the published Mesh CoS MCP app scans the production catalog
    When the CoS tool catalog is projected
    Then exactly 27 governed CoS tools are exposed
    And approval.record_decision is absent
    And reliability.human_override is absent
    And Mesh Devil's Advocate is not an agent principal
    And Message Operations remains the tenth registered agent
