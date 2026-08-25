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

## v4.1.3 non-root QNAP correction

A live v4.1.2 deployment proved that the SSH operator can use Container Station/Docker while QTS rejects host `chown` to runtime UID/GID 65532. v4.1.3 therefore treats Docker authority and host filesystem ownership authority as separate contracts.

Preparation builds the release image before state ownership handoff. A one-shot Docker helper then normalizes the explicit state mount using network disabled, read-only rootfs, no Docker socket, all capabilities dropped plus only required ownership/mode capabilities. It exits immediately afterward. Ledger staging itself runs as UID/GID 65532 and receives an explicitly approved source through stdin.

The long-running runtime is not made root and its security controls are unchanged.

## Runtime-identity preflight

Host preflight no longer asks whether the SSH user can read/write the canonical ledger. It validates expected owner/mode and starts a short, network-disabled UID-65532 container to prove that the runtime identity can read/write canonical state.

## Backup boundary

The application creates online SQLite backups as runtime UID 65532. The host wrapper exports the completed backup using `docker cp`, then deletes the temporary file through `docker exec`. The backup share still receives SQLite integrity evidence, non-secret configuration, image IDs, and SHA-256 receipts. `secrets/` is never copied.

## Deployment observability

Deploy, prepare, preflight, verify, and backup share one timestamped log and run ID. Failures record stage, safe command classification, return code, component/script identity, and bounded QNAP/Docker/filesystem/container evidence. The console prints `DIAGNOSTIC_LOG=<path>`.

The diagnostic contract does not collect secret contents, `.env` contents, process environments, credential-bearing argv, or tunnel logs. See `qnap-deployment-observability-standard.md` in the bundle.

## Docker and Compose

The scripts set `DOCKER_CONFIG=/share/Docker/cos-mcp/.docker-cli` so Docker does not depend on the inaccessible Container Station QPKG-home config observed in the live v4.1.2 trace.

Compose V2 discovery remains QNAP-aware: `docker compose` first, then Docker plugin metadata, standard CLI-plugin paths, then the Container Station QPKG path. Compose V1 is rejected.

## Operator flow

Use the complete SSH-safe v4.1.3 block in `DEPLOYMENT-STEPS.md`. After local deployment/verification passes, use `CHATGPT-ACCEPTANCE.md` for Secure MCP Tunnel acceptance.

Controlled HTTPS remains unimplemented and requires separate explicit approval.
