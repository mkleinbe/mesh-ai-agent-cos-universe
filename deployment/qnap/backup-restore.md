# Backup and Restore
Canonical state is SQLite at `/var/lib/mesh/ledger/taskledger.sqlite3` plus governance/audit/runtime files under the verified state root. Do not back up `.env`, runtime API keys, transient `/tmp`, images, logs, or caches as business-state backups.

## Consistent backup
Do not copy an actively written SQLite file blindly. Use SQLite's online backup API from a controlled operator utility or stop the MCP service cleanly before a filesystem copy/snapshot. A QNAP snapshot is acceptable only after consistency has been established for the SQLite file.

Recommended cadence: daily retained backups plus a mandatory pre-upgrade backup, calibrated to business recovery objectives. Production scheduling remains a human operations decision.

## Restore
1. Stop `mesh-cos-mcp` and tunnel-client.
2. Preserve the failed/current state separately for audit.
3. Restore the verified database and required governance/runtime files to the same narrow QNAP root.
4. Restore required ownership and permissions.
5. Start only `mesh-cos-mcp`; require `/readyz` success and audit-chain verification.
6. Confirm canonical task counts/known records and `cos` identity.
7. Start tunnel-client and run a read-only MCP acceptance test.
8. Record restore source, checksum/snapshot identifier, operator, image digest, and verification evidence.
