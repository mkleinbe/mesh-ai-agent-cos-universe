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

## Human/platform inputs that cannot be invented

- [ ] Secure MCP Tunnel exists and is associated with the target Platform organization and ChatGPT workspace
- [ ] Operator has the necessary tunnel permissions
- [ ] Approved existing canonical TaskLedger source is identified if the target ledger is absent
- [ ] OpenAI `tunnel_id` is available
- [ ] OpenAI tunnel runtime API key is available for hidden entry
- [ ] Slack provider identity for MK is known to the operator but is not committed or logged
- [ ] A Slack bot credential with read access to the governed private approval channel is available for hidden provider-verifier configuration
- [ ] A Slack Socket Mode app-level `xapp-` credential is available for hidden human-ingress configuration
- [ ] Slack app exposes `/mesh-approval` through Socket Mode
- [ ] Official ChatGPT Agents app is installed in Slack
- [ ] A specific OpenAI Workspace Agent is deployed/configured to `#mesh-agent-ops` for official bot-authored HITL delivery

## Automated by `mesh-cos-mcp-deploy.sh`

Invoke from the QNAP operator account as `sudo sh /share/Docker/mesh-cos-mcp-deploy.sh` so child Docker and Compose operations have the required host permission.

- [ ] `/share/Docker/cos-mcp` state/secrets tree prepared with approved ownership/permissions
- [ ] Backup root `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` exists and is writable
- [ ] Bundle `release-metadata.txt` reports release `4.1.10` and a valid release commit
- [ ] Any same-tag local `mesh-cos-mcp:qnap-v4.1.10` image is reused only if OCI version/revision exactly match bundle metadata
- [ ] Stale/ambiguous same-tag image is rebuilt from the extracted v4.1.10 build context
- [ ] Built/reused image labels are revalidated before content-addressed image ID is recorded
- [ ] OpenAI tunnel image resolves to immutable RepoDigest and image ID
- [ ] Canonical ledger is staged only if missing and validated before deployment
- [ ] Tunnel runtime key remains outside `.env`, owner `65532:65532`, mode `0400`
- [ ] Slack HITL protected configuration runs after release preparation and before preflight
- [ ] Human Slack identity is stored only in `secrets/slack-approver-user-id`, runtime-owned, mode `0400`
- [ ] Slack verifier bot token is stored only in `secrets/slack-verifier-token`, runtime-owned, mode `0400`
- [ ] Slack Socket Mode app token is stored only in `secrets/slack-socket-app-token`, runtime-owned, mode `0400`
- [ ] Deterministic `.env` is generated with no tunnel secret, Slack verifier/app token, or human Slack identifier value
- [ ] Application receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.10`
- [ ] Application receives `MESH_COS_SLACK_HITL_REQUIRED=true`
- [ ] Application receives `MESH_COS_SLACK_APPROVAL_COMMAND=/mesh-approval`
- [ ] Slack identity/verifier/Socket Mode protected files are mounted read-only
- [ ] Remote MCP startup/readiness fails closed when deployment identity, notice verification, or active Socket Mode HITL boundary is missing
- [ ] 2 CPU / 24 GiB / no PID limit policy validated
- [ ] Host/runtime preflight passes
- [ ] Compose renders with `pull_policy: never`
- [ ] Containers become healthy
- [ ] `/healthz` and `/readyz` report `mcp_version=4.0.0`, `deployment_release=4.1.10`, `agent_id=cos`, and `transport=SECURE_MCP_TUNNEL`
- [ ] Hosted `/readyz` reports `slack_hitl_ready=true`
- [ ] Post-deploy verifier executes a real read-only `registry.get_agent` MCP call from the tunnel network namespace
- [ ] Public `tools/list` remains exactly 27 canonical CoS tools with closed schemas
- [ ] Human-only tools remain absent from agent-facing catalogs
- [ ] Scheduled idempotency/lifecycle regression remains green
- [ ] CoS `slack-adapter` exposes `bind_notice` only and cannot record/infer a human decision
- [ ] `COMPLETED != VERIFIED` remains enforced
- [ ] `mesh-cos-mcp` remains non-root UID/GID 65532, read-only, no-new-privileges, no Docker socket
- [ ] Direct non-tunnel MCP request is denied
- [ ] Post-deploy state/configuration backup and SHA-256 verification pass

## v4.1.10 ChatGPT and Slack acceptance

- [ ] Local image is `mesh-cos-mcp:qnap-v4.1.10`, running and healthy
- [ ] `.env` and bundle metadata both report release `4.1.10`
- [ ] Running OCI version is `4.1.10-qnap` and revision equals bundle `commit=`
- [ ] Installed **Mesh CoS MCP** ChatGPT app connects through the Secure MCP Tunnel
- [ ] Scan Tools returns exactly 27 canonical CoS tools
- [ ] 10-agent roster is ACTIVE and Devil's Advocate remains a shared Skill, not an agent principal
- [ ] Every successful governed envelope reports `mcp_version=4.0.0`, `deployment_release=4.1.10`, and `agent_id=cos`
- [ ] Audit chain remains valid
- [ ] Synthetic scheduled exact-once/lifecycle acceptance passes
- [ ] Official OpenAI Workspace Agent creates the synthetic HITL parent as ChatGPT/ChatGPT Agents, not as MK
- [ ] Provider-verified notice binding succeeds for exact Approval ID/thread/fingerprint
- [ ] An ordinary thread message containing `APPROVE <Approval ID>` leaves the canonical approval PENDING
- [ ] MK invokes `/mesh-approval APPROVE <Approval ID>` through Slack
- [ ] Active Socket Mode boundary receives the slash-command envelope and the non-MCP human-ingress service records canonical principal `michael`
- [ ] Fresh `approval.get` reflects the exact synthetic canonical decision
- [ ] No prospect Gmail, publication, commercial commitment, or other consequential external action occurs during acceptance
- [ ] Google TaskLedger operating mirror is reconciled when the exact source connector is available; no shadow workbook is substituted
- [ ] Production certification closes only with zero open CRITICAL/HIGH defects and no required acceptance blocker
