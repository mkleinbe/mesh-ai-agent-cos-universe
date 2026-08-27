# Short QNAP Deployment and Upgrade Steps

v4.2.0 replaces QNAP-hosted Slack Socket Mode approval ingress with ChatGPT-native Slack new-message task triggers. The canonical Phase 1 MCP runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- extracted release: `/share/Docker/cos-mcp/releases/v4.2.0`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases`. The ZIP creates `v4.2.0/` during extraction.

## Slack prerequisites

Apply `slack-app-manifest.v4.2.0.json` to the dedicated **ChatGPT Enterprise AI Agent** bot if needed and ensure the bot is a member of `#mesh-agent-ops` (`C0BRL4GCL3A`). The v4.2.0 bot manifest requires `chat:write` and `groups:history`, disables Socket Mode and Slack interactivity, and does not subscribe the QNAP bot to Slack message events.

The QNAP runtime requires two protected Slack bindings:

1. the governed human approver user ID mapped to canonical principal `michael`;
2. the `xoxb-` bot OAuth token used for bot-authored notices and server-side provider reconciliation.

An `xapp-` Slack Socket Mode token is not used by v4.2.0 and must not be configured in the candidate runtime.

If the existing valid bot token and approver ID are already present, preserve them. Only if the bot credential is genuinely missing or invalid:

```sh
sudo sh ./v4.2.0/mesh-cos-slack-hitl-provision.sh
```

If the OpenAI tunnel runtime key is missing:

```sh
sudo sh ./v4.2.0/mesh-cos-tunnel-key-provision.sh
```

## Safe v4.2.0 deployment

Place `mesh-cos-mcp-qnap-v4.2.0.zip` and `mesh-cos-mcp-qnap-v4.2.0.zip.sha256` directly in `/share/Docker/cos-mcp/releases`, then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.2.0.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.2.0.zip
sudo sh ./v4.2.0/mesh-cos-mcp-deploy.sh
```

Only if deployment reports a genuinely missing or invalid Slack bot credential:

```sh
sudo sh ./v4.2.0/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.2.0/mesh-cos-mcp-deploy.sh
```

Only if preparation reports a missing OpenAI tunnel key:

```sh
sudo sh ./v4.2.0/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.2.0/mesh-cos-mcp-deploy.sh
```

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.2.0/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.2.0/mesh-cos-mcp-preflight.sh
sudo sh ./v4.2.0/mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release `4.2.0`, application image `mesh-cos-mcp:qnap-v4.2.0`, healthy application/tunnel containers, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.2.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
```

Do not print protected Slack or tunnel files.

## ChatGPT-native dispatcher provisioning

QNAP deployment does not create the ChatGPT event-triggered task. In the ChatGPT environment that supports native Slack event triggers, create exactly one Mesh Slack HITL Dispatcher using `docs/chatgpt-native-slack-dispatcher-v4.2.0.md`.

Preferred filter:

- new Slack channel message;
- channel `C0BRL4GCL3A`;
- sender `U01KG3CNYHK`;
- thread replies, if that filter is available.

The dispatcher passes only Slack thread/message locators to Mesh CoS MCP. It must never pass decision text or asserted authority.

## Failure diagnostics

Do not delete or recreate state after a failure:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`. Do not replace the canonical TaskLedger with an unverified file.

Rollback must use the complete prior immutable v4.1.18 release unit and disable the v4.2.0 native Slack dispatcher task. Do not combine v4.2.0 code with the retired v4.1.17 Socket Mode configuration.

## Post-upgrade acceptance

After local deployment passes and the native dispatcher exists, execute `docs/chatgpt-published-app-production-acceptance-v4.2.0.md`. Production acceptance requires the actual QNAP serving instance, live Secure MCP Tunnel path, real ChatGPT native Slack trigger, server-side Slack reconciliation, synthetic positive/negative approval cases, idempotency, and final audit-chain verification.