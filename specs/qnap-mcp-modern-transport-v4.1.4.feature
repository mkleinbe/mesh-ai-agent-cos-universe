@ready
Feature: QNAP Secure MCP Tunnel modern protocol reliability
  Background:
    Given the production MCP runtime is bound to agent "cos"
    And the canonical TaskLedger remains the configured SQLite ledger
    And OpenAI Secure MCP Tunnel is the only supported remote ingress

  Scenario: QNAP-042 Modern MCP discovery is served
    Given a trusted tunnel client reaches POST /mcp
    When it sends the MCP 2026-07-28 server/discover probe
    Then the endpoint returns a valid modern MCP discovery response
    And no initialize request or Mcp-Session-Id is required

  Scenario: QNAP-043 Sequential modern MCP requests remain stateless and reliable
    Given a trusted modern MCP client
    When it sends at least 10 consecutive valid MCP requests
    Then every request receives a valid MCP response
    And no request fails because of stale or exhausted protocol sessions
    And the runtime identity remains "cos"
    And neither the MCP process nor tunnel process requires a restart

  Scenario: QNAP-044 Legacy stateless MCP remains compatible during migration
    Given a trusted 2025-era Streamable HTTP client
    When it invokes the supported MCP endpoint
    Then the request is served through the v2 compatibility path
    And no persistent server-side protocol session is required

  Scenario: QNAP-045 Direct non-tunnel MCP ingress remains denied
    Given a request to POST /mcp does not originate from MCP_TRUSTED_CLIENT_IP
    When the request reaches mesh-cos-mcp
    Then HTTP 403 is returned before MCP dispatch
    And no governed tool is invoked

  Scenario: QNAP-046 Readiness detects protocol-serving failure
    Given the Python runtime and canonical TaskLedger are healthy
    And the modern MCP HTTP serving path cannot answer server/discover
    When GET /readyz is requested
    Then HTTP 503 is returned
    And healthz may remain a process-liveness signal

  Scenario: QNAP-047 Governance boundaries survive transport modernization
    When the modern MCP catalog is discovered
    Then exactly the governed CoS tool allowlist is exposed
    And approval.record_decision is absent
    And reliability.human_override is absent
    And exactly 10 canonical agents remain registered
    And Devil's Advocate remains a Skill rather than agent 11
