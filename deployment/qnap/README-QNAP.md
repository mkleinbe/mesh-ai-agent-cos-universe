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
- Release-bound image build context: `/share/Docker/cos-mcp/build-context`
- Canonical state root: `/share/Docker/cos-mcp/state`
- Canonical ledger: `/share/Docker/cos-mcp/state/ledger/taskledger.sqlite3`
- Tunnel secret: `/share/Docker/cos-mcp/secrets/openai-tunnel-runtime-key`
- Backup root: `/share/QNAP NAS/Mike Home/MCP/CoS/Backups`

The backup path contains spaces. Scripts always quote it as one shell argument.

## Resource controls

- `mesh-cos-mcp`: 2 CPUs, 24 GiB RAM, no PID limit
- `mesh-cos-tunnel`: 0.25 CPU, 256 MiB RAM, no PID limit
- Both containers: non-root, read-only root filesystem, all capabilities dropped, no-new-privileges, no Docker socket, no host networking

The QNAP probe verified 4 CPU cores, approximately 62.7 GiB RAM, QTS 5.2.10 build 20260731, Docker 27.1.2-qnap8, Compose 2.29.1-qnap2, `lan7` qnet on `eth1`, and no overlap between existing private Docker bridges and `172.30.60.0/29`.

## One-command deployment

After extracting the release ZIP directly into `/share/Docker`, run:

```sh
cd /share/Docker && sh mesh-cos-mcp-deploy.sh
```

On first deployment the script asks only for the approved existing TaskLedger source path, OpenAI `tunnel_id`, and hidden tunnel runtime API key. It automates image construction and pinning, ledger staging, secret-file creation, `.env` generation, preflight, deployment, health waits, verification, and backup. Existing canonical state and secret material are preserved on subsequent runs.

The release-bound Mesh image is built locally from the bundle. Its versioned local tag is coupled to a recorded Docker content-addressed image ID. The OpenAI tunnel client is coupled to an immutable GHCR RepoDigest and recorded image ID. Compose uses `pull_policy: never`, so deployment cannot silently replace either prepared image.

## Canonical-state boundary

Production refuses to create a missing or in-memory TaskLedger. If the canonical target file is absent, the prepare step requires the operator to explicitly select an existing approved TaskLedger source. Once the canonical target exists, prepare preserves it and never overwrites it from another source.

## Secret boundary

The OpenAI tunnel runtime key is entered with terminal echo disabled and written only to the approved secret file, owner `65532:65532`, mode `0400`. The key is never written to `.env`, release metadata, deployment-state receipts, or backups.

## Backup boundary

`mesh-cos-mcp-backup.sh` creates an online SQLite backup and a dated deployment receipt directory under the quoted backup root. It captures the closed TaskLedger backup, `compose.yaml`, non-secret generated `.env`, release metadata, running image IDs, and SHA-256 verification. It never copies `secrets/`.

The backup target is on the same NAS, so it protects application/configuration recovery but not total NAS loss. QNAP snapshots and an independent second copy remain recommended defense in depth.

## Operational commands

```sh
cd /share/Docker
sh mesh-cos-mcp-deploy.sh
sh mesh-cos-mcp-preflight.sh
sh mesh-cos-mcp-verify.sh
sh mesh-cos-mcp-backup.sh manual
```

Use `DEPLOYMENT-STEPS.md` for the short operator flow and `CHATGPT-ACCEPTANCE.md` for the final ChatGPT tunnel/app acceptance procedure.

## Controlled HTTPS fallback

Controlled HTTPS remains unimplemented and requires separate explicit approval. Do not expose raw port 8080, QTS administration, or an ad hoc bearer-token endpoint to the internet.
