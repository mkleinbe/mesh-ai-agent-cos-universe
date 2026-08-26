@ready
Feature: QNAP versioned release staging and safe promotion
  The QNAP deployment bundle must execute from its versioned release directory
  while preserving canonical runtime state and failing closed on release identity drift.

  Background:
    Given the canonical Mesh CoS MCP runtime contract is "4.0.0"
    And the canonical QNAP application root is "/share/Docker/cos-mcp"
    And release artifacts are staged under "/share/Docker/cos-mcp/releases/vX.Y.Z"
    And exactly 10 Mesh agents and 27 CoS MCP tools remain governed

  Scenario: QNAP-074 Versioned bundle executes without helper copying
    Given a release bundle is extracted into its versioned release directory
    When an operator invokes its deployment script from that directory
    Then helper scripts resolve from the extracted bundle root
    And no helper script must be copied to "/share/Docker"

  Scenario: QNAP-075 Staged candidate identity is independent of active production
    Given active production may still report deployment release "4.1.8"
    And the staged bundle metadata reports a newer semantic release
    When preflight runs before candidate preparation
    Then preflight reports the active deployment release separately
    And preflight reports the staged candidate release from staged metadata
    And it does not describe the active release as the candidate

  Scenario: QNAP-076 Git tag form normalizes to runtime release form
    Given Git release identity may be expressed as "vX.Y.Z"
    When release identity is compared with runtime metadata
    Then only a leading "v" is normalized
    And the runtime deployment value is "X.Y.Z"
    And invalid semantic versions are rejected

  Scenario: QNAP-077 Genuine release mismatch fails closed
    Given staged metadata identifies release "X.Y.Z"
    And an explicit requested deployment release identifies a different semantic release
    When preparation validates release identity
    Then preparation fails with "requested deployment release does not match extracted bundle metadata"
    And provenance validation is not bypassed

  Scenario: QNAP-078 Sudo does not need to preserve release identity
    Given a correctly staged release bundle contains release metadata
    When the operator runs "sudo sh ./mesh-cos-mcp-deploy.sh"
    And sudo does not preserve MESH_COS_DEPLOYMENT_RELEASE
    Then preparation derives the candidate release from staged metadata
    And deployment remains deterministic

  Scenario: QNAP-079 Candidate artifacts remain staged until healthy
    Given active runtime descriptors belong to the current production release
    When a new candidate is prepared
    Then candidate Compose and runtime environment remain in the versioned release directory
    And the active runtime descriptors are not replaced before candidate health succeeds

  Scenario: QNAP-080 Healthy candidate is promoted before verification
    Given candidate application and tunnel containers become healthy
    When deployment reaches the promotion stage
    Then candidate .env, Compose, and release metadata are atomically promoted to the canonical application root
    And post-deploy verification reads the promoted release identity

  Scenario: QNAP-081 Failed candidate preserves canonical state and rollback evidence
    Given the canonical TaskLedger and protected secrets already exist
    When candidate deployment fails before promotion
    Then the canonical TaskLedger is not destroyed or replaced
    And protected tunnel and Slack files are not exposed
    And the pre-deploy online backup remains available for rollback

  Scenario: QNAP-082 BusyBox and authority invariants remain unchanged
    Given the QNAP host uses its BusyBox-constrained shell environment
    When v4.1.11 deployment tooling runs
    Then operator scripts remain POSIX sh compatible
    And existing qnet/static networking is preserved
    And no L4 or L5 authority is widened
    And human-only approval operations remain human-only
    And completion remains separate from verification
