# Backup and Restore

Canonical state is SQLite at `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` plus governance/audit/runtime state under `/share/Docker/cos-mcp/state/`.

The operator-authorized local backup destination is:

```text
/share/QNAP NAS/Mike Home/MCP/CoS/Backups
```

Because the path contains spaces, all scripts quote it as one shell argument.

## Automated backup

`mesh-cos-mcp-backup.sh` creates a dated directory under the backup root and uses SQLite's online backup API inside the running container. It then records non-secret deployment configuration and verifies SHA-256 checksums.

Each backup directory contains, when available:

- `taskledger.sqlite3`, created by SQLite online backup;
- `compose.yaml`;
- generated `.env`, which contains image identities, paths, resource settings, and `tunnel_id` but no runtime API key;
- `release-metadata.txt`;
- `deployment-state.txt` with running image IDs and `secret_material_included=false`;
- `SHA256SUMS`.

The `secrets/` directory and `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key` are never copied.

`mesh-cos-mcp-deploy.sh` automatically creates a pre-deploy backup when an existing service is running and a post-deploy backup after verification succeeds. A manual backup can also be run from `/share/Docker`:

```sh
sh mesh-cos-mcp-backup.sh manual
```

The destination is on the same NAS. It protects against application/configuration failure but not total NAS loss. QNAP snapshots and an independent second copy remain recommended defense in depth after retention policy is approved.

## Restore

1. Stop `mesh-cos-tunnel` and `mesh-cos-mcp`.
2. Preserve current failed state and logs for audit.
3. Select a verified dated directory under `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` and run `sha256sum -c SHA256SUMS` inside it.
4. Confirm the selected backup is schema-compatible with the intended Mesh image.
5. Restore `taskledger.sqlite3` to `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` and restore ownership `65532:65532`, mode `0660`.
6. If configuration recovery is required, restore `compose.yaml` and `.env`. Never fabricate or recover a runtime API key from backup because secret material is intentionally excluded.
7. Ensure the approved tunnel runtime key exists separately at the secret path with owner `65532:65532`, mode `0400`.
8. Run `cd /share/Docker && sh mesh-cos-mcp-preflight.sh`.
9. Start/deploy through `sh mesh-cos-mcp-deploy.sh`; require automated verification and a new post-restore backup.
10. Re-run `CHATGPT-ACCEPTANCE.md` before broader use.
