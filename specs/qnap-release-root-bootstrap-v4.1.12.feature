@ready
Feature: QNAP release-root bootstrap and self-contained version pathing
  The QNAP operator must be able to keep the shell at /share/Docker/cos-mcp/releases
  while each release artifact creates and operates from its own versioned subdirectory.
  No operator step may require manually creating the version directory, copying helper
  scripts, changing into the version directory, moving bundle contents, or repairing modes.

  Background:
    Given the canonical active application root is /share/Docker/cos-mcp
    And the canonical release root is /share/Docker/cos-mcp/releases
    And the canonical Phase 1 authority/runtime contract remains 4.0.0

  Scenario: QNAP-083 release archive creates its version directory from the release root
    Given mesh-cos-mcp-qnap-v4.1.12.zip is present in /share/Docker/cos-mcp/releases
    When the operator unzips the archive while remaining in /share/Docker/cos-mcp/releases
    Then every extracted release payload path is under v4.1.12/
    And v4.1.12/mesh-cos-mcp-deploy.sh exists
    And v4.1.12/cos-mcp/release-metadata.txt exists
    And no loose mesh-cos operator script is extracted into the release root

  Scenario: QNAP-084 deployment runs from the canonical release root
    Given v4.1.12 has been extracted under /share/Docker/cos-mcp/releases
    When the operator remains in /share/Docker/cos-mcp/releases
    And runs sudo sh ./v4.1.12/mesh-cos-mcp-deploy.sh
    Then the deployment script resolves its own directory as the candidate release root
    And child scripts are invoked from that resolved release root
    And the operator does not need to cd into v4.1.12

  Scenario: QNAP-085 release directory identity must agree with staged metadata
    Given the deployment script resolves a versioned release directory
    And staged release metadata declares version 4.1.12
    Then the release-directory basename must be v4.1.12
    And a genuine directory-to-metadata version mismatch fails closed before preparation

  Scenario: QNAP-086 no manual staging choreography is required
    Given the ZIP and checksum are placed in /share/Docker/cos-mcp/releases
    When the operator follows the deployment runbook
    Then the runbook does not require mkdir for a version directory
    And the runbook does not require cp or mv of release payload files
    And the runbook does not require chmod of extracted operator scripts
    And the only working-directory change is cd /share/Docker/cos-mcp/releases

  Scenario: QNAP-087 auxiliary operator actions also run from the release root
    Given v4.1.12 has been extracted
    When the operator invokes backup, preflight, verify, or intentional Slack reconfiguration
    Then each command is addressed as ./v4.1.12/<script>.sh from /share/Docker/cos-mcp/releases
    And each script resolves its helper files relative to its own script directory

  Scenario: QNAP-088 release archive contains no canonical state or protected secrets
    When the v4.1.12 release archive is built
    Then every archive entry is under v4.1.12/
    And the archive contains no generated .env.runtime
    And the archive contains no canonical TaskLedger
    And the archive contains no secrets directory
    And the archive contains no protected Slack or tunnel credential values

  Scenario: QNAP-089 active runtime paths stay independent of release payload paths
    Given a v4.1.12 candidate is staged under the release root
    Then canonical state remains /share/Docker/cos-mcp/state
    And protected secrets remain /share/Docker/cos-mcp/secrets
    And deployment logs remain under /share/Docker/cos-mcp/logs/deployment
    And candidate build context and release metadata remain under the versioned release directory

  Scenario: QNAP-090 QNAP BusyBox-compatible path resolution is preserved
    When operator scripts resolve their own release directory
    Then they use POSIX sh compatible dirname, cd, and pwd -P behavior
    And they do not require realpath or readlink -f

  Scenario: QNAP-091 deployment remains fail-closed and authority-neutral
    Given the pathing remediation is applied
    Then release metadata mismatch checks remain mandatory
    And OCI image version and revision provenance remain mandatory
    And the Secure MCP Tunnel remains the production ingress
    And exactly 10 registered agents remain
    And exactly 27 governed CoS tools remain
    And human-only operations remain human-only
    And COMPLETED remains distinct from VERIFIED
