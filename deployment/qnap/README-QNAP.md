# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.16 Restarting-Runtime Backup Hotfix.**  
**Canonical Phase 1 authority/runtime contract: 4.0.0.**

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` retains `192.168.7.60` on verified QNAP `lan7` qnet and `172.30.60.2` on the internal MCP/tunnel bridge. The tunnel remains the trusted MCP source at `172.30.60.3` and uses a dedicated Docker egress bridge at `172.30.61.2` for OpenAI control-plane traffic.

The shared `mesh-cos-private` bridge is `internal: true`, so QNAP Docker Engine 27 is not asked to choose between multiple external-capable default routes. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

## v4.1.16 pre-deploy backup behavior

QNAP Docker can report `.State.Running=true` while a container is actually `restarting`. v4.1.16 no longer interprets `.State.Running` alone as proof that `docker exec` is safe.

- Stable `status=running` and `.State.Restarting=false`: use the existing online SQLite backup through the running container.
- Restarting or otherwise non-running existing runtime: use the quiesced helper backup path.
- A restarting runtime is stopped before SQLite state is read.
- The helper uses the exact active Mesh image with `--network none`, non-root UID/GID, read-only root filesystem, dropped capabilities, `no-new-privileges`, and no protected credential mounts.
- The helper runs the canonical `sqlite_backup.py`, including SQLite backup semantics and `PRAGMA integrity_check`.
- If the old runtime had running intent, that intent is restored after the backup attempt even if backup fails.
- Failed backup attempts remove temporary/partial backup state and fail closed.

## Slack HITL boundary

Slack has two deliberately separate surfaces:

- the connected Slack integration is collaboration-only and carries approval requests, status, coordination, and thread activity;
- the custom Slack app is only provider-authenticated `/mesh-approval` Socket Mode human ingress.

Connected Slack collaboration does not create approval authority. Ordinary Slack messages, reactions, copied commands, or user attribution cannot decide a canonical approval.

v4.1.16 requires one Slack application credential: the protected `xapp-` Socket Mode app-level token. It does not require, mount, validate, prompt for, or use an `xoxb-` verifier-bot token. A legacy verifier file may remain on the host solely for rollback compatibility with older releases.

## Canonical QNAP paths

- Operator release root: `/share/Docker/cos-mcp/releases`
- Current release directory: `/share/Docker/cos-mcp/releases/v4.1.16`
- Candidate payload: `/share/Docker/cos-mcp/releases/v4.1.16/cos-mcp`
- Candidate runtime environment: `/share/Docker/cos-mcp/releases/v4.1.16/cos-mcp/.env.runtime`
- Canonical application root: `/share/Docker/cos-mcp`
- Canonical state: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Protected secrets: `/share/Docker/cos-mcp/secrets`
- Deployment Docker config: `/share/Docker/cos-mcp/.docker-cli`
- Deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The operator remains in `/share/Docker/cos-mcp/releases` for staging and execution. The ZIP creates `v4.1.16/` automatically. Do not manually create the release directory, copy helpers into `/share/Docker`, or chmod release scripts before invoking them with `sh`.

## Governed human approver

The governed human approver is Michael/MK. The verified Slack user principal is `U01KG3CNYHK`.

A Slack identifier beginning with `D` is a conversation/channel identifier and is not a human user principal. Deployment validates existing `U...`/`W...` approver identity or stages the governed default non-interactively.

## Release-root and transactional promotion controls

1. The archive contains one top-level `v4.1.16/` directory.
2. Operator scripts self-resolve their own release directory using POSIX `dirname`, `cd`, and `pwd -P` behavior.
3. Deployment validates the resolved release directory beneath `/share/Docker/cos-mcp/releases` and matches its version to staged metadata.
4. Existing runtime state is backed up before candidate preparation whenever `mesh-cos-mcp` exists.
5. Candidate release identity comes from staged metadata, not active `.env` or caller environment.
6. Candidate build context, Compose, and `.env.runtime` remain inside the versioned release directory.
7. Candidate containers must become healthy before any active-file promotion.
8. Active `.env`, Compose, and release metadata are snapshotted before promotion, including absence markers.
9. Partial promotion or post-promotion verification failure restores the pre-promotion snapshot and previously active stack when available.
10. Failed rollback preserves the recovery snapshot for operator recovery.
11. Successful post-deploy verification is the promotion transaction commit point; only then is the rollback snapshot removed.
12. Canonical TaskLedger, tunnel identity/key, Slack protected files, qnet identity, logs, and backups remain outside the release directory.

## Runtime controls

- `mesh-cos-mcp`: UID/GID 65532, 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- long-running containers: non-root, read-only root filesystem, capabilities dropped, no-new-privileges, no Docker socket, no host networking
- `MESH_COS_AGENT_ID=cos` is process-bound
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.16` is required by the remote process
- `MESH_COS_SLACK_HITL_REQUIRED=true` is required by production Compose
- protected approver identity and Socket Mode token are read-only runtime mounts
- `/healthz` remains available through Slack provider degradation; `/readyz` fails closed while required Slack HITL is unavailable

Successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.16
agent_id: cos
```

Hosted production readiness additionally requires `slack_hitl_ready=true`.

## Authority boundary

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification separation, and tunnel source-IP trust boundary remain governed. Message Operations remains agent 10. Mesh Devil's Advocate remains a governed shared Skill, not agent 11.

## QNAP Docker privilege

From `/share/Docker/cos-mcp/releases`:

```sh
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

Host-side sudo does not alter the long-running application identity, which remains UID/GID `65532:65532`.

## Persistence, backup, rollback, and observability

Stable runtimes use online SQLite backup. Restarting/non-running existing runtimes use the quiesced one-shot helper. Backup receipts include integrity evidence, non-secret configuration, image IDs, source container state, backup method, and SHA-256 checks. `secrets/` is never copied or mounted into the quiesced helper.

Do not delete or recreate state after a failed candidate. Use `rollback-checklist.md` and `backup-restore.md`. If deployment reports an incomplete transactional rollback, preserve the referenced `.release-rollback.*` snapshot.

Deployment logs and diagnostics exclude credential contents, protected identity contents, generated environment contents, credential-bearing argv, and tunnel credentials.

## Operator flow

Use `DEPLOYMENT-STEPS.md`. The release staging working directory is `/share/Docker/cos-mcp/releases`.

After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and `chatgpt-published-app-production-acceptance-v4.1.16.md`. Repository/release verification is not production certification; the actual QNAP serving instance plus hosted ChatGPT and Slack acceptance must pass separately.

Controlled HTTPS remains unimplemented and requires separate explicit approval.