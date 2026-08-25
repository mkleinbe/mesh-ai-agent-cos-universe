# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.6 Secure MCP Published App Production Identity.**  
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
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.6` is required by the remote process and is passed explicitly through Compose

## v4.1.6 production identity and published-app acceptance

The published Mesh CoS MCP app has passed the ten-call sequential read-only hosted acceptance path through the OpenAI Secure MCP Tunnel without HTTP 502, `invalid_session`, reconnect, or container restart. That acceptance confirmed transport stability, the canonical 10-agent roster, audit-chain access, metrics access, CoS identity, Message Operations identity, and TaskLedger reads.

The live baseline also exposed one observability gap: hosted responses identified only the canonical MCP contract as `mcp_version=4.0.0`, so ChatGPT could not prove which QNAP deployment release served a request.

v4.1.6 closes that gap without changing authority. Successful governed tool envelopes now include:

```text
mcp_version: 4.0.0
deployment_release: 4.1.6
agent_id: cos
```

`/healthz` and `/readyz` report the same dual release identity plus `transport: SECURE_MCP_TUNNEL`. Remote startup fails closed when deployment release identity is missing or blank. Readiness still requires an ACTIVE bound agent, valid governance audit chain, and modern MCP discovery.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification semantics, and tunnel source-IP trust boundary are unchanged.

## v4.1.5 release-identity correction retained

v4.1.5 corrected the QNAP host-preflight drift exposed by the v4.1.4 upgrade attempt. The v4.1.4 bundle generated release `4.1.4`, but preflight still carried an independent hardcoded `4.1.3` comparison and therefore stopped before Compose replacement.

Preflight requires `release-metadata.txt`, derives the expected release from its `version=` record, and compares that value with generated `MESH_COS_DEPLOYMENT_RELEASE`. Missing metadata, missing version, or a mismatch fails closed before service replacement. No patch-release literal is duplicated in the preflight gate.

## v4.1.4 transport correction retained

The v4.1.4 modern MCP transport correction is carried forward unchanged. The former v4.1.3 HTTP router relied on a legacy server-managed `Mcp-Session-Id` lifecycle. Current releases use the stable MCP v2 Node/server packages and stateless HTTP handling, support current `server/discover`, and preserve compatibility with older client flows.

## v4.1.3 QNAP filesystem correction retained

The non-root QNAP fixes from v4.1.3 remain in place: state ownership is normalized through a constrained one-shot Docker helper, canonical ledger staging runs as UID/GID 65532, host preflight verifies runtime-identity access, Docker-mediated backup avoids host ownership assumptions, and deployment uses a local `DOCKER_CONFIG`.

## Docker privilege on this operator account

This QNAP operator account requires `sudo` for Docker access. Invoke the deployment orchestrator as `sudo sh /share/Docker/mesh-cos-mcp-deploy.sh`. The host-side sudo invocation is only for Docker/Container Station authority. The long-running application container remains UID/GID `65532:65532` and does not run as root.

## Backup boundary

The application creates online SQLite backups as runtime UID 65532. The host wrapper exports the completed backup using `docker cp`, then deletes the temporary file through `docker exec`. The backup share receives SQLite integrity evidence, non-secret configuration, image IDs, and SHA-256 receipts. `secrets/` is never copied.

## Deployment observability

Deploy, prepare, preflight, verify, and backup share one timestamped log and run ID. Failures record stage, safe command classification, return code, component/script identity, and bounded QNAP/Docker/filesystem/container evidence. The console prints `DIAGNOSTIC_LOG=<path>`.

The diagnostic contract does not collect secret contents, `.env` contents, process environments, credential-bearing argv, or tunnel logs.

## Docker and Compose

The scripts set `DOCKER_CONFIG=/share/Docker/cos-mcp/.docker-cli` so Docker does not depend on the inaccessible Container Station QPKG-home config observed in the earlier live trace.

Compose V2 discovery remains QNAP-aware: `docker compose` first, then Docker plugin metadata, standard CLI-plugin paths, then the Container Station QPKG path. Compose V1 is rejected.

## Operator flow

Use the complete SSH-safe **v4.1.6** upgrade block in `DEPLOYMENT-STEPS.md`. After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and require dual release identity plus the ten-call sequential hosted regression before accepting the new deployment.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
