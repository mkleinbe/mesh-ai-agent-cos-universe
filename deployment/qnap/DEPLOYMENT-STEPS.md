# Short QNAP Deployment and Upgrade Steps

v4.1.18 is the protected Slack bot credential permission hotfix for the v4.1.17 dedicated **ChatGPT Enterprise AI Agent** Slack bot, Block Kit buttons, and authenticated thread replies. The canonical Phase 1 MCP runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- extracted release: `/share/Docker/cos-mcp/releases/v4.1.18`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases`. The ZIP creates `v4.1.18/` during extraction.

## Slack prerequisite

The v4.1.17 Slack manifest remains the governing behavior manifest. Apply `slack-app-manifest.v4.1.17.json` if not already applied, reinstall/re-authorize the app for the required private-channel history scope, enable Socket Mode/interactivity, and ensure **ChatGPT Enterprise AI Agent** is a member of `mesh-agent-ops`.

The QNAP runtime requires three protected bindings: the human approver ID, an `xapp-` Socket Mode app token, and an `xoxb-` bot OAuth token. The retired verifier token and `/mesh-approval` slash command are not used.

If a valid `slack-bot-token` was already provisioned during the failed v4.1.17 deployment, **do not re-enter it**. v4.1.18 repairs the protected file ownership automatically while retaining mode `0400`.

Only if Slack credentials are genuinely missing or invalid:

```sh
sudo sh ./v4.1.18/mesh-cos-slack-hitl-provision.sh
```

If the OpenAI tunnel runtime key is missing:

```sh
sudo sh ./v4.1.18/mesh-cos-tunnel-key-provision.sh
```

## Safe v4.1.18 deployment

Place `mesh-cos-mcp-qnap-v4.1.18.zip` and `mesh-cos-mcp-qnap-v4.1.18.zip.sha256` directly in `/share/Docker/cos-mcp/releases`, then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.1.18.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.1.18.zip
sudo sh ./v4.1.18/mesh-cos-mcp-deploy.sh
```

Only if deployment reports a genuinely missing or invalid Slack credential:

```sh
sudo sh ./v4.1.18/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.1.18/mesh-cos-mcp-deploy.sh
```

Only if preparation reports a missing OpenAI tunnel key:

```sh
sudo sh ./v4.1.18/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.1.18/mesh-cos-mcp-deploy.sh
```

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.1.18/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.1.18/mesh-cos-mcp-preflight.sh
sudo sh ./v4.1.18/mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release `4.1.18`, application image `mesh-cos-mcp:qnap-v4.1.18`, healthy application/tunnel containers, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.18
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

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file.

## Post-upgrade acceptance

After local deployment passes, run `CHATGPT-ACCEPTANCE.md` and `chatgpt-published-app-production-acceptance-v4.1.18.md`. Production acceptance requires the actual QNAP serving instance and live Slack HITL checks.
