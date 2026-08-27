# QNAP Installation Checklist

## Verified environment

- [x] QNAP linux/amd64 environment confirmed
- [x] QNAP Container Station Docker/Compose runtime confirmed
- [x] `lan7` qnet on `192.168.7.0/24` confirmed
- [x] `172.30.60.0/29` and `172.30.61.0/29` reserved for Mesh private/egress bridges
- [x] QNAP operator requires `sudo` for Docker access

## Human/platform inputs

- [ ] Secure MCP Tunnel exists and is associated with the target OpenAI Platform organization and ChatGPT workspace
- [ ] Approved existing canonical TaskLedger source is identified if the target ledger is absent
- [ ] OpenAI `tunnel_id` is available
- [ ] OpenAI tunnel runtime API key is available for protected entry if not already preserved
- [x] Verified Slack human user principal for Michael/MK is `U01KG3CNYHK`
- [x] Provider-verified Slack App ID is `A0B49RNE4K0`
- [ ] Dedicated Slack bot is a member of `#mesh-agent-ops`
- [ ] Bot Token Scopes include `chat:write` and `groups:history`
- [ ] If bot scopes changed, Slack app was reinstalled/reauthorized and the resulting `xoxb-` token was reprovisioned to QNAP
- [ ] Single ChatGPT Work **Mesh Slack HITL Dispatcher** exists and is enabled

No Slack `xapp-` Socket Mode credential is required or permitted by the production v4.2.2 HITL path.

## v4.2.2 release-root staging

- [ ] `mesh-cos-mcp-qnap-v4.2.2.zip` and `.sha256` are placed directly in `/share/Docker/cos-mcp/releases`
- [ ] operator working directory is `/share/Docker/cos-mcp/releases`
- [ ] `sha256sum -c mesh-cos-mcp-qnap-v4.2.2.zip.sha256` passes
- [ ] extraction creates `v4.2.2/` automatically
- [ ] no manual release-directory creation, helper copy, payload move, or chmod is required
- [ ] `v4.2.2/cos-mcp/release-metadata.txt` reports `version=4.2.2` and a valid 40-character commit
- [ ] release-directory basename agrees with staged metadata

## Automated deployment

```sh
sudo sh ./v4.2.2/mesh-cos-mcp-deploy.sh
```

- [ ] canonical `/share/Docker/cos-mcp` state/secrets tree is preserved
- [ ] any existing runtime receives the required pre-deploy backup attempt
- [ ] canonical TaskLedger is preserved and passes integrity checks
- [ ] tunnel runtime key remains protected and outside environment values
- [ ] protected Slack approver identity and `xoxb-` bot token remain separate, runtime-owned, mode `0400`, and read-only mounted
- [ ] no `xapp-` credential is configured or mounted
- [ ] staged `.env.runtime` uses Slack App ID `A0B49RNE4K0`
- [ ] staged `.env.runtime` contains no Slack/tunnel credential values
- [ ] `mesh-cos-private` remains internal-only `172.30.60.0/29`
- [ ] MCP remains `172.30.60.2` private plus qnet `192.168.7.60`
- [ ] tunnel remains `172.30.60.3` private plus egress `172.30.61.2`
- [ ] no direct MCP host port exists
- [ ] candidate application and tunnel become healthy
- [ ] transactional promotion/rollback controls pass
- [ ] post-deploy verification passes before promotion commit
- [ ] post-deploy backup and SHA-256 verification pass

## Live Slack provider-read gate

- [ ] QNAP verification runs the provider-read probe inside the running `mesh-cos-mcp` container
- [ ] probe uses the mounted `xoxb-` credential without printing it
- [ ] probe calls `conversations.history` for `C0BRL4GCL3A` with limit 1
- [ ] verification reports `Slack bot provider read scope and governed-channel access`
- [ ] `missing_scope`, invalid auth, missing channel membership/access, or provider/network failure blocks deployment verification
- [ ] provider diagnostics expose only a sanitized error code, never token/header/full response metadata

## Runtime and authority acceptance

- [ ] active release/image are `4.2.2` / `mesh-cos-mcp:qnap-v4.2.2`
- [ ] `/healthz` and `/readyz` report `mcp_version=4.0.0`, `deployment_release=4.2.2`, `agent_id=cos`, `transport=SECURE_MCP_TUNNEL`
- [ ] hosted `/readyz` reports `slack_hitl_ready=true`
- [ ] exactly 10 agents remain registered
- [ ] human-only tools remain unavailable to agents
- [ ] ChatGPT Work dispatcher remains one event-triggered task, not a schedule/polling loop
- [ ] dispatcher prompt remains `Mesh CoS MCP v4.x`
- [ ] dispatcher passes only `thread_ts` and `message_ts`
- [ ] governed Slack approval notice is posted by the dedicated bot and bound to canonical approval state
- [ ] QNAP provider reread uses GET/query `conversations.replies`
- [ ] provider-retrieved `*APPROVE*` creates exactly one canonical APPROVED decision for a fresh synthetic approval
- [ ] same locator replay is idempotent
- [ ] DENY and CHANGE synthetic cases behave as documented
- [ ] wrong user, bot/app author, root/unbound thread, edited/unavailable message, malformed formatting, fingerprint drift, and provider failure all fail closed
- [ ] `COMPLETED != VERIFIED` remains enforced
- [ ] application remains UID/GID 65532, read-only, no-new-privileges, no Docker socket
- [ ] direct non-tunnel MCP request is denied
- [ ] final governance audit chain verifies
- [ ] no consequential external action occurs during acceptance
- [ ] production certification closes only with zero open CRITICAL/HIGH defects and no required live acceptance blocker
