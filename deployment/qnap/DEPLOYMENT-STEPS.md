# Short QNAP Deployment and Upgrade Steps

v4.1.15 simplifies Slack HITL, fixes QNAP Docker Engine 27 egress ambiguity, and makes release promotion recoverable through post-deploy verification. The canonical Phase 1 authority/runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- v4.1.15 extracted release: `/share/Docker/cos-mcp/releases/v4.1.15`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases` for staging and execution. The ZIP creates `v4.1.15/` during extraction. Do not manually create the version directory, copy helpers into `/share/Docker`, or chmod the bundle before running scripts with `sh`.

## Slack identity and credentials

The governed human approver is Michael/MK. The verified Slack user ID is `U01KG3CNYHK`. Slack `D...` values are conversation IDs and are not valid human principals.

v4.1.15 uses the connected Slack integration for collaboration and one custom Slack app boundary for authenticated `/mesh-approval` Socket Mode ingress.

The QNAP runtime requires only:

- protected approver identity file;
- protected Slack Socket Mode app-level token beginning `xapp-`.

A Slack `xoxb-` verifier bot token is **not required, mounted, validated, prompted for, or used** by v4.1.15. A legacy verifier file may remain on the host solely to permit rollback to an older release.

Normal upgrades do not ask for the approver user ID, Socket Mode app token, or OpenAI tunnel runtime key when the protected files already exist.

If the Socket Mode credential is missing or invalid, deployment fails closed and directs the operator to:

```sh
sudo sh ./v4.1.15/mesh-cos-slack-hitl-provision.sh
```

If the OpenAI tunnel runtime key is missing:

```sh
sudo sh ./v4.1.15/mesh-cos-tunnel-key-provision.sh
```

Explicit provisioners read secrets only from the controlling TTY using no-echo input, never put secret values on the command line, and normalize protected files to runtime ownership/mode.

## Artifact layout

The archive contains one top-level directory:

```text
v4.1.15/
```

Extracting `mesh-cos-mcp-qnap-v4.1.15.zip` under the canonical releases root therefore creates `/share/Docker/cos-mcp/releases/v4.1.15` automatically.

## Network topology

v4.1.15 avoids relying on newer Compose gateway-priority features that are not part of the QNAP Docker Engine 27 baseline.

- `mesh-cos-private` is an internal-only bridge on `172.30.60.0/29`.
- MCP uses `172.30.60.2` privately and retains qnet `lan7` address `192.168.7.60` as its only external-capable network.
- The tunnel remains the trusted MCP source at `172.30.60.3` and receives a dedicated egress bridge address `172.30.61.2` for OpenAI control-plane traffic.
- No second qnet LAN address is consumed by the tunnel.
- No direct MCP host port is published.

## Upgrade behavior

`mesh-cos-mcp-deploy.sh` performs:

1. release-root and staged metadata validation;
2. pre-deploy online backup when the current service is running;
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

If candidate activation or health fails before promotion, the previously active stack is restored when available. If active-file promotion is partial or post-deploy verification fails, the exact pre-promotion configuration snapshot is restored and the previously active stack is restarted. If rollback itself is incomplete, the recovery snapshot is preserved for operator recovery.

The canonical TaskLedger, Secure MCP tunnel identity/key, Slack protected files, qnet/static identity, logs, and backups remain outside the versioned release folder.

## Safe v4.1.15 deployment

Place these assets directly in `/share/Docker/cos-mcp/releases`:

- `mesh-cos-mcp-qnap-v4.1.15.zip`
- `mesh-cos-mcp-qnap-v4.1.15.zip.sha256`

Then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.15.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.15.zip
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

If deployment reports a missing Socket Mode credential:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.15/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

Only if preparation explicitly reports a missing OpenAI tunnel key:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.15/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

Release identity comes from staged metadata; no `MESH_COS_DEPLOYMENT_RELEASE` variable needs to survive `sudo`.

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.15/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.1.15/mesh-cos-mcp-preflight.sh
sudo sh ./v4.1.15/mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release `4.1.15`, application image `mesh-cos-mcp:qnap-v4.1.15`, both containers healthy, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.15
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

Do not print protected Slack or tunnel files.

## Intentional credential replacement

Slack Socket Mode token:

```sh
cd /share/Docker/cos-mcp/releases
sudo env MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh ./v4.1.15/mesh-cos-slack-hitl-provision.sh
```

Tunnel runtime key:

```sh
cd /share/Docker/cos-mcp/releases
sudo env MESH_COS_FORCE_TUNNEL_KEY_RECONFIGURE=1 sh ./v4.1.15/mesh-cos-tunnel-key-provision.sh
```

## Failure diagnostics

Do not delete or recreate state after a failure. Capture the durable diagnostic log:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

If a failed transactional rollback reports a preserved `.release-rollback.*` snapshot, retain it until recovery is complete. Do not delete that directory during investigation.

The deployment log must not contain Slack or tunnel credential values.

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file.

## Post-upgrade acceptance

After local deployment passes:

1. run `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app;
2. run `chatgpt-published-app-production-acceptance-v4.1.15.md` for hosted roster/catalog, Slack collaboration-only handoff, authenticated `/mesh-approval`, canonical approval readback, replay denial, and no unauthorized external action;
3. reconcile the TaskLedger operating mirror when the exact source connector is available.

Repository-green v4.1.15 is not production certification. Production acceptance requires the actual QNAP serving instance and live hosted checks.
