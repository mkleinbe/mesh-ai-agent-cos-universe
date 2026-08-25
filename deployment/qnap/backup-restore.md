# Backup and Restore

Canonical state is SQLite at `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` plus governance/audit/runtime state under `/share/Docker/cos-mcp/state/`.

The operator-authorized local backup destination is:

```text
/share/QNAP NAS/Mike Home/MCP/CoS/Backups
```

Because the path contains spaces, shell usage must quote the entire path, for example:

```sh
BACKUP_ROOT="/share/QNAP NAS/Mike Home/MCP/CoS/Backups"
```

## Consistent backup

Do not copy the live SQLite ledger directly. `mesh-cos-mcp-backup.sh` invokes the repository SQLite online backup utility inside the running container, verifies the completed backup, then copies that closed backup file to the quoted backup directory and verifies the copied SHA-256 hash.

Run from `/share/Docker`:

```sh
sh mesh-cos-mcp-backup.sh
```

Recommended cadence is daily retained backups plus a mandatory pre-upgrade/pre-rollback backup. Scheduling remains an operator decision.

The configured destination is on the same NAS. It protects against application/configuration failure but not total NAS loss. QNAP snapshots and an independent second copy remain recommended defense in depth after their retention policy is approved.

Do not include `.env`, tunnel runtime keys, transient `/tmp`, images, container logs, or caches in business-state backups.

## Restore

1. Stop `mesh-cos-tunnel` and `mesh-cos-mcp`.
2. Preserve the current failed state and logs for audit.
3. Select a verified backup from `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` and verify its recorded SHA-256.
4. Restore it to `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` only after schema compatibility is confirmed.
5. Restore ownership `65532:65532` and the approved state permissions.
6. Start only `mesh-cos-mcp`; require readiness, SQLite integrity, active `cos`, and audit-chain verification.
7. Start the tunnel sidecar and run the controlled ChatGPT read-only acceptance test.
8. Record backup source, checksum, operator, image digest, restore result, and audit evidence.
