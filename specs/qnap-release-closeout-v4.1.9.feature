@ready @qnap @release @documentation @security-targeted
Feature: Mesh CoS MCP v4.1.9 release and documentation closeout
  v4.1.9 must advance the deployment release identity and release evidence
  without changing the canonical Phase 1 authority/runtime contract.

  @QNAP-069 @documentation
  Scenario: QNAP-069 Active documentation names one current deployment release
    Given the v4.1.9 release candidate
    When current repository and QNAP operator documentation is inspected
    Then the current deployment release is v4.1.9
    And historical versioned release records remain historical evidence
    And the canonical authority/runtime contract remains 4.0.0

  @QNAP-070 @release-identity
  Scenario: QNAP-070 Bundle, image, Compose, and governed envelope share deployment identity
    Given the verified v4.1.9 release bundle
    When the QNAP image and deployment configuration are produced
    Then release metadata reports version 4.1.9
    And the image version label is 4.1.9-qnap
    And Compose passes MESH_COS_DEPLOYMENT_RELEASE 4.1.9
    And successful governed responses report deployment_release 4.1.9

  @QNAP-071 @authority
  Scenario: QNAP-071 Patch release does not widen Phase 1 authority
    Given the v4.1.9 candidate
    When registry and tool projections are evaluated
    Then exactly 10 registered agents remain canonical
    And CoS exposes exactly 27 governed agent-facing tools
    And human-only operations remain absent from agent catalogs
    And Mesh Devil's Advocate remains a governed shared Skill rather than agent 11
    And COMPLETED does not imply VERIFIED

  @QNAP-072 @artifact @security
  Scenario: QNAP-072 Release package is deterministic and does not contain runtime secrets or canonical state
    Given the v4.1.9 release build
    When the QNAP ZIP and checksum are generated
    Then the checksum verifies the ZIP
    And the bundle contains the v4.1.9 release, security, acceptance, and scenario evidence
    And the tunnel runtime secret is absent
    And canonical TaskLedger data is absent

  @QNAP-073 @hosted
  Scenario: QNAP-073 Final production acceptance remains post-deploy evidence
    Given repository and container verification are green
    When v4.1.9 has not yet been exercised through the actual published ChatGPT app
    Then repository verification does not claim hosted production acceptance
    And final acceptance requires the installed Mesh CoS MCP app through the OpenAI Secure MCP Tunnel
