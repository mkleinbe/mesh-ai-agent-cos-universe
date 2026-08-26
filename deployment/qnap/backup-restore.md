# Backup and Restore

Canonical state is SQLite at `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` plus governance/audit/runtime state under `/share/Docker/cos-mcp/state/`.

The operator-authorized local backup destination is:

```text
/share/QNAP NAS/Mike Home/MCP/CoS/Backups
```

Because the path contains spaces, all scripts quote it as one shell argument.

## QNAP Docker privilege and release location

The current QNAP operator account requires `sudo` for Docker access. Invoke backup, restore validation, preflight, and deployment wrappers with `sudo` when they call Docker. The long-running Mesh container remains non-root UID/GID 65532.

Operator scripts are executed from the retained versioned release directory, for example `/share/Docker/cos-mcp/releases/v4.1.11`. They must not be copied to `/share/Docker`.

## Automated backup

`mesh-cos-mcp-backup.sh` creates a dated directory under the backup root and uses SQLite's online backup API inside the running container. It then records non-secret active deployment configuration and verifies SHA-256 checksums.

Each backup directory contains, when available:

- `taskledger.sqlite3`, created by SQLite online backup;
- active `compose.yaml`;
- active generated `.env`, which contains image identities, paths, resource settings, and `tunnel_id` but no runtime API key;
- active `release-metadata.txt`;
- `deployment-state.txt` with running image IDs and `secret_material_included=false`;
- `SHA256SUMS`.

The `secrets/` directory, tunnel runtime key, protected Slack human identity, Slack verifier token, and Socket Mode token are never copied.

`mesh-cos-mcp-deploy.sh` automatically creates a pre-deploy backup when an existing service is running and a post-deploy backup after verification succeeds. For v4.1.11, an explicit manual backup can be run from the versioned release directory:

```sh
cd /share/Docker/cos-mcp/releases/v4.1.11
sudo sh ./mesh-cos-mcp-backup.sh manual
```

The destination is on the same NAS. It protects against application/configuration failure but not total NAS loss. QNAP snapshots and an independent second copy remain recommended defense in depth after retention policy is approved.

## Candidate failure before promotion

A failed v4.1.11 candidate before `candidate_promote` leaves the active `.env`, active Compose, active release metadata, and canonical TaskLedger in place. Do not restore or replace state merely because candidate preparation or startup failed. Preserve the diagnostic log and versioned release directory, then determine whether rollback is actually required.

## Restore

1. Stop new consequential MCP work and preserve current logs/state metadata.
2. Stop `mesh-cos-tunnel` and `mesh-cos-mcp` using the approved Container Station/Docker path with `sudo` where required.
3. Select a verified dated directory under `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` and run `sha256sum -c SHA256SUMS` inside it.
4. Confirm the selected backup is schema-compatible with the intended Mesh image.
5. Restore `taskledger.sqlite3` to `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` only when state rollback is actually required, and restore ownership `65532:65532`, mode `0660` through the governed deployment/permission path rather than weakening the state mode.
6. If active configuration recovery is required, restore `compose.yaml`, `.env`, and matching `release-metadata.txt` as one compatible release set. Never fabricate or recover a runtime API key from backup because secret material is intentionally excluded.
7. Ensure the approved tunnel and Slack protected files still exist separately under `/share/Docker/cos-mcp/secrets` with governed ownership and mode `0400`.
8. Use the retained versioned release directory corresponding to the release being restored. Run its preflight from that directory with `sudo`.
9. Start/deploy through that release directory's `mesh-cos-mcp-deploy.sh`; require automated verification and a new post-restore backup.
10. Re-run `CHATGPT-ACCEPTANCE.md` before broader use.

For a v4.1.11 rollback investigation, the authoritative backup root remains `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`; choose the most recent verified `pre-deploy` or explicit `pre-v4.1.11-manual` backup rather than guessing a state file.
