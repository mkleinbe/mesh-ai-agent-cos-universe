# Short QNAP Deployment and Upgrade Steps

v4.1.14 removes hidden protected-secret entry from the ordinary QNAP deployment path after a real v4.1.13 upgrade failed at Slack verifier-token configuration with a mandatory `stty` dependency. The canonical Phase 1 authority/runtime contract remains **4.0.0**. The v4.1.13 governed approver, v4.1.12 release-root contract, and v4.1.10 scheduled-execution/Slack HITL trust model remain unchanged.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- v4.1.14 extracted release: `/share/Docker/cos-mcp/releases/v4.1.14`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

**The operator stays in `/share/Docker/cos-mcp/releases` for release staging and execution.** The ZIP creates `v4.1.14/` during extraction. Do not manually create the version directory, copy or move release payload files, copy helpers to `/share/Docker`, or chmod scripts before running them with `sh`.

## Protected identity and credentials

The governed human approver is Michael/MK. The verified Slack **user ID** is `U01KG3CNYHK`. Slack `D...` values are direct-message/conversation channel IDs and are not valid human principals.

Normal upgrades do not ask for the approver user ID, Slack verifier bot token, Slack Socket Mode app token, or OpenAI tunnel runtime key. Existing protected files are validated/preserved.

If a Slack verifier or Socket Mode credential is missing or invalid, deployment fails closed and instructs the operator to run:

```sh
sudo sh ./v4.1.14/mesh-cos-slack-hitl-provision.sh
```

If the OpenAI tunnel runtime key is missing, preparation fails closed and instructs the operator to run:

```sh
sudo sh ./v4.1.14/mesh-cos-tunnel-key-provision.sh
```

These explicit provisioning commands read secrets only from the controlling TTY using a no-echo mechanism, never place secret values on the command line, and normalize protected files to runtime ownership/mode.

## Artifact layout

The release archive contains one top-level directory:

```text
v4.1.14/
```

Therefore, extracting `mesh-cos-mcp-qnap-v4.1.14.zip` from `/share/Docker/cos-mcp/releases` automatically creates `/share/Docker/cos-mcp/releases/v4.1.14`.

## Upgrade behavior

`mesh-cos-mcp-deploy.sh` performs, in order:

1. release-root and staged metadata validation;
2. pre-deploy online backup when the current service is running;
3. candidate preparation from staged metadata/build context, preserving the existing tunnel key;
4. protected Slack HITL validation/preservation using the governed approver user ID and staged candidate image;
5. staged-candidate QNAP preflight;
6. candidate Compose render/deployment;
7. application/tunnel health wait;
8. atomic promotion of candidate `.env`, Compose, and release metadata to the canonical application root;
9. governed MCP verification;
10. post-deploy backup.

The canonical TaskLedger, existing Secure MCP `tunnel_id`, tunnel runtime key, Slack HITL protected files, qnet/static networking, and active runtime descriptors remain outside the versioned release folder and are preserved through upgrade.

## Safe v4.1.14 deployment

Place these two release assets directly in `/share/Docker/cos-mcp/releases`:

- `mesh-cos-mcp-qnap-v4.1.14.zip`
- `mesh-cos-mcp-qnap-v4.1.14.zip.sha256`

Then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.14.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.14.zip
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

If deployment stops because a protected Slack credential is missing, run the Slack provisioner and rerun the normal deployment:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

The existing production tunnel key should be preserved. Only if preparation explicitly reports that it is missing, run:

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.1.14/mesh-cos-mcp-deploy.sh
```

No `MESH_COS_DEPLOYMENT_RELEASE` environment variable needs to survive `sudo`; release identity comes from staged metadata.

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.14/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.1.14/mesh-cos-mcp-preflight.sh
sudo sh ./v4.1.14/mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release identity `4.1.14`, application image `mesh-cos-mcp:qnap-v4.1.14`, both containers healthy, `slack_hitl_ready=true`, and the governed response envelope:

```text
mcp_version: 4.0.0
deployment_release: 4.1.14
agent_id: cos
```

Do not print protected Slack or tunnel files as an acceptance check.

## Intentional credential replacement

Use the dedicated provisioners rather than forcing the ordinary deploy configurator. For Slack credentials:

```sh
cd /share/Docker/cos-mcp/releases
sudo env MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh ./v4.1.14/mesh-cos-slack-hitl-provision.sh
```

For the tunnel runtime key:

```sh
cd /share/Docker/cos-mcp/releases
sudo env MESH_COS_FORCE_TUNNEL_KEY_RECONFIGURE=1 sh ./v4.1.14/mesh-cos-tunnel-key-provision.sh
```

## Failure diagnostics

Do not delete or recreate state after a failure. Capture the durable diagnostic log:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

The log must not contain tunnel or Slack credential values.

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file and do not delete the v4.1.14 release directory while investigating a failed deployment.

## Post-upgrade acceptance

After local deployment passes:

1. run `CHATGPT-ACCEPTANCE.md` through the installed **Mesh CoS MCP** app;
2. run `chatgpt-published-app-production-acceptance-v4.1.14.md` for roster/catalog, audit, official OpenAI bot notice, verified human approver identity, and `/mesh-approval` Socket Mode acceptance;
3. reconcile the TaskLedger operating mirror when the exact source connector is available.

Repository-green v4.1.14 is not production certification. Production acceptance requires the actual QNAP serving instance and hosted checks to pass.
