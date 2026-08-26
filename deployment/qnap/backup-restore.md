# Backup and Restore

Canonical state is SQLite at `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` plus governance/audit/runtime state under `/share/Docker/cos-mcp/state/`.

The operator-authorized local backup destination is:

```text
/share/QNAP NAS/Mike Home/MCP/CoS/Backups
```

Because the path contains spaces, all scripts quote it as one shell argument.

## QNAP Docker privilege and release location

The current QNAP operator account requires `sudo` for Docker access. The stable operator working directory for retained release scripts is:

```text
/share/Docker/cos-mcp/releases
```

Invoke a retained release by its versioned path from that root, for example `./v4.1.12/mesh-cos-mcp-backup.sh`. Release helpers are never copied to `/share/Docker`, and the operator does not need to change into the version directory.

The long-running Mesh container remains non-root UID/GID 65532.

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

`mesh-cos-mcp-deploy.sh` automatically creates a pre-deploy backup when an existing service is running and a post-deploy backup after verification succeeds. An explicit v4.1.12 manual backup can be run without leaving the releases root:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.12/mesh-cos-mcp-backup.sh manual
```

The destination is on the same NAS. It protects against application/configuration failure but not total NAS loss. QNAP snapshots and an independent second copy remain recommended defense in depth after retention policy is approved.

## Candidate failure before promotion

A failed v4.1.12 candidate before `candidate_promote` leaves the active `.env`, active Compose, active release metadata, and canonical TaskLedger in place. Do not restore or replace state merely because candidate preparation or startup failed. Preserve the diagnostic log and versioned release directory, then determine whether rollback is actually required.

## Restore

1. Stop new consequential MCP work and preserve current logs/state metadata.
2. Stop `mesh-cos-tunnel` and `mesh-cos-mcp` using the approved Container Station/Docker path with `sudo` where required.
3. Select a verified dated directory under `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` and run `sha256sum -c SHA256SUMS` inside it.
4. Confirm the selected backup is schema-compatible with the intended Mesh image.
5. Restore `taskledger.sqlite3` to `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3` only when state rollback is actually required, and restore ownership `65532:65532`, mode `0660` through the governed deployment/permission path rather than weakening the state mode.
6. If active configuration recovery is required, restore `compose.yaml`, `.env`, and matching `release-metadata.txt` as one compatible release set. Never fabricate or recover a runtime API key from backup because secret material is intentionally excluded.
7. Ensure the approved tunnel and Slack protected files still exist separately under `/share/Docker/cos-mcp/secrets` with governed ownership and mode `0400`.
8. Return to `/share/Docker/cos-mcp/releases` and invoke the retained version's preflight as `sudo sh ./vX.Y.Z/mesh-cos-mcp-preflight.sh`.
9. Start/deploy from the same working directory using `sudo sh ./vX.Y.Z/mesh-cos-mcp-deploy.sh`; require automated verification and a new post-restore backup.
10. Re-run `CHATGPT-ACCEPTANCE.md` before broader use.

The authoritative backup root remains `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`; choose the most recent verified compatible backup rather than guessing a state file.
