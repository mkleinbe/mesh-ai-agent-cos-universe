# mesh-cos-mcp on QNAP Container Station

**Current deployment release: v4.1.7 QNAP Image Provenance and Hosted Envelope Verification.**  
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
- `MESH_COS_DEPLOYMENT_RELEASE=4.1.7` is required by the remote process and passed explicitly through Compose

## v4.1.7 image provenance and hosted envelope correction

The final v4.1.6 repository and release ZIP already contained the required `deployment_release` field in successful governed response envelopes. Production testing nevertheless observed hosted responses with `mcp_version: 4.0.0` and `agent_id: cos` but no `deployment_release`.

The QNAP preparation path allowed any existing local image under the requested mutable release tag to be reused without proving that its OCI release labels matched the final extracted bundle. The post-deploy verifier also checked `/healthz` and `/readyz`, but did not execute the governed `tools/call` path that failed hosted acceptance.

v4.1.7 closes both gaps:

1. Existing local Mesh images are reusable only when OCI `org.opencontainers.image.version` and `org.opencontainers.image.revision` exactly match the extracted `release-metadata.txt`. A mismatch forces a rebuild from the extracted release build context.
2. After build or reuse, the image labels are verified again before the image ID is recorded.
3. Post-deploy verification issues an actual read-only `registry.get_agent` MCP `tools/call` from an ephemeral verifier sharing the tunnel client's network namespace.
4. Deployment does not return PASS unless the actual governed response envelope contains:

```text
mcp_version: 4.0.0
deployment_release: 4.1.7
agent_id: cos
```

The verification container has no state volume, no tunnel secret, no Docker socket, no added capabilities, and no persistent service lifetime. The production source-IP gate remains unchanged.

## v4.1.6 production identity semantics retained

The dual version domains remain distinct:

- `mcp_version` identifies the canonical Phase 1 authority/runtime contract and remains `4.0.0`.
- `deployment_release` identifies the QNAP deployment release serving the request and is `4.1.7` for this release.

`/healthz` and `/readyz` report the same identity plus `transport: SECURE_MCP_TUNNEL`. Remote startup fails closed when deployment release identity is missing or blank. Readiness still requires an ACTIVE bound agent, valid governance audit chain, and modern MCP discovery.

The 10-agent roster, 27-tool CoS catalog, human-only operations, canonical TaskLedger, completion/verification semantics, and tunnel source-IP trust boundary are unchanged.

## Earlier corrections retained

- v4.1.5 removed duplicated patch-release authority from host preflight and binds `.env` deployment identity to extracted release metadata.
- v4.1.4 introduced stateless modern MCP transport and current `server/discover` support.
- v4.1.3 added non-root QNAP filesystem handling, Docker-mediated backup, deployment-local Docker configuration, and structured observability.

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

Use the complete SSH-safe **v4.1.7** upgrade block in `DEPLOYMENT-STEPS.md`. After local deployment and verification pass, run `CHATGPT-ACCEPTANCE.md` and require `deployment_release: 4.1.7` on every successful hosted governed response before accepting the deployment.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
