# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.9 Documentation and Release Closeout.**  
**Canonical Phase 1 authority/runtime contract: 4.0.0.**

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` receives `192.168.7.60` on the verified QNAP `lan7` qnet network while the MCP/tunnel trust boundary uses dedicated bridge `172.30.60.0/29`.

The published **Mesh CoS MCP** ChatGPT app reaches `/mcp` only through the tunnel sidecar source address. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

## Fixed QNAP paths

- Script root: `/share/Docker`
- Application root: `/share/Docker/cos-mcp`
- Build context: `/share/Docker/cos-mcp/build-context`
- Canonical state: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Tunnel secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`
- Deployment Docker config: `/share/Docker/cos-mcp/.docker-cli`
- Deployment logs: `/share/Docker/cos-mcp/logs/deployment`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

## Runtime controls

- `mesh-cos-mcp`: UID/GID 65532, 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- Long-running containers: non-root, read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, no host networking
- `MESH_COS_AGENT_ID=cos` is process-bound
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.9` is required by the remote process and passed explicitly through Compose

## Current release train controls

v4.1.9 carries forward the v4.1.8 MCP contract corrections and closes active-documentation drift. The QNAP runtime continues to enforce:

1. exact closed `tools/list` input schemas matching runtime validation;
2. bounded `validation_failed` field details for malformed requests;
3. canonical task lookup that distinguishes request validation from true `not_found` resources;
4. auditable `CHATGPT_SKILL_HANDOFF` for declared governed Skills with arbitrary executable payloads rejected;
5. documented AgentOps request binding;
6. OCI image version/revision provenance matched to extracted `release-metadata.txt` before same-tag reuse;
7. governed read-only post-deploy MCP verification from the tunnel network namespace;
8. deterministic backup, restart, least-privilege, and direct-ingress-denial checks.

Successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.9
agent_id: cos
```

`/healthz` and `/readyz` report the same identity plus `transport: SECURE_MCP_TUNNEL`.

## Authority boundary

The dual version domains remain distinct:

- `mcp_version` identifies the canonical Phase 1 authority/runtime contract and remains `4.0.0`.
- `deployment_release` identifies the QNAP deployment release serving the request and is `4.1.9` for this release.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification semantics, and tunnel source-IP trust boundary are unchanged. Mesh Devil's Advocate remains a governed shared Skill, not agent 11.

## Docker privilege on this operator account

This QNAP operator account requires `sudo` for Docker access. Invoke the deployment orchestrator as `sudo sh /share/Docker/mesh-cos-mcp-deploy.sh`. The host-side sudo invocation is only for Docker/Container Station authority. The long-running application container remains UID/GID `65532:65532` and does not run as root.

## Persistence and backup

The application creates online SQLite backups as runtime UID 65532. The host wrapper exports the completed backup using `docker cp`, then deletes the temporary file through `docker exec`. The backup share receives SQLite integrity evidence, non-secret configuration, image IDs, and SHA-256 receipts. `secrets/` is never copied.

Existing canonical TaskLedger state, Secure MCP `tunnel_id`, and tunnel runtime-key file are preserved during normal upgrade.

## Deployment observability

Deploy, prepare, preflight, verify, and backup share one timestamped log and run ID. Failures record stage, safe command classification, return code, component/script identity, and bounded QNAP/Docker/filesystem/container evidence. The console prints `DIAGNOSTIC_LOG=<path>`.

The diagnostic contract does not collect secret contents, `.env` contents, process environments, credential-bearing argv, or tunnel logs.

## Docker and Compose

The scripts set `DOCKER_CONFIG=/share/Docker/cos-mcp/.docker-cli` so Docker does not depend on the inaccessible Container Station QPKG-home config observed in earlier live traces.

Compose V2 discovery remains QNAP-aware: `docker compose` first, then Docker plugin metadata, standard CLI-plugin paths, then the Container Station QPKG path. Compose V1 is rejected.

## Operator flow

Use the complete SSH-safe **v4.1.9** upgrade block in `DEPLOYMENT-STEPS.md`. After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and require `deployment_release: 4.1.9` on every successful hosted governed response before accepting the deployment.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
