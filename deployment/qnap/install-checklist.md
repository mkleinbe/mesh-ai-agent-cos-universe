# QNAP Installation Checklist

## Verified environment

- [x] QNAP probe captured on 2026-08-25
- [x] linux/amd64 confirmed
- [x] 4 CPU cores and approximately 62.7 GiB RAM confirmed
- [x] QTS 5.2.10 build 20260731 confirmed
- [x] Docker 27.1.2-qnap8 and Compose 2.29.1-qnap2 confirmed
- [x] `lan7` verified as QNAP qnet on `eth1`, subnet `192.168.7.0/24`
- [x] `172.30.60.0/29` and `172.30.61.0/29` are reserved for Mesh private/egress bridges
- [x] QNAP operator requires `sudo` for Docker access

## Human/platform inputs

- [ ] Secure MCP Tunnel exists and is associated with the target OpenAI Platform organization and ChatGPT workspace
- [ ] Operator has required tunnel permissions
- [ ] Approved existing canonical TaskLedger source is identified if the target ledger is absent
- [ ] OpenAI `tunnel_id` is available
- [ ] OpenAI tunnel runtime API key is available for protected entry if not already preserved
- [x] Verified Slack human user principal for Michael/MK is `U01KG3CNYHK`
- [ ] Slack Socket Mode app-level `xapp-` credential is available if not already preserved
- [ ] Slack app exposes `/mesh-approval` through Socket Mode
- [ ] Connected Slack integration is available for collaboration and approval-request delivery

No Slack `xoxb-` verifier credential is required by v4.1.15.

## v4.1.15 release-root staging

- [ ] `mesh-cos-mcp-qnap-v4.1.15.zip` and `.sha256` are placed directly in `/share/Docker/cos-mcp/releases`
- [ ] operator working directory is `/share/Docker/cos-mcp/releases`
- [ ] `sha256sum -c mesh-cos-mcp-qnap-v4.1.15.zip.sha256` passes
- [ ] extraction creates `v4.1.15/` automatically
- [ ] no manual release-directory creation, helper copy, payload move, or chmod is required
- [ ] `v4.1.15/cos-mcp/release-metadata.txt` reports `version=4.1.15` and a valid 40-character commit
- [ ] release-directory basename agrees with staged metadata

## Automated deployment

Invoke from `/share/Docker/cos-mcp/releases`:

```sh
sudo sh ./v4.1.15/mesh-cos-mcp-deploy.sh
```

- [ ] release root is validated before candidate preparation
- [ ] canonical `/share/Docker/cos-mcp` state/secrets tree is preserved
- [ ] pre-deploy backup succeeds when current runtime is running
- [ ] release identity derives from staged metadata
- [ ] same-tag image reuse requires matching OCI version/revision; mismatch rebuilds
- [ ] tunnel image resolves to immutable RepoDigest
- [ ] canonical ledger is staged only if missing and validated before deployment
- [ ] tunnel runtime key remains outside candidate/active env values and mode `0400`
- [ ] missing approver identity is bootstrapped non-interactively from `U01KG3CNYHK`
- [ ] `D...` conversation IDs are rejected as human principals
- [ ] existing `U...`/`W...` approver identity is validated/preserved
- [ ] only Socket Mode token is required as a Slack credential
- [ ] Slack verifier token is not mounted, validated, prompted for, or used
- [ ] protected Slack files are runtime-owned, mode `0400`, and read-only mounted
- [ ] candidate `.env.runtime` contains no tunnel or Slack credential value
- [ ] `mesh-cos-private` is internal-only `172.30.60.0/29`
- [ ] MCP is `172.30.60.2` private plus qnet `192.168.7.60`
- [ ] tunnel is `172.30.60.3` private plus egress `172.30.61.2`
- [ ] no second qnet tunnel address and no direct MCP host port exist
- [ ] staged-candidate preflight passes
- [ ] both candidate containers become healthy
- [ ] active `.env`, Compose, and metadata are snapshotted before promotion
- [ ] partial promotion/post-promotion verification failure restores the exact pre-promotion configuration and previous stack
- [ ] incomplete rollback preserves its `.release-rollback.*` snapshot
- [ ] post-deploy verification passes before promotion is committed
- [ ] post-deploy backup and SHA-256 verification pass

## Runtime and authority acceptance

- [ ] active release/image are `4.1.15` / `mesh-cos-mcp:qnap-v4.1.15`
- [ ] `/healthz` and `/readyz` report `mcp_version=4.0.0`, `deployment_release=4.1.15`, `agent_id=cos`, `transport=SECURE_MCP_TUNNEL`
- [ ] hosted `/readyz` reports `slack_hitl_ready=true`
- [ ] public CoS tool surface remains exactly 27 governed tools
- [ ] exactly 10 agents remain registered; Devil's Advocate remains a shared Skill
- [ ] human-only tools remain absent from agent-facing catalogs
- [ ] CoS `slack-adapter` returns `CHATGPT_CONNECTOR_HANDOFF` with `COLLABORATION_ONLY` authority for `operation: handoff`
- [ ] Slack collaboration cannot mutate canonical approval state
- [ ] ordinary Slack `APPROVE` text leaves canonical approval PENDING
- [ ] verified MK `/mesh-approval` succeeds for the synthetic approval; another user/channel fails closed
- [ ] replay is idempotent and conflicting second interaction fails closed
- [ ] fresh `approval.get` reflects the exact canonical decision
- [ ] `COMPLETED != VERIFIED` remains enforced
- [ ] application remains UID/GID 65532, read-only, no-new-privileges, no Docker socket
- [ ] direct non-tunnel MCP request is denied
- [ ] no consequential external action occurs during acceptance
- [ ] production certification closes only with zero open CRITICAL/HIGH defects and no required live acceptance blocker
