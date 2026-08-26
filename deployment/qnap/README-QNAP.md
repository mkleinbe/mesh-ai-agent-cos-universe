# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.10 Scheduled Automation and Slack HITL Hardening.**  
**Canonical Phase 1 authority/runtime contract: 4.0.0.**

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` receives `192.168.7.60` on the verified QNAP `lan7` qnet network while the MCP/tunnel trust boundary uses dedicated bridge `172.30.60.0/29`.

The published **Mesh CoS MCP** ChatGPT app reaches `/mcp` only through the tunnel sidecar source address. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

Slack HITL uses two separate external surfaces: an official OpenAI Workspace Agent bot-authored notice and an outbound Slack Socket Mode connection for the `/mesh-approval` human interaction. Neither expands the agent-facing MCP catalog.

## Fixed QNAP paths

- Script root: `/share/Docker`
- Application root: `/share/Docker/cos-mcp`
- Build context: `/share/Docker/cos-mcp/build-context`
- Canonical state: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Tunnel secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`
- Slack human-identity binding: `/share/Docker/cos-mcp/secrets/slack-approver-user-id`
- Slack provider-verifier credential: `/share/Docker/cos-mcp/secrets/slack-verifier-token`
- Slack Socket Mode app-level credential: `/share/Docker/cos-mcp/secrets/slack-socket-app-token`
- Deployment Docker config: `/share/Docker/cos-mcp/.docker-cli`
- Deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The Slack human identity and both Slack credentials are protected runtime files, not release assets or `.env` values.

## Runtime controls

- `mesh-cos-mcp`: UID/GID 65532, 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- Long-running containers: non-root, read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, no host networking
- `MESH_COS_AGENT_ID=cos` is process-bound
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.10` is required by the remote process and passed explicitly through Compose
- `MESH_COS_SLACK_HITL_REQUIRED=true` is required by production Compose
- Slack identity/verifier/Socket Mode files are mounted read-only
- `/readyz` fails when required Slack HITL verification or the authenticated Socket Mode connection is unavailable

## v4.1.10 controls

v4.1.10 carries forward the v4.1.8 MCP request-contract remediation and v4.1.9 documentation closeout, and adds:

1. explicit scheduled `task.intake.idempotency_key` use;
2. valid scheduled lifecycle progression through `QA` before completion;
3. separate canonical verification after `COMPLETED`;
4. provider-verified official ChatGPT/ChatGPT Agents bot authorship for governed Slack HITL parent notices;
5. protected runtime human identity binding for canonical principal `michael`;
6. provider readback and exact Approval ID/fingerprint binding for the notice;
7. a notice-only CoS `slack-adapter` that cannot record or infer human decisions;
8. a separate non-MCP Slack Socket Mode `/mesh-approval` human-ingress service;
9. explicit rejection of ordinary Slack messages as human approval authority, including user-attributed application posts;
10. protected QNAP identity/verifier/Socket Mode file provisioning and mode/ownership enforcement;
11. runtime readiness failure when required Slack HITL controls cannot initialize or remain active;
12. current security/readiness documentation reconciled to the 10-agent Secure MCP Tunnel topology.

Successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.10
agent_id: cos
```

`/healthz` and `/readyz` report the same identity plus `transport: SECURE_MCP_TUNNEL`. Hosted production readiness additionally requires `slack_hitl_ready=true`.

## Slack HITL boundary

The generic user-scoped Slack connector is not the governed notice-author surface and is not the human-approval transport. Governed HITL notices must be provider-authored by the official ChatGPT or ChatGPT Agents Slack identity.

The server-owned verifier uses a protected bot credential only to read the bound Slack provider thread. It does not become the outbound HITL author. The CoS can bind verified notice evidence but cannot ingest a human decision.

Canonical Slack human decisions enter only through the authenticated Socket Mode `/mesh-approval` slash command. The non-MCP human-ingress service validates the governed channel, protected configured human identity, exact command and Approval ID, PENDING canonical approval, official OpenAI bot notice binding, exact fingerprint, and replay state before recording canonical principal `michael`.

An ordinary Slack message saying `APPROVE`, a reaction, copied text, or user-attributed application post is evidence only and cannot change canonical approval state.

If the official OpenAI Workspace Agent Slack delivery surface is unavailable, the notice action fails closed as `BLOCKED_CHATGPT_AGENT_TRANSPORT`. If Socket Mode is unavailable, approval remains PENDING. Neither case may fall back to posting or approving as MK.

## Authority boundary

The dual version domains remain distinct:

- `mcp_version` identifies the canonical Phase 1 authority/runtime contract and remains `4.0.0`.
- `deployment_release` identifies the QNAP deployment release serving the request and is `4.1.10` for this release.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification semantics, and tunnel source-IP trust boundary remain governed. Mesh Devil's Advocate remains a shared Skill, not agent 11.

## Docker privilege on this operator account

This QNAP operator account requires `sudo` for Docker access. Invoke the deployment orchestrator as `sudo sh /share/Docker/mesh-cos-mcp-deploy.sh`. The host-side sudo invocation is only for Docker/Container Station authority. The long-running application container remains UID/GID `65532:65532` and does not run as root.

## Persistence and backup

The application creates online SQLite backups as runtime UID 65532. The host wrapper exports the completed backup using `docker cp`, then deletes the temporary file through `docker exec`. The backup share receives SQLite integrity evidence, non-secret configuration, image IDs, and SHA-256 receipts. `secrets/` is never copied.

Existing canonical TaskLedger state, Secure MCP `tunnel_id`, tunnel runtime-key file, and existing protected Slack HITL files are preserved during normal upgrade.

## Deployment observability

Deploy, prepare, Slack HITL configure, preflight, verify, and backup share one timestamped log and run ID. Failures record stage, safe command classification, return code, component/script identity, and bounded QNAP/Docker/filesystem/container evidence.

The diagnostic contract does not collect secret contents, personal Slack identifier contents, `.env` contents, process environments, credential-bearing argv, or tunnel logs.

## Operator flow

Use the complete SSH-safe **v4.1.10** upgrade block in `DEPLOYMENT-STEPS.md`. The single deployment orchestrator provisions missing protected Slack files after the release image is prepared and before preflight/Compose activation.

After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and `chatgpt-published-app-production-acceptance-v4.1.10.md`. Production certification requires the actual official OpenAI bot-authored synthetic HITL notice, proof ordinary Slack text cannot approve, a live `/mesh-approval` Socket Mode interaction by MK, fresh canonical approval readback, valid audit chain, no unauthorized external action, and required operating-mirror reconciliation.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
