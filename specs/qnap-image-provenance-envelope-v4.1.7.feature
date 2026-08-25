@ready
Feature: QNAP release image provenance and hosted MCP envelope verification
  The QNAP deployment must not reuse an ambiguous local Mesh image tag and must verify
  the governed tool response envelope of the actually running Secure MCP service.

  Scenario: QNAP-056 stale same-tag Mesh image is rebuilt from the verified bundle
    Given a local Mesh image already exists under the requested QNAP release tag
    And its OCI version or revision label does not match the extracted release metadata
    When the deployment prepares the Mesh image
    Then the existing local tag is not trusted as the release candidate
    And the Mesh image is rebuilt from the extracted release build context
    And the rebuilt image OCI version and revision match the release metadata

  Scenario: QNAP-057 matching release image may be reused only with provenance evidence
    Given a local Mesh image already exists under the requested QNAP release tag
    And its OCI version and revision labels exactly match the extracted release metadata
    When the deployment prepares the Mesh image
    Then the image may be reused without changing the canonical TaskLedger or tunnel secret
    And the recorded image ID remains bound to the verified release identity

  Scenario: QNAP-058 post-deploy verification exercises the governed tool envelope
    Given mesh-cos-mcp and mesh-cos-tunnel are healthy on the private Secure MCP network
    When post-deploy verification invokes an allowed CoS tools/call from the tunnel network namespace
    Then the returned governed tool envelope reports mcp_version 4.0.0
    And the returned governed tool envelope reports deployment_release 4.1.7
    And the returned governed tool envelope reports agent_id cos
    And the result is returned without weakening the tunnel source-IP ingress boundary
