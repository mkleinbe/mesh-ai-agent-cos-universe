# QNAP Installation Checklist

## Verified environment

- [x] QNAP probe captured on 2026-08-25
- [x] linux/amd64 confirmed
- [x] 4 CPU cores and approximately 62.7 GiB RAM confirmed
- [x] QTS 5.2.10 build 20260731 confirmed
- [x] Docker 27.1.2-qnap8 and Compose 2.29.1-qnap2 confirmed
- [x] `lan7` verified as QNAP qnet on `eth1`, subnet `192.168.7.0/24`
- [x] `172.30.60.0/29` confirmed non-overlapping with probed Docker/LXC/LXD networks
- [x] Current QNAP operator account requires `sudo` for Docker access

## Human inputs that cannot be invented

- [ ] Secure MCP Tunnel exists and is associated with the target Platform organization and ChatGPT workspace
- [ ] Operator has the necessary tunnel permissions
- [ ] Approved existing canonical TaskLedger source is identified if the target ledger is absent
- [ ] OpenAI `tunnel_id` is available
- [ ] OpenAI tunnel runtime API key is available for hidden entry

## Automated by `mesh-cos-mcp-deploy.sh`

Invoke from the QNAP operator account as `sudo sh /share/Docker/mesh-cos-mcp-deploy.sh` so child Docker and Compose operations have the required host permission.

- [ ] `/share/Docker/cos-mcp` state/secrets tree prepared with approved ownership/permissions
- [ ] Backup root `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` exists and is writable
- [ ] Release-bound Mesh image built locally and content-addressed image ID recorded
- [ ] OpenAI tunnel image resolved to immutable RepoDigest and image ID
- [ ] Canonical ledger staged only if missing and validated before deployment
- [ ] Tunnel runtime key written outside `.env`, owner `65532:65532`, mode `0400`
- [ ] Deterministic `.env` generated with no secret values
- [ ] Bundle `release-metadata.txt` exists and its version matches generated `MESH_COS_DEPLOYMENT_RELEASE`
- [ ] 2 CPU / 24 GiB / no PID limit policy validated
- [ ] Host preflight passes without a stale patch-release literal
- [ ] Compose renders with `pull_policy: never`
- [ ] Containers become healthy
- [ ] `mesh-cos-mcp` remains non-root UID/GID 65532, read-only, no-new-privileges, no Docker socket
- [ ] Direct non-tunnel MCP request is denied
- [ ] Post-deploy state/configuration backup and SHA-256 verification pass

## v4.1.5 ChatGPT acceptance

- [ ] Local image is `mesh-cos-mcp:qnap-v4.1.5`, running and healthy
- [ ] `.env` and bundle metadata both report release `4.1.5`
- [ ] ChatGPT app connects through the associated Secure MCP Tunnel
- [ ] Scan Tools returns exactly 27 canonical CoS tools
- [ ] Human-only tools are absent
- [ ] 10-agent roster is returned and Devil's Advocate is not an agent principal
- [ ] Ten sequential read-only MCP calls complete with no 502, `invalid_session`, reconnect, or container restart
- [ ] Read-only audit/metrics acceptance passes
- [ ] Idempotent L0 `task.intake` acceptance with key `qnap-secure-mcp-v4.1.5` persists and reads back successfully
- [ ] Audit chain remains valid after acceptance write
- [ ] Deployment image IDs and acceptance evidence retained
