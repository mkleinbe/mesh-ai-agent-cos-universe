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
- [ ] Bundle `release-metadata.txt` exists, reports release `4.1.9`, and contains a valid release commit
- [ ] Any same-tag local Mesh image is reused only if OCI version/revision exactly match bundle metadata
- [ ] Stale or ambiguous same-tag Mesh image is rebuilt from the extracted release build context
- [ ] Built/reused Mesh image labels are revalidated before its content-addressed image ID is recorded
- [ ] OpenAI tunnel image resolved to immutable RepoDigest and image ID
- [ ] Canonical ledger staged only if missing and validated before deployment
- [ ] Tunnel runtime key written outside `.env`, owner `65532:65532`, mode `0400`
- [ ] Deterministic `.env` generated with no secret values
- [ ] Application container receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.9`
- [ ] Remote MCP startup fails closed when deployment release identity is missing
- [ ] 2 CPU / 24 GiB / no PID limit policy validated
- [ ] Host preflight passes
- [ ] Compose renders with `pull_policy: never`
- [ ] Containers become healthy
- [ ] `/healthz` and `/readyz` report `mcp_version=4.0.0`, `deployment_release=4.1.9`, `agent_id=cos`, and `transport=SECURE_MCP_TUNNEL`
- [ ] Post-deploy verifier executes a real read-only `registry.get_agent` MCP `tools/call` from the tunnel network namespace
- [ ] Governed tool envelope reports `mcp_version=4.0.0`, `deployment_release=4.1.9`, and `agent_id=cos`
- [ ] Public `tools/list` schemas match the checked-in closed input-schema registry
- [ ] Invalid request shapes return bounded `validation_failed` details
- [ ] Governed Skills use auditable `CHATGPT_SKILL_HANDOFF`; client-supplied executable material is rejected
- [ ] `agentops.recommend` accepts its documented structured contract
- [ ] `COMPLETED != VERIFIED` remains enforced
- [ ] `mesh-cos-mcp` remains non-root UID/GID 65532, read-only, no-new-privileges, no Docker socket
- [ ] Direct non-tunnel MCP request is denied
- [ ] Post-deploy state/configuration backup and SHA-256 verification pass

## v4.1.9 ChatGPT acceptance

- [ ] Local image is `mesh-cos-mcp:qnap-v4.1.9`, running and healthy
- [ ] `.env` and bundle metadata both report release `4.1.9`
- [ ] Running image OCI version is `4.1.9-qnap` and revision equals the bundle `commit=` value
- [ ] Installed **Mesh CoS MCP** ChatGPT app connects through the associated Secure MCP Tunnel
- [ ] Scan Tools returns exactly 27 canonical CoS tools
- [ ] Human-only tools are absent
- [ ] 10-agent roster is returned and Devil's Advocate is not an agent principal
- [ ] Every successful governed tool envelope reports `mcp_version=4.0.0`, `deployment_release=4.1.9`, and `agent_id=cos`
- [ ] v4.1.8 schema, validation, canonical lookup, Skill handoff, AgentOps, lifecycle, and audit acceptance remains green
- [ ] Audit chain remains valid after any synthetic acceptance write
- [ ] Deployment image IDs and acceptance evidence retained
