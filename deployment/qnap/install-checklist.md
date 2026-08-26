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
- [ ] Slack provider-verifier bot credential is available for hidden configuration
- [ ] Slack Socket Mode app-level `xapp-` credential is available for hidden configuration
- [ ] Slack app exposes `/mesh-approval` through Socket Mode
- [ ] Official ChatGPT Agents app is installed in Slack
- [ ] A specific OpenAI Workspace Agent is configured for official bot-authored HITL delivery

## v4.1.12 release-root staging

- [ ] `mesh-cos-mcp-qnap-v4.1.12.zip` and its `.sha256` file are placed directly in `/share/Docker/cos-mcp/releases`
- [ ] operator changes working directory only to `/share/Docker/cos-mcp/releases`
- [ ] `sha256sum -c mesh-cos-mcp-qnap-v4.1.12.zip.sha256` passes there
- [ ] `unzip -oq mesh-cos-mcp-qnap-v4.1.12.zip` creates `v4.1.12/` automatically
- [ ] no manual `mkdir`, `cp`, `mv`, or `chmod` is required for the release payload
- [ ] no helper script is copied to `/share/Docker`
- [ ] `v4.1.12/cos-mcp/release-metadata.txt` reports `4.1.12` and a valid 40-character commit
- [ ] release-directory basename `v4.1.12` agrees with staged metadata

## Automated by `mesh-cos-mcp-deploy.sh`

Invoke while remaining in `/share/Docker/cos-mcp/releases`:

```sh
sudo sh ./v4.1.12/mesh-cos-mcp-deploy.sh
```

Normal deployment does not require a release environment variable to survive `sudo`.

- [ ] release root is validated before candidate preparation
- [ ] canonical `/share/Docker/cos-mcp` state/secrets tree is preserved
- [ ] backup root `"/share/QNAP NAS/Mike Home/MCP/CoS/Backups"` exists and is writable
- [ ] pre-deploy online backup succeeds when current runtime is running
- [ ] release identity derives from staged metadata, not active `.env`
- [ ] a genuine requested-versus-staged release mismatch fails closed
- [ ] any same-tag `mesh-cos-mcp:qnap-v4.1.12` image is reused only when OCI version/revision matches staged metadata
- [ ] stale/ambiguous same-tag image is rebuilt from staged v4.1.12 build context
- [ ] OpenAI tunnel image resolves to immutable RepoDigest and image ID
- [ ] canonical ledger is staged only if missing and validated before deployment
- [ ] tunnel runtime key remains outside candidate/active environment files, owner `65532:65532`, mode `0400`
- [ ] Slack HITL protected configuration runs against the staged candidate image
- [ ] Slack protected files remain runtime-owned, mode `0400`, and read-only mounted
- [ ] staged `v4.1.12/cos-mcp/.env.runtime` contains no tunnel secret, Slack token, or human Slack identifier value
- [ ] active `.env`, Compose, and release metadata are not promoted before candidate health
- [ ] candidate application receives `MESH_COS_DEPLOYMENT_RELEASE=4.1.12`
- [ ] application receives `MESH_COS_SLACK_HITL_REQUIRED=true`
- [ ] application receives `MESH_COS_SLACK_APPROVAL_COMMAND=/mesh-approval`
- [ ] remote MCP startup/readiness fails closed when deployment identity, notice verification, or active Socket Mode HITL boundary is missing
- [ ] 2 CPU / 24 GiB / no PID limit policy validated
- [ ] staged-candidate preflight passes
- [ ] candidate Compose renders with `pull_policy: never`
- [ ] both candidate containers become healthy
- [ ] active descriptors are promoted only after health
- [ ] `/healthz` and `/readyz` report `mcp_version=4.0.0`, `deployment_release=4.1.12`, `agent_id=cos`, and `transport=SECURE_MCP_TUNNEL`
- [ ] hosted `/readyz` reports `slack_hitl_ready=true`
- [ ] post-deploy verifier executes a real read-only `registry.get_agent` call from the tunnel network namespace
- [ ] public `tools/list` remains exactly 27 canonical CoS tools with closed schemas
- [ ] human-only tools remain absent from agent-facing catalogs
- [ ] scheduled idempotency/lifecycle regression remains green
- [ ] CoS `slack-adapter` exposes `bind_notice` only and cannot record/infer a human decision
- [ ] `COMPLETED != VERIFIED` remains enforced
- [ ] application remains non-root UID/GID 65532, read-only, no-new-privileges, no Docker socket
- [ ] direct non-tunnel MCP request is denied
- [ ] post-deploy backup and SHA-256 verification pass

## v4.1.12 ChatGPT and Slack acceptance

- [ ] local image is `mesh-cos-mcp:qnap-v4.1.12`, running and healthy
- [ ] active `.env` and active release metadata both report `4.1.12`
- [ ] running OCI version is `4.1.12-qnap` and revision equals staged bundle `commit=`
- [ ] installed **Mesh CoS MCP** ChatGPT app connects through the Secure MCP Tunnel
- [ ] Scan Tools returns exactly 27 canonical CoS tools
- [ ] 10-agent roster is ACTIVE and Devil's Advocate remains a shared Skill, not an agent principal
- [ ] every successful governed envelope reports `mcp_version=4.0.0`, `deployment_release=4.1.12`, and `agent_id=cos`
- [ ] audit chain remains valid
- [ ] synthetic scheduled exact-once/lifecycle acceptance passes
- [ ] official OpenAI Workspace Agent creates the synthetic HITL parent as ChatGPT/ChatGPT Agents, not as MK
- [ ] provider-verified notice binding succeeds for exact Approval ID/thread/fingerprint
- [ ] ordinary thread text containing `APPROVE <Approval ID>` leaves canonical approval PENDING
- [ ] MK invokes `/mesh-approval APPROVE <Approval ID>` through Slack
- [ ] Socket Mode non-MCP human ingress records canonical principal `michael`
- [ ] fresh `approval.get` reflects the exact synthetic canonical decision
- [ ] no prospect Gmail, publication, commercial commitment, or other consequential external action occurs during acceptance
- [ ] TaskLedger operating mirror is reconciled when the exact source connector is available; no shadow workbook is substituted
- [ ] production certification closes only with zero open CRITICAL/HIGH defects and no required acceptance blocker
