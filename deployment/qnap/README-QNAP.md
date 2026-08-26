# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.13 Slack Approver Bootstrap.**  
**Canonical Phase 1 authority/runtime contract: 4.0.0.**

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` receives `192.168.7.60` on the verified QNAP `lan7` qnet network while the MCP/tunnel trust boundary uses dedicated bridge `172.30.60.0/29`.

The published **Mesh CoS MCP** ChatGPT app reaches `/mcp` only through the tunnel sidecar source address. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

Slack HITL uses an official OpenAI Workspace Agent bot-authored notice and an outbound Slack Socket Mode connection for the `/mesh-approval` human interaction. Neither expands the agent-facing MCP catalog.

## Canonical QNAP paths

- Operator release root: `/share/Docker/cos-mcp/releases`
- Current release directory: `/share/Docker/cos-mcp/releases/v4.1.13`
- Candidate payload: `/share/Docker/cos-mcp/releases/v4.1.13/cos-mcp`
- Candidate runtime environment: `/share/Docker/cos-mcp/releases/v4.1.13/cos-mcp/.env.runtime`
- Canonical application root: `/share/Docker/cos-mcp`
- Canonical state: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Protected secrets: `/share/Docker/cos-mcp/secrets`
- Deployment Docker config: `/share/Docker/cos-mcp/.docker-cli`
- Deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The operator remains in `/share/Docker/cos-mcp/releases` for release staging and execution. The v4.1.13 ZIP creates `v4.1.13/` automatically. Do not manually create the release directory, copy or move release payload files, copy helpers into `/share/Docker`, or chmod scripts before invoking them with `sh`.

## v4.1.13 Slack approver bootstrap

The governed human approver is Michael/MK. The verified Slack **user principal** is `U01KG3CNYHK`.

A Slack identifier beginning with `D`, including the `Channel ID` shown for a direct-message conversation, is a conversation/channel identifier and is not a Slack user principal. v4.1.13 no longer asks the operator for the approver user ID. It automatically stages the governed user principal into the protected runtime approver identity file, validates existing persisted identity before preserving it, and fails closed on `D...` values.

Only Slack user-principal forms beginning with `U` or `W` are accepted. The Slack verifier bot token and Socket Mode app token remain external protected credentials and are never embedded in the release artifact or routine logs.

## Release-root controls retained from v4.1.12

1. The archive contains one top-level `v4.1.13/` directory.
2. Operator scripts self-resolve their own release directory using POSIX `dirname`, `cd`, and `pwd -P` behavior.
3. The deployment orchestrator validates that its resolved parent is `/share/Docker/cos-mcp/releases`.
4. The resolved directory basename must be `v4.1.13` and must agree with staged `release-metadata.txt`.
5. Candidate release identity comes from staged metadata, not active `.env` and not caller environment.
6. Candidate build context, Compose, and `.env.runtime` remain inside the versioned release directory.
7. Active `.env`, Compose, and release metadata are promoted only after both candidate containers are healthy.
8. Canonical TaskLedger, tunnel identity/key, Slack protected files, qnet/static networking, OCI provenance, and backup/restore controls remain outside the release directory and are preserved.

Historical already-published archive layouts remain immutable. v4.1.12 was the first release whose ZIP itself created the versioned directory; v4.1.13 retains that contract.

## Runtime controls

- `mesh-cos-mcp`: UID/GID 65532, 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- long-running containers: non-root, read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, no host networking
- `MESH_COS_AGENT_ID=cos` is process-bound
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.13` is required by the remote process and passed through candidate Compose
- `MESH_COS_SLACK_HITL_REQUIRED=true` is required by production Compose
- protected Slack identity/verifier/Socket Mode files are read-only runtime mounts
- `/readyz` fails when required Slack HITL verification or authenticated Socket Mode is unavailable

Successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.13
agent_id: cos
```

Hosted production readiness additionally requires `slack_hitl_ready=true`.

## Authority boundary

The dual version domains remain distinct:

- `mcp_version` identifies the canonical Phase 1 authority/runtime contract and remains `4.0.0`.
- `deployment_release` identifies the QNAP release serving the request and is `4.1.13` after successful promotion.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification separation, and tunnel source-IP trust boundary remain governed. Message Operations remains agent 10. Mesh Devil's Advocate remains a governed shared Skill, not agent 11.

## QNAP Docker privilege

The current QNAP operator account requires `sudo` for Docker access. From `/share/Docker/cos-mcp/releases`, invoke the versioned script path:

```sh
sudo sh ./v4.1.13/mesh-cos-mcp-deploy.sh
```

Host-side sudo is only for Docker/Container Station authority. The long-running application remains UID/GID `65532:65532`.

## Persistence, backup, rollback, and observability

The application creates online SQLite backups as runtime UID 65532. The backup share receives SQLite integrity evidence, non-secret configuration, image IDs, and SHA-256 receipts. `secrets/` is never copied.

A failed candidate before promotion does not justify deleting or recreating state. Use `rollback-checklist.md` and `backup-restore.md` with the verified pre-deploy backup.

Deploy, prepare, Slack HITL configure, preflight, verify, and backup share one timestamped log and run ID. Diagnostic collection excludes credential contents, protected Slack identity contents, `.env` contents, process environments, credential-bearing argv, and tunnel logs.

## Operator flow

Use `DEPLOYMENT-STEPS.md`. The only release staging working directory is `/share/Docker/cos-mcp/releases`.

After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and `chatgpt-published-app-production-acceptance-v4.1.13.md`. Production certification still requires the actual QNAP serving instance plus hosted ChatGPT and Slack acceptance.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
