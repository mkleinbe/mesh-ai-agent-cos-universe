# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.3.0 Cross-Agent Owner Execution.**  
**Canonical Phase 1 authority/runtime contract: 4.0.0.**

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` retains `192.168.7.60` on verified QNAP `lan7` qnet and `172.30.60.2` on the internal MCP/tunnel bridge. The tunnel remains the trusted MCP source at `172.30.60.3` and uses a dedicated Docker egress bridge at `172.30.61.2` for OpenAI control-plane traffic.

The shared `mesh-cos-private` bridge is `internal: true`. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

## v4.3.0 delegated owner execution

v4.3.0 adds the governed `delegation.execute_owner` operation and repairs PF-057 across the full Phase 1 workforce. The external MCP process remains bound to `MESH_COS_AGENT_ID=cos`; that transport identity is immutable and is not treated as child authority.

For delegated work, the server:

1. reads the canonical delegation and task;
2. derives the accountable owner from TaskLedger and Agent Registry state;
3. validates ancestry, delegation depth, permissions, approval constraints, owner status, and owner tool allowlist;
4. executes the permitted operation through the trusted server-owned owner executor;
5. records owner-scoped audit and idempotency evidence;
6. permits `task.complete` only under the canonical accountable owner;
7. keeps verification separate from completion.

The request schema contains no caller-selectable owner or principal. Prompt text, task metadata, depth hints, ancestry hints, and asserted authority cannot select the execution principal.

The governed CoS catalog contains 28 agent tools, including `delegation.execute_owner`. Human-only `approval.record_decision` and `reliability.human_override` remain unavailable to agents.

## Native Slack HITL boundary

Slack approval collaboration and human authority remain separated:

- the dedicated **ChatGPT Enterprise AI Agent** bot posts governed approval notices in `#mesh-agent-ops`;
- a single ChatGPT Work **Mesh Slack HITL Dispatcher** wakes on new MK messages/thread replies and passes only `thread_ts` and `message_ts`;
- the Work trigger is not approval authority;
- QNAP independently rereads the exact Slack provider message with `conversations.replies`, verifies provider identity and manual authorship, validates canonical approval state and fingerprint, and only then records authority.

The dispatcher prompt remains version-family labeled `Mesh CoS MCP v4.x`. It must never forward Slack text, asserted identity, decision, approval state, actor, principal, or consequential instructions.

QNAP does not run Slack Socket Mode, does not mount an `xapp-` credential, and does not own Slack event ingress.

## Slack application and credential

The provider-verified Slack App ID remains `A0B49RNE4K0`.

The dedicated bot requires Bot Token Scopes `chat:write` and `groups:history`. The protected `xoxb-` Bot User OAuth Token is stored under `/share/Docker/cos-mcp/secrets/slack-bot-token` and mounted read-only to the runtime. The protected MK approver identity is stored separately. Secret values are never written to `.env.runtime`, release bundles, logs, or TaskLedger.

The v4.2.3 Slack/qnet provider-read controls are retained unchanged in v4.3.0: provider reads use authenticated GET/query transport; only pre-provider qnet/network exceptions may retry; Slack `ok:false`, malformed response, invalid credential, missing scope, or missing channel access fails immediately and triggers transactional rollback when encountered during deployment verification.

## Canonical QNAP paths

- Operator release root: `/share/Docker/cos-mcp/releases`
- Current release directory: `/share/Docker/cos-mcp/releases/v4.3.0`
- Candidate payload: `/share/Docker/cos-mcp/releases/v4.3.0/cos-mcp`
- Candidate runtime environment: `/share/Docker/cos-mcp/releases/v4.3.0/cos-mcp/.env.runtime`
- Canonical application root: `/share/Docker/cos-mcp`
- Canonical state: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Protected secrets: `/share/Docker/cos-mcp/secrets`
- Deployment Docker config: `/share/Docker/cos-mcp/.docker-cli`
- Deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The operator remains in `/share/Docker/cos-mcp/releases` for staging and execution. The ZIP creates `v4.3.0/` automatically.

## Release-root and transactional promotion controls

1. The archive contains one top-level `v4.3.0/` directory.
2. Operator scripts self-resolve their own versioned release directory.
3. Deployment validates the release directory beneath the canonical releases root and matches it to staged metadata.
4. Existing runtime state is backed up before candidate preparation whenever the application exists.
5. Candidate release identity comes from staged metadata, not active `.env` or caller assumptions.
6. Candidate build context, Compose, and `.env.runtime` remain inside the versioned release directory.
7. Candidate containers must become healthy before active-file promotion.
8. Active `.env`, Compose, and release metadata are snapshotted before promotion.
9. Partial promotion or post-promotion verification failure restores the pre-promotion snapshot and prior stack when available.
10. Successful post-deploy verification, including live provider-read/qnet readiness, is the promotion transaction commit point.
11. Canonical TaskLedger, tunnel identity/key, Slack protected files, logs, and backups remain outside the release directory.

## Runtime controls

- `mesh-cos-mcp`: UID/GID 65532, 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- long-running containers: non-root, read-only root filesystem, capabilities dropped, no-new-privileges, no Docker socket, no host networking
- `MESH_COS_AGENT_ID=cos` is process-bound
- `MESH_COS_DEPLOYMENT_RELEASE=4.3.0` is required by the remote process
- `MESH_COS_SLACK_HITL_REQUIRED=true` and `MESH_COS_SLACK_HITL_MODE=CHATGPT_NATIVE_EVENT_TRIGGER` are required by production Compose
- protected approver identity and bot token are read-only runtime mounts
- `/healthz` remains available through provider degradation; authority reconciliation itself fails closed without provider evidence

Successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.3.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
```

Hosted production readiness additionally requires `slack_hitl_ready=true`, successful live Slack provider-read/qnet readiness verification, and representative delegated-owner execution acceptance.

## Authority boundary

The 10-agent roster, L4/L5 human authority, canonical TaskLedger, completion/verification separation, Message Operations boundary, and tunnel source-IP trust boundary remain governed. Message Operations remains agent 10. Mesh Devil's Advocate remains a governed shared Skill, not agent 11.

Direct reports and nested agents may execute only through registry-authorized canonical delegation. CoS cannot complete child-owned work directly. Nested delegation is supported only through canonical relationships such as CMO -> VP Content and COO -> Consultant Network Steward.

## QNAP deployment

After human authorization, from `/share/Docker/cos-mcp/releases`:

```sh
sha256sum -c mesh-cos-mcp-qnap-v4.3.0.zip.sha256
unzip -oq mesh-cos-mcp-qnap-v4.3.0.zip
sudo sh ./v4.3.0/mesh-cos-mcp-deploy.sh
```

Host-side sudo does not alter the long-running application identity, which remains UID/GID `65532:65532`.

## Persistence, backup, rollback, and observability

Stable runtimes use online SQLite backup. Restarting/non-running existing runtimes use the quiesced one-shot helper. Backup receipts include integrity evidence, non-secret configuration, image IDs, source container state, backup method, and SHA-256 checks. `secrets/` is never copied into backup artifacts.

Do not delete, recreate, or rewrite canonical tasks after a failed candidate. Use `rollback-checklist.md` and `backup-restore.md`. Deployment logs and diagnostics exclude credential contents, protected identity contents, generated environment contents, credential-bearing argv, and tunnel credentials.

## Operator flow

Use `DEPLOYMENT-STEPS.md`. After local deployment verification, run `CHATGPT-ACCEPTANCE.md` and `docs/chatgpt-published-app-production-acceptance-v4.3.0.md`. Repository/release verification is not production certification; the actual QNAP serving instance plus hosted ChatGPT, delegated-owner paths, and Slack acceptance must pass separately.
