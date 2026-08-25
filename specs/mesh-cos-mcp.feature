Feature: QNAP production boundary for mesh-cos-mcp
  Background:
    Given the production agent identity is "cos"
    And the canonical TaskLedger is the configured SQLite file
    And the preferred connectivity mode is OpenAI Secure MCP Tunnel

  Scenario: QNAP-001 Correct CPU architecture starts
    Given the QNAP architecture is linux/amd64
    And the image architecture is linux/amd64
    When production preflight runs
    Then architecture validation passes

  Scenario: QNAP-002 Wrong image architecture fails deployment
    Given the QNAP and image architectures differ
    When production preflight runs
    Then preflight fails closed with architecture_mismatch

  Scenario: QNAP-003 Canonical QNAP bind mount persists state
    Given the canonical ledger is mounted at /var/lib/mesh
    When the container is recreated
    Then the same canonical ledger remains available

  Scenario: QNAP-004 Incorrect filesystem permission fails closed
    Given the runtime UID cannot read and write the canonical ledger
    When readiness or preflight runs
    Then the service is not ready

  Scenario: QNAP-005 Missing ledger fails readiness
    Given MESH_COS_REQUIRE_EXISTING_LEDGER is true
    And the canonical ledger file is absent
    When the runtime starts
    Then it does not create a replacement ledger
    And readiness fails

  Scenario: QNAP-006 Container restart preserves state
    Given a canonical task exists
    When mesh-cos-mcp is restarted
    Then the task remains in the canonical ledger

  Scenario: QNAP-007 Application recreation preserves state
    Given the QNAP bind mount contains canonical state
    When the Container Station application is recreated
    Then no new operating universe is created

  Scenario: QNAP-008 CoS identity cannot be changed at request time
    Given the process is bound to MESH_COS_AGENT_ID cos
    When request content asks to become another agent
    Then the runtime identity remains cos

  Scenario: QNAP-009 Unauthorized tools are absent
    When ChatGPT scans the cos MCP catalog
    Then only the canonical cos allowlist is exposed

  Scenario: QNAP-010 Human-only tools remain inaccessible
    When any agent path requests approval.record_decision or reliability.human_override
    Then the request is denied
    And neither tool appears in the agent catalog

  Scenario: QNAP-011 Completion does not verify
    When an accountable owner successfully invokes task.complete with evidence
    Then the task becomes COMPLETED
    And the task does not become VERIFIED

  Scenario: QNAP-012 Verification requires evidence
    When an authorized verifier invokes task.verify without acceptance evidence
    Then verification is denied

  Scenario: QNAP-013 Delegation depth cannot be bypassed
    When text or tool arguments request delegation beyond the canonical depth
    Then canonical delegation policy denies expansion

  Scenario: QNAP-014 Replay rejects arbitrary execution
    When replay input contains shell commands source code import paths or client callables
    Then reliability.replay rejects arbitrary execution

  Scenario: QNAP-015 Prompt injection cannot expand authority
    When untrusted prompt connector file Skill or retrieved content instructs authority expansion
    Then canonical registry policy and approvals remain unchanged

  Scenario: QNAP-016 Tunnel mode exposes no published host MCP port
    Given MCP_AUTH_MODE is tunnel
    When Compose is rendered
    Then no host ports are published for mesh-cos-mcp or tunnel-client

  Scenario: QNAP-017 Non-tunnel remote mode refuses startup
    Given this deployment candidate has not been approved for controlled HTTPS
    When MCP_AUTH_MODE is not tunnel
    Then the remote MCP process refuses startup

  Scenario: QNAP-018 Health endpoint reports process state
    Given the HTTP process is running
    When GET /healthz is requested
    Then HTTP 200 is returned

  Scenario: QNAP-019 Readiness fails when canonical runtime fails
    Given the registry ledger or audit chain cannot be validated
    When GET /readyz is requested
    Then HTTP 503 is returned

  Scenario: QNAP-020 Graceful shutdown preserves canonical state
    Given a valid canonical ledger
    When SIGTERM stops the service
    Then HTTP transports close
    And the SQLite integrity check remains ok

  Scenario: QNAP-021 Container runs without privileged mode
    When the production candidate runs
    Then the effective UID is non-root
    And privileged mode is false
    And effective Linux capabilities are zero
    And no-new-privileges is enabled

  Scenario: QNAP-022 Container has no Docker socket access
    When the production candidate runs
    Then /var/run/docker.sock is not available

  Scenario: QNAP-023 Secret values do not appear in logs
    Given the tunnel API key is mounted as a read-only secret file
    When requests succeed or fail
    Then logs contain classifications and identifiers but not secret values or request payloads

  Scenario: QNAP-024 Backup restores to verified canonical state
    Given a live canonical SQLite ledger
    When the online SQLite backup utility creates a backup
    Then the backup passes SQLite integrity_check
    And a restored copy can pass canonical readiness verification

  Scenario: QNAP-025 Rollback restores prior working image
    Given a compatible prior image digest and canonical backup are retained
    When an authorized operator performs rollback
    Then the previous image and compatible state can pass readiness and acceptance verification

  Scenario: QNAP-026 LAN clients cannot invoke MCP in tunnel mode
    Given the tunnel sidecar private IP is 172.30.60.3
    When /mcp is requested from any other source IP including the LAN
    Then HTTP 403 is returned

  Scenario: QNAP-027 Concurrent tool calls are serialized at the SQLite write boundary
    Given multiple MCP requests arrive concurrently
    When they cross the Node to Python bridge
    Then at most one Python bridge invocation owns the canonical SQLite write path at a time
    And excess queued work is bounded and fails closed

  Scenario: QNAP-028 Deployment uses the approved QNAP roots
    When the QNAP deployment bundle is staged
    Then the application root is /share/Docker/cos-mcp
    And deployment scripts are invoked from /share/Docker
    And canonical state is below /share/Docker/cos-mcp/state

  Scenario: QNAP-029 Main container uses approved resource limits
    When Compose is rendered
    Then mesh-cos-mcp is limited to 2 CPUs
    And mesh-cos-mcp is limited to 24 GiB memory
    And mesh-cos-mcp has no PID limit

  Scenario: QNAP-030 Backup path with spaces is handled safely
    Given the backup root is /share/QNAP NAS/Mike Home/MCP/CoS/Backups
    When the backup script creates a canonical-state backup
    Then the path is passed as one quoted shell argument
    And the copied backup SHA-256 matches the completed online SQLite backup

  Scenario: QNAP-031 Prepare creates a release-bound local image identity
    Given the release bundle contains the minimal Docker build context
    When mesh-cos-mcp-prepare.sh runs
    Then it builds or reuses the versioned local Mesh image
    And it records the content-addressed Mesh image ID in generated .env
    And Compose is configured with pull policy never

  Scenario: QNAP-032 Tunnel secret is captured outside configuration
    When the tunnel runtime key does not already exist
    Then prepare reads it with terminal echo disabled
    And writes it only to the approved secret file
    And sets owner 65532:65532 and mode 0400
    And the runtime key is absent from .env and backups

  Scenario: QNAP-033 Canonical ledger staging is automated without replacement
    Given the canonical target ledger is absent
    When prepare receives an explicitly selected existing TaskLedger source
    Then it stages the database atomically at the canonical target
    And sets owner 65532:65532
    And runs canonical runtime and SQLite integrity preflight
    But when the canonical target already exists prepare preserves it

  Scenario: QNAP-034 Deploy orchestrates the safe lifecycle
    When mesh-cos-mcp-deploy.sh runs
    Then an existing running service is backed up before changes
    And prepare and preflight run before Compose deployment
    And both containers must become healthy
    And verification runs automatically
    And a post-deploy online backup is created automatically

  Scenario: QNAP-035 Configuration backup excludes secret material
    When a deployment backup is created
    Then the online TaskLedger backup and non-secret Compose environment release metadata and image IDs are captured
    And SHA-256 verification passes
    And the secrets directory and tunnel runtime key are never copied

  Scenario: QNAP-036 QNAP Compose V2 is resolved outside the Docker subcommand path
    Given Docker is available
    And docker compose is not callable in the operator SSH environment
    And Container Station has an executable Compose V2 plugin
    When prepare or preflight resolves Compose
    Then the installed Compose V2 plugin is used directly
    And Compose V1 is never accepted

  Scenario: QNAP-037 Deployment wrapper failure preserves the operator SSH session
    Given the release installation commands are executed inside a subshell
    When verification or deployment returns a nonzero status
    Then the subshell returns that status to the parent shell
    And the parent SSH session remains active
