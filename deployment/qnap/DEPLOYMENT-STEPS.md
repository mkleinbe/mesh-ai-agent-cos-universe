# Short QNAP Deployment and Upgrade Steps

v4.1.16 fixes the restarting-runtime pre-deploy backup defect while retaining the v4.1.15 Slack HITL simplification, QNAP Docker Engine 27 deterministic egress, and transactional promotion recovery. The canonical Phase 1 authority/runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- v4.1.16 extracted release: `/share/Docker/cos-mcp/releases/v4.1.16`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases` for staging and execution. The ZIP creates `v4.1.16/` during extraction. Do not manually create the version directory, copy helpers into `/share/Docker`, or chmod the bundle before running scripts with `sh`.

## Pre-deploy backup behavior

Deployment backs up state whenever an existing `mesh-cos-mcp` container exists.

- Stable `status=running` and `.State.Restarting=false`: online SQLite backup through the existing container.
- `restarting`, `exited`, or other non-stable existing state: quiesced helper backup.
- A restarting runtime is stopped before SQLite state is read and its prior running intent is restored after the backup attempt.
- The one-shot helper uses the exact active Mesh image, `--network none`, non-root UID/GID, read-only root filesystem, dropped capabilities, `no-new-privileges`, and no protected Slack/tunnel secret mounts.
- The canonical SQLite helper uses SQLite backup semantics and `PRAGMA integrity_check` before acceptance.
- Failed backup/export attempts remove temporary/partial backup state and fail closed.

This specifically handles the QNAP Docker 27 condition where `.State.Running=true` can coexist with `.State.Status=restarting`.

## Slack identity and credentials

The governed human approver is Michael/MK. The verified Slack user ID is `U01KG3CNYHK`. Slack `D...` values are conversation IDs and are not valid human principals.

v4.1.16 retains the v4.1.15 split: connected Slack is collaboration-only; the custom Slack app is authenticated `/mesh-approval` Socket Mode ingress.

The QNAP runtime requires only the protected approver identity file and protected Slack Socket Mode app-level token beginning `xapp-`. A Slack `xoxb-` verifier bot token is not required, mounted, validated, prompted for, or used.

If the Socket Mode credential is missing or invalid:

```sh
sudo sh ./v4.1.16/mesh-cos-slack-hitl-provision.sh
```

If the OpenAI tunnel runtime key is missing:

```sh
sudo sh ./v4.1.16/mesh-cos-tunnel-key-provision.sh
```

## Artifact layout

The archive contains one top-level directory:

```text
v4.1.16/
```

Extracting `mesh-cos-mcp-qnap-v4.1.16.zip` under the canonical releases root creates `/share/Docker/cos-mcp/releases/v4.1.16` automatically.

## Network topology

- `mesh-cos-private` is internal-only on `172.30.60.0/29`.
- MCP uses `172.30.60.2` privately and qnet `lan7` address `192.168.7.60` as its only external-capable network.
- Tunnel is trusted MCP source `172.30.60.3` and uses dedicated egress `172.30.61.2` for OpenAI control-plane traffic.
- No direct MCP host port is published.

## Upgrade behavior

`mesh-cos-mcp-deploy.sh` performs:

1. release-root and staged metadata validation;
2. pre-deploy state/configuration backup for any existing `mesh-cos-mcp`, selecting online or quiesced mode from actual Docker status;
3. candidate preparation from staged metadata/build context;
4. minimal Slack HITL identity/Socket Mode credential validation;
5. staged-candidate QNAP preflight;
6. candidate Compose render/deployment;
7. application/tunnel health wait;
8. snapshot of active `.env`, Compose, and release metadata;
9. candidate active-configuration promotion;
10. governed MCP post-deploy verification;
11. promotion transaction commit and rollback-snapshot cleanup;
12. post-deploy backup.

If candidate activation or health fails before promotion, the previously active stack is restored when available. If active-file promotion is partial or post-deploy verification fails, the exact pre-promotion configuration snapshot is restored and the previously active stack is restarted. If rollback itself is incomplete, the recovery snapshot is preserved.

## Safe v4.1.16 deployment

Place these assets directly in `/share/Docker/cos-mcp/releases`:

- `mesh-cos-mcp-qnap-v4.1.16.zip`
- `mesh-cos-mcp-qnap-v4.1.16.zip.sha256`

Then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.16.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.16.zip
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

If deployment reports a missing Socket Mode credential:

```sh
sudo sh ./v4.1.16/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

Only if preparation reports a missing OpenAI tunnel key:

```sh
sudo sh ./v4.1.16/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.1.16/mesh-cos-mcp-deploy.sh
```

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.16/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.1.16/mesh-cos-mcp-preflight.sh
sudo sh ./v4.1.16/mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release `4.1.16`, application image `mesh-cos-mcp:qnap-v4.1.16`, both containers healthy, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.16
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

Do not print protected Slack or tunnel files.

## Failure diagnostics

Do not delete or recreate state after a failure:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

A successful pre-deploy backup from a restarting source should record `state_export_method=quiesced_helper`. Preserve any `.release-rollback.*` snapshot reported by a failed transactional rollback.

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file.

## Post-upgrade acceptance

After local deployment passes:

1. run `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app;
2. run `chatgpt-published-app-production-acceptance-v4.1.16.md`;
3. reconcile the TaskLedger operating mirror when the exact source connector is available.

Repository-green v4.1.16 is not production certification. Production acceptance requires the actual QNAP serving instance and live hosted checks.