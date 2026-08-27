# Short QNAP Deployment and Upgrade Steps

v4.2.3 preserves the v4.2.2 Slack GET/query provider transport repair and adds bounded QNAP/qnet external-egress readiness handling to the live Slack provider-read deployment gate. The canonical Phase 1 MCP runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- extracted release: `/share/Docker/cos-mcp/releases/v4.2.3`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases`. The ZIP creates `v4.2.3/` during extraction.

## Slack prerequisites

The dedicated Slack bot must be installed in `#mesh-agent-ops` with Bot Token Scopes `chat:write` and `groups:history`. The provider-verified Slack App ID is `A0B49RNE4K0`. Socket Mode, Slack interactivity, and QNAP message-event subscriptions remain disabled.

If `groups:history` was newly added, reinstall/reauthorize the Slack app and reprovision the resulting `xoxb-` Bot User OAuth Token before deployment. The protected approver identity remains unchanged. An `xapp-` Slack Socket Mode token is not used and must not be configured.

v4.2.3 deployment verification actively tests the mounted bot token and freshly recreated qnet namespace against the governed private channel. Only pre-provider network exceptions are retried, up to six total attempts with five-second inter-attempt delay. A Slack `ok:false` response, malformed provider response, invalid bot token, missing scope, or missing channel access fails immediately.

## Safe v4.2.3 deployment

Place `mesh-cos-mcp-qnap-v4.2.3.zip` and `mesh-cos-mcp-qnap-v4.2.3.zip.sha256` directly in `/share/Docker/cos-mcp/releases`, then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.2.3.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.2.3.zip
sudo sh ./v4.2.3/mesh-cos-mcp-deploy.sh
```

If deployment reports a genuinely missing or invalid Slack bot credential, or an authorized bot-token rotation is required:

```sh
sudo env MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh ./v4.2.3/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.2.3/mesh-cos-mcp-deploy.sh
```

Only if preparation reports a missing OpenAI tunnel key:

```sh
sudo sh ./v4.2.3/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.2.3/mesh-cos-mcp-deploy.sh
```

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.2.3/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.2.3/mesh-cos-mcp-preflight.sh
sudo sh ./v4.2.3/mesh-cos-mcp-verify.sh
```

PASS includes `Slack bot provider read scope, governed-channel access, and qnet egress readiness`.

## Local post-deploy checks

```sh
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires active release `4.2.3`, application image `mesh-cos-mcp:qnap-v4.2.3`, healthy application/tunnel containers, successful live Slack provider-read/qnet readiness verification, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.2.3
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
```

Do not print protected Slack or tunnel files.

## ChatGPT Work dispatcher

Do not create a new dispatcher and do not pin it to this patch release. Keep the existing **Mesh Slack HITL Dispatcher** trigger and condition unchanged and retain the prompt label:

`Act as the production Mesh Slack HITL Dispatcher for Mesh CoS MCP v4.x.`

The dispatcher must continue to pass only `thread_ts` and `message_ts` and must never interpret or forward Slack approval text or asserted authority.

## Failure diagnostics

Do not delete or recreate state after a failure:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

A network-readiness retry may log only attempt metadata. Slack provider failures expose only a sanitized code, not the bot token, Authorization header, provider response body, or response metadata.

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`.

Rollback must use a complete prior immutable release unit. v4.2.1 contains a confirmed Slack provider transport defect. v4.2.2 contains the transport repair but was blocked on this QNAP by the fresh qnet egress-readiness race. Do not combine release units and do not re-enable Socket Mode.

## Post-upgrade acceptance

After local deployment and live provider-read/qnet readiness verification pass, keep the dispatcher version-family prompt unchanged and execute `docs/chatgpt-published-app-production-acceptance-v4.2.3.md`. Start with a fresh synthetic provider text `*APPROVE*` case, verify replay idempotency, then complete the DENY, CHANGE, and negative security matrix with final audit-chain verification.
