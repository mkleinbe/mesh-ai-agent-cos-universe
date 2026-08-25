@ready
Feature: QNAP release identity preflight reliability
  The QNAP deployment preflight must validate the generated deployment identity
  against the release metadata shipped in the same verified bundle rather than
  a duplicated hardcoded patch-release literal.

  Scenario: QNAP-048 matching bundle and environment release identities pass
    Given a verified QNAP release bundle contains release-metadata.txt with a version value
    And mesh-cos-mcp-prepare.sh generates MESH_COS_DEPLOYMENT_RELEASE from that release
    When mesh-cos-mcp-preflight.sh validates the deployment environment
    Then the release identity check compares MESH_COS_DEPLOYMENT_RELEASE to the bundle metadata version
    And no prior patch-release literal is used as the authority

  Scenario: QNAP-049 mismatched release identities fail closed before Compose replacement
    Given release-metadata.txt identifies one QNAP release version
    And the generated .env identifies a different MESH_COS_DEPLOYMENT_RELEASE
    When mesh-cos-mcp-preflight.sh validates the deployment environment
    Then preflight fails the release identity check
    And deployment does not proceed to Compose replacement
    And the existing healthy service remains available

  Scenario: QNAP-050 missing release metadata fails closed
    Given the extracted QNAP application root does not contain release-metadata.txt
    When mesh-cos-mcp-preflight.sh validates required paths
    Then preflight fails with a bundle release metadata error
    And deployment does not proceed to Compose replacement
