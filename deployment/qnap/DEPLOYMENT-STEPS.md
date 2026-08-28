# Short QNAP Deployment and Upgrade Steps

v4.3.0 adds governed cross-agent owner execution for PF-057 while preserving the v4.2.3 Slack/qnet provider-read and transactional deployment controls. The canonical Phase 1 MCP authority/runtime contract remains **4.0.0**.

## Canonical paths

- operator release root: `/share/Docker/cos-mcp/releases`
- extracted release: `/share/Docker/cos-mcp/releases/v4.3.0`
- active application root: `/share/Docker/cos-mcp`
- canonical state: `/share/Docker/cos-mcp/state`
- canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- protected secrets: `/share/Docker/cos-mcp/secrets`
- deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- backups: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Stay in `/share/Docker/cos-mcp/releases`. The ZIP creates `v4.3.0/` during extraction.

## Pre-deploy requirements

- exact v4.3.0 candidate CI is green, including 100% Python coverage, owner execution readiness, QNAP bundle/container provenance, modern MCP transport, and security gates;
- human merge/release/deployment authority is valid;
- protected Slack/tunnel credentials and canonical TaskLedger are preserved;
- the existing ChatGPT Work **Mesh Slack HITL Dispatcher** remains one event-triggered locator-only bridge labeled `Mesh CoS MCP v4.x`;
- the dedicated Slack bot remains installed in `#mesh-agent-ops` with `chat:write` and `groups:history`, App ID `A0B49RNE4K0`;
- no `xapp-` Socket Mode credential is configured.

## Safe v4.3.0 deployment

Place `mesh-cos-mcp-qnap-v4.3.0.zip` and `mesh-cos-mcp-qnap-v4.3.0.zip.sha256` directly in `/share/Docker/cos-mcp/releases`, then run:

```sh
cd /share/Docker/cos-mcp/releases
sha256sum -c mesh-cos-mcp-qnap-v4.3.0.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.3.0.zip
sudo sh ./v4.3.0/mesh-cos-mcp-deploy.sh
```

If deployment reports a genuinely missing or invalid Slack bot credential, or an authorized bot-token rotation is required:

```sh
sudo env MESH_COS_FORCE_SLACK_HITL_RECONFIGURE=1 sh ./v4.3.0/mesh-cos-slack-hitl-provision.sh
sudo sh ./v4.3.0/mesh-cos-mcp-deploy.sh
```

Only if preparation reports a missing OpenAI tunnel key:

```sh
sudo sh ./v4.3.0/mesh-cos-tunnel-key-provision.sh
sudo sh ./v4.3.0/mesh-cos-mcp-deploy.sh
```

## Optional explicit checks

```sh
cd /share/Docker/cos-mcp/releases
sudo sh ./v4.3.0/mesh-cos-mcp-backup.sh manual
sudo sh ./v4.3.0/mesh-cos-mcp-preflight.sh
sudo sh ./v4.3.0/mesh-cos-mcp-verify.sh
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

PASS requires active release `4.3.0`, application image `mesh-cos-mcp:qnap-v4.3.0`, healthy application/tunnel containers, successful live Slack provider-read/qnet readiness verification, `slack_hitl_ready=true`, and:

```text
mcp_version: 4.0.0
deployment_release: 4.3.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
```

Do not print protected Slack or tunnel files.

## Delegated owner acceptance

After local runtime readiness passes, use only synthetic, non-consequential tasks to prove:

1. the CoS can execute its own governed work normally;
2. each ACTIVE direct-report owner eligible for delegated work has a valid `delegation.execute_owner` route;
3. CMO -> VP Content works through canonical nested delegation;
4. COO -> Consultant Network Steward works through canonical nested delegation;
5. CoS direct `task.complete` against a child-owned task is denied;
6. the child owner can complete its own task exactly once;
7. replay with the same idempotency key returns the canonical result without a second execution/audit write;
8. disabled/quarantined/unroutable owners fail closed;
9. approvals and Message Operations boundaries remain inherited and enforced;
10. `COMPLETED != VERIFIED` remains enforced.

Then execute `docs/chatgpt-published-app-production-acceptance-v4.3.0.md`.

## Failure diagnostics

Do not delete or recreate state after a failure:

```sh
LOG=$(cat /share/Docker/cos-mcp/logs/deployment/LATEST)
printf 'LOG=%s\n' "$LOG"
cat "$LOG"
```

Network-readiness retries may log only attempt metadata. Slack provider failures expose only a sanitized code, not the bot token, Authorization header, provider response body, or response metadata. Delegated-owner failures must preserve the canonical task/delegation and emit bounded routing/audit evidence without changing owner identity.

## Rollback

Use the most recent successful `pre-deploy` backup under `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`. Follow `rollback-checklist.md` and `backup-restore.md`.

Rollback uses a complete prior immutable release unit. Do not combine release units. Software rollback must not delete or rewrite canonical PF-057 tasks. If v4.3.0 is rolled back before recovery, leave stranded tasks in their existing state until a corrected transport is authorized.

## PF-057 recovery

Only after production acceptance passes, re-run the read-only stranded-task inventory and resume eligible tasks in place. Do not recreate `task-b0b613daff51`; validate its canonical CMO ownership and use the governed CMO completion route, followed by separate verification where required.
