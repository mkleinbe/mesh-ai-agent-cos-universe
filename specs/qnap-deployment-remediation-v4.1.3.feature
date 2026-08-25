@ready
Feature: QNAP non-root deployment remediation and observability
  Background:
    Given the production runtime identity remains UID and GID 65532
    And the QNAP SSH operator has Docker access but is not assumed to have host chown authority
    And canonical TaskLedger and tunnel-secret boundaries remain unchanged

  Scenario: QNAP-038 Non-root QNAP operator can hand runtime ownership to UID 65532
    Given host chown of QNAP shared-folder state to UID 65532 is not permitted
    When preparation normalizes runtime state ownership
    Then it uses a one-shot Docker helper with network disabled and read-only root filesystem
    And the helper drops all capabilities before adding only the required ownership capabilities
    And the helper can access only the explicit state or secrets bind mount
    And the long-running Mesh runtime remains non-root UID 65532
    And no host chown command is required

  Scenario: QNAP-039 Deployment failures produce durable redaction-safe diagnostics
    Given any deployment prepare preflight verify or backup stage returns a nonzero status
    When the failure is handled
    Then the durable log records run ID timestamp stage command classification return code script and line when available
    And bounded operator Docker Compose filesystem capacity and container-state evidence is collected
    And the final console output includes the diagnostic log path
    And secret-file contents env-file contents process environments and credential-bearing argv are not collected
    And the parent SSH session remains active

  Scenario: QNAP-040 Docker CLI uses a deployment-local writable configuration path
    Given Container Station maps the default Docker config home to a path unreadable by the SSH operator
    When Mesh QNAP deployment tooling initializes Docker
    Then DOCKER_CONFIG points to the deployment-local application directory
    And that directory is writable by the SSH operator
    And Docker and Compose operations do not depend on the inaccessible QPKG home config

  Scenario: QNAP-041 Backup export does not require host ownership of canonical runtime state
    Given the online SQLite backup is created by runtime UID 65532 inside the state bind mount
    When the backup script exports the completed SQLite backup
    Then it uses Docker-mediated copy from the running Mesh container
    And it removes the temporary backup through the runtime container
    And the SSH operator does not need direct read or write permission on the canonical state file
    And backup integrity and secret-exclusion checks still pass
