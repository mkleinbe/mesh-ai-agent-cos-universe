@ready
Feature: QNAP pre-deploy backup survives an unhealthy restarting active container

  Background:
    Given the canonical TaskLedger remains at /share/Docker/cos-mcp/state/ledger/taskledger.sqlite3
    And release deployment must preserve a verified pre-deploy backup before replacing an existing runtime

  Scenario: QNAP-112 Stable running runtime keeps the online SQLite backup path
    Given mesh-cos-mcp exists with Docker state status "running"
    And Docker reports State.Restarting as false
    When the QNAP backup command runs
    Then it uses the in-container SQLite backup helper through docker exec
    And it exports the consistent backup through docker cp
    And it does not stop the healthy running runtime

  Scenario: QNAP-113 Restarting runtime is quiesced and backed up without docker exec
    Given mesh-cos-mcp exists with Docker state status "restarting"
    And Docker may report State.Running as true during the restart loop
    When the pre-deploy backup runs
    Then it must not invoke docker exec against mesh-cos-mcp
    And it stops the unstable runtime before reading canonical SQLite state
    And it runs a one-shot network-isolated backup helper from the exact active Mesh image
    And the helper mounts only canonical state read-write and performs SQLite backup integrity checking
    And the backup is exported to the governed backup root
    And the previously running intent is restored after the backup attempt

  Scenario: QNAP-114 Failed quiesced backup restores the prior runtime intent and fails closed
    Given mesh-cos-mcp was running or restarting before the quiesced backup
    And the one-shot SQLite backup helper fails
    When backup cleanup runs
    Then temporary backup state is removed
    And mesh-cos-mcp is started again before the backup command returns
    And the backup command returns failure
    And no partial backup is represented as successful

  Scenario: QNAP-115 Deployment backs up an existing runtime even when it is not stably running
    Given mesh-cos-mcp exists in Docker
    And its state may be running, restarting, exited, or created
    When mesh-cos-mcp-deploy.sh enters pre_backup
    Then it invokes mesh-cos-mcp-backup.sh for the existing runtime
    And the backup implementation selects online or quiesced mode from Docker State.Status and State.Restarting
    And a missing mesh-cos-mcp container remains the only no-runtime condition that skips pre-deploy backup
