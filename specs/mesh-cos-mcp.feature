Feature: QNAP production boundary for mesh-cos-mcp
  Scenario: QNAP-001 Correct CPU architecture starts
  Scenario: QNAP-002 Wrong image architecture fails deployment
  Scenario: QNAP-003 Canonical QNAP bind mount persists state
  Scenario: QNAP-004 Incorrect filesystem permission fails closed
  Scenario: QNAP-005 Missing ledger fails readiness
  Scenario: QNAP-006 Container restart preserves state
  Scenario: QNAP-007 Application recreation preserves state
  Scenario: QNAP-008 CoS identity cannot be changed at request time
  Scenario: QNAP-009 Unauthorized tools are absent
  Scenario: QNAP-010 Human-only tools remain inaccessible
  Scenario: QNAP-011 Completion does not verify
  Scenario: QNAP-012 Verification requires evidence
  Scenario: QNAP-013 Delegation depth cannot be bypassed
  Scenario: QNAP-014 Replay rejects arbitrary execution
  Scenario: QNAP-015 Prompt injection cannot expand authority
  Scenario: QNAP-016 Tunnel mode exposes no published host MCP port
  Scenario: QNAP-017 Non-tunnel remote mode refuses startup
  Scenario: QNAP-018 Health endpoint reports process state
  Scenario: QNAP-019 Readiness fails when canonical runtime fails
  Scenario: QNAP-020 Graceful shutdown preserves canonical state
  Scenario: QNAP-021 Container runs without privileged mode
  Scenario: QNAP-022 Container has no Docker socket access
  Scenario: QNAP-023 Secret values do not appear in logs
  Scenario: QNAP-024 Backup restores verified canonical state
  Scenario: QNAP-025 Rollback restores prior working image
  Scenario: QNAP-026 MCP requests from LAN are rejected while tunnel-private source is accepted
  Scenario: QNAP-027 Concurrent tool calls are serialized at the SQLite write boundary
