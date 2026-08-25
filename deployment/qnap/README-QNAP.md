# mesh-cos-mcp on QNAP Container Station

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` receives `192.168.7.60` on the verified QNAP `lan7` qnet network while the MCP/tunnel trust boundary uses dedicated bridge `172.30.60.0/29`.

`/mcp` accepts only the tunnel sidecar source address. No host MCP ports, router forwarding, UPnP, public QNAP administration exposure, duplicate TaskLedger, or additional data service are introduced.

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

## v4.1.5 release identity correction

v4.1.5 corrects the QNAP host-preflight drift exposed by the v4.1.4 upgrade attempt. The v4.1.4 bundle generated release `4.1.4`, but preflight still carried an independent hardcoded `4.1.3` comparison and therefore stopped before Compose replacement.

Preflight now requires `release-metadata.txt`, derives the expected release from its `version=` record, and compares that value with generated `MESH_COS_DEPLOYMENT_RELEASE`. Missing metadata, missing version, or a mismatch fails closed before service replacement. No patch-release literal is duplicated in the preflight gate.

The v4.1.4 failed upgrade did not require rollback because the existing v4.1.3 containers remained healthy and Compose replacement never began.

## v4.1.4 transport correction retained

The v4.1.4 modern MCP transport correction is carried forward unchanged. The former v4.1.3 HTTP router relied on a legacy server-managed `Mcp-Session-Id` lifecycle. Current releases use the stable MCP v2 Node/server packages and stateless HTTP handling, support current `server/discover`, and preserve compatibility with older client flows.

`/readyz` verifies that modern MCP discovery is actually serviceable in addition to bound-agent and audit-chain health. The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, and Secure MCP Tunnel authority boundary are unchanged.

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

Use the complete SSH-safe v4.1.5 upgrade block in `DEPLOYMENT-STEPS.md`. After local deployment/verification passes, run `CHATGPT-ACCEPTANCE.md`, including release-identity confirmation and the ten-call sequential MCP regression, before closing the production deployment blocker.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
