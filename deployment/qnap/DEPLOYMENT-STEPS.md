# Short QNAP Deployment and Upgrade Steps

v4.2.1 patches the ChatGPT-native Slack HITL provider-decision parser introduced in v4.2.0. The canonical Phase 1 MCP runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- extracted release: `/share/Docker/cos-mcp/releases/v4.2.1`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases`. The ZIP creates `v4.2.1/` during extraction.

## Slack prerequisites

The v4.2.1 Slack app manifest is unchanged in privilege from v4.2.0 and requires only `chat:write` and `groups:history`. Socket Mode, Slack interactivity, and QNAP message event subscriptions remain disabled.

The existing production `xoxb-` bot OAuth token and protected approver identity should be preserved. v4.2.1 introduces no new Slack OAuth scope and does not require Slack reauthorization when the existing app already has the v4.2.0/v4.1.17 scope set.

An `xapp-` Slack Socket Mode token is not used and must not be configured.

## Safe v4.2.1 deployment

Place `mesh-cos-mcp-qnap-v4.2.1.zip` and `mesh-cos-mcp-qnap-v4.2.1.zip.sha256` directly in `/share/Docker/cos-mcp/releases`, then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.2.1.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.2.1.zip
sudo sh ./v4.2.1/mesh-cos-mcp-deploy.sh
```

Only if deployment reports a genuinely missing or invalid Slack bot credential:

```sh
sudo sh ./v4.2.1/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.2.1/mesh-cos-mcp-deploy.sh
```

Only if preparation reports a missing OpenAI tunnel key:

```sh
sudo sh ./v4.2.1/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.2.1/mesh-cos-mcp-deploy.sh
```

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.2.1/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.2.1/mesh-cos-mcp-preflight.sh
sudo sh ./v4.2.1/mesh-cos-mcp-verify.sh
```

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release `4.2.1`, application image `mesh-cos-mcp:qnap-v4.2.1`, healthy application/tunnel containers, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.2.1
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
```

Do not print protected Slack or tunnel files.

## ChatGPT Work dispatcher

Do not create a new dispatcher. Keep the existing **Mesh Slack HITL Dispatcher** trigger and condition unchanged. Edit only the task prompt's release label from `v4.2.0` to `v4.2.1` using `docs/chatgpt-native-slack-dispatcher-v4.2.1.md`.

The dispatcher must continue to pass only `thread_ts` and `message_ts` and must never interpret Slack approval text.

## Failure diagnostics

Do not delete or recreate state after a failure:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`.

Rollback must use the complete prior immutable v4.2.0 release unit. If rolling back because HITL acceptance fails, disable the native Slack dispatcher until the failure is classified. Do not combine release units and do not re-enable Socket Mode.

## Post-upgrade acceptance

After local deployment passes and the existing dispatcher prompt is labeled v4.2.1, execute `docs/chatgpt-published-app-production-acceptance-v4.2.1.md`. The first live case must reproduce provider text `*APPROVE*`, followed by the complete positive/negative/idempotency matrix and final audit-chain verification.
