# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.11 QNAP Versioned Release Staging Remediation.**  
**Canonical Phase 1 authority/runtime contract: 4.0.0.**

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` receives `192.168.7.60` on the verified QNAP `lan7` qnet network while the MCP/tunnel trust boundary uses dedicated bridge `172.30.60.0/29`.

The published **Mesh CoS MCP** ChatGPT app reaches `/mcp` only through the tunnel sidecar source address. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

Slack HITL uses two separate external surfaces: an official OpenAI Workspace Agent bot-authored notice and an outbound Slack Socket Mode connection for the `/mesh-approval` human interaction. Neither expands the agent-facing MCP catalog.

## Fixed QNAP paths and release staging

- Canonical application root: `/share/Docker/cos-mcp`
- Versioned release root pattern: `/share/Docker/cos-mcp/releases/vX.Y.Z`
- Current staged release root: `/share/Docker/cos-mcp/releases/v4.1.11`
- Candidate payload: `/share/Docker/cos-mcp/releases/v4.1.11/cos-mcp`
- Candidate runtime environment: `/share/Docker/cos-mcp/releases/v4.1.11/cos-mcp/.env.runtime`
- Canonical state: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Tunnel secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`
- Slack human-identity binding: `/share/Docker/cos-mcp/secrets/slack-approver-user-id`
- Slack provider-verifier credential: `/share/Docker/cos-mcp/secrets/slack-verifier-token`
- Slack Socket Mode app-level credential: `/share/Docker/cos-mcp/secrets/slack-socket-app-token`
- Deployment Docker config: `/share/Docker/cos-mcp/.docker-cli`
- Deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

Operator/helper scripts live at the versioned release root and self-resolve that root. They are not installed or copied into `/share/Docker`.

## Runtime controls

- `mesh-cos-mcp`: UID/GID 65532, 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- Long-running containers: non-root, read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, no host networking
- `MESH_COS_AGENT_ID=cos` is process-bound
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.11` is required by the remote process and passed through candidate Compose
- `MESH_COS_SLACK_HITL_REQUIRED=true` is required by production Compose
- Slack identity/verifier/Socket Mode files are mounted read-only
- `/readyz` fails when required Slack HITL verification or authenticated Socket Mode is unavailable

## v4.1.11 release-layout controls

1. Candidate release identity is read from staged `release-metadata.txt`, not the active `.env`.
2. Git tag form `vX.Y.Z` normalizes to runtime `X.Y.Z`; true mismatch still fails closed.
3. Preflight explicitly separates active production identity from the staged candidate identity.
4. The staged build context and Compose file stay in the release directory.
5. `mesh-cos-mcp-prepare.sh` generates staged `.env.runtime` and does not replace active `.env`.
6. Standard `sudo sh ./mesh-cos-mcp-deploy.sh` does not require sudo environment preservation for release identity.
7. Candidate containers start from the staged Compose/environment.
8. Active `.env`, `compose.yaml`, and `release-metadata.txt` are promoted only after both containers are healthy.
9. The pre-deploy online SQLite backup remains before preparation and post-deploy backup remains after verification.
10. Existing canonical state, tunnel secret, Slack protected configuration, qnet/static networking, and OCI provenance controls are preserved.

## v4.1.10 controls retained

v4.1.11 carries forward explicit scheduled idempotency, canonical lifecycle progression through QA before completion, separate verification, official OpenAI bot notice binding, protected human identity, provider readback, notice-only CoS Slack adapter, non-MCP Socket Mode `/mesh-approval`, rejection of ordinary Slack text as approval authority, protected Slack files, and fail-closed Slack HITL readiness.

Successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.11
agent_id: cos
```

`/healthz` and `/readyz` report the same identity plus `transport: SECURE_MCP_TUNNEL`. Hosted production readiness additionally requires `slack_hitl_ready=true`.

## Authority boundary

The dual version domains remain distinct:

- `mcp_version` identifies the canonical Phase 1 authority/runtime contract and remains `4.0.0`.
- `deployment_release` identifies the QNAP deployment release serving the request and is `4.1.11` after successful promotion.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification semantics, and tunnel source-IP trust boundary remain governed. Mesh Devil's Advocate remains a shared Skill, not agent 11.

## Docker privilege on this operator account

This QNAP operator account requires `sudo` for Docker access. From the versioned release directory invoke `sudo sh ./mesh-cos-mcp-deploy.sh`. Host-side sudo is only for Docker/Container Station authority. The long-running application remains UID/GID `65532:65532`.

## Persistence, backup, and rollback

The application creates online SQLite backups as runtime UID 65532. The host wrapper exports the completed backup using `docker cp`, then deletes the temporary file through `docker exec`. The backup share receives SQLite integrity evidence, non-secret configuration, image IDs, and SHA-256 receipts. `secrets/` is never copied.

Existing canonical TaskLedger state, Secure MCP `tunnel_id`, tunnel runtime-key file, protected Slack HITL files, and active descriptors are preserved during staging. A failed candidate before promotion does not justify deleting or recreating state. Use `rollback-checklist.md` and `backup-restore.md` with the verified pre-deploy backup.

## Deployment observability

Deploy, prepare, Slack HITL configure, preflight, verify, and backup share one timestamped log and run ID. Failures record stage, safe command classification, return code, component/script identity, and bounded QNAP/Docker/filesystem/container evidence.

The diagnostic contract does not collect secret contents, protected Slack identity contents, `.env` contents, process environments, credential-bearing argv, or tunnel logs.

## Operator flow

Use the complete SSH-safe **v4.1.11** versioned upgrade block in `DEPLOYMENT-STEPS.md`. Do not manually copy helper scripts into `/share/Docker`.

After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and `chatgpt-published-app-production-acceptance-v4.1.11.md`. Production certification requires the actual official OpenAI bot-authored synthetic HITL notice, proof ordinary Slack text cannot approve, live `/mesh-approval` Socket Mode interaction, fresh canonical approval readback, valid audit chain, no unauthorized external action, and required operating-mirror reconciliation.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
