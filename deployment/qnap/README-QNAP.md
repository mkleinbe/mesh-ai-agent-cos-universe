# mesh-cos-mcp on QNAP Container Station

## Production topology

Production uses **OpenAI Secure MCP Tunnel**. `mesh-cos-mcp` receives `192.168.7.60` on the verified QNAP `lan7` **qnet** network while the MCP/tunnel trust boundary uses dedicated bridge `172.30.60.0/29`.

```text
ChatGPT
  |
OpenAI Secure MCP Tunnel
  |
mesh-cos-tunnel 172.30.60.3
  |
mesh-cos-mcp 172.30.60.2 + 192.168.7.60
  |
canonical MCPRuntime
  |
TaskLedger SQLite
```

`/mcp` accepts only the tunnel sidecar source address. No host ports, router forwarding, UPnP, public QNAP administration exposure, additional proxy container, Redis, PostgreSQL, queue, message bus, or duplicate TaskLedger are introduced.

## Fixed QNAP paths

- Script root: `/share/Docker`
- Application root: `/share/Docker/cos-mcp`
- Canonical state root: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Tunnel secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The backup path contains spaces. Always quote it as one shell argument.

## Resource controls

- `mesh-cos-mcp`: 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- Both containers: non-root, read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, no host networking

The QNAP probe verified 4 CPU cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, and no overlap between existing private Docker bridges and `172.30.60.0/29`.

## Deployment

Use [`DEPLOYMENT-STEPS.md`](DEPLOYMENT-STEPS.md) for the short path. The scripts in `scripts/` assume they are invoked from `/share/Docker` and reference `/share/Docker/cos-mcp` explicitly.

Production refuses to create a missing TaskLedger. Stage the approved canonical database before deployment. Resolve both images to immutable digests and create the OpenAI tunnel/runtime credential before running the deployment script.

## Operational commands

```sh
cd /share/Docker
sh mesh-cos-mcp-preflight.sh
sh mesh-cos-mcp-deploy.sh
sh mesh-cos-mcp-verify.sh
sh mesh-cos-mcp-backup.sh
```

The release bundle places these wrapper scripts directly under `/share/Docker` and the Container Station application files under `/share/Docker/cos-mcp`.

## Controlled HTTPS fallback

Controlled HTTPS remains unimplemented and requires separate explicit approval. Do not expose raw port 8080, QTS administration, or an ad hoc bearer-token endpoint to the internet.
