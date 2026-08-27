# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this only after the **v4.1.17** QNAP deployment passes local deployment, preflight, verification, and backup. The published **Mesh CoS MCP** app reaches the QNAP runtime through the **OpenAI Secure MCP Tunnel**. The canonical MCP runtime remains **4.0.0** and the deployment release is **4.1.17**.

v4.1.17 replaces `/mesh-approval` and the connected-ChatGPT Slack posting path with the dedicated **ChatGPT Enterprise AI Agent** bot, Block Kit buttons, and provider-authenticated Socket Mode thread interactions.

## 1. Local deployment identity

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires image `mesh-cos-mcp:qnap-v4.1.17`, healthy application/tunnel containers, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.17
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_ready: true
```

## 2. Slack protected configuration

The governed human principal is Michael/MK. The protected Slack bindings are the approver user ID, `xapp-` Socket Mode app token, and `xoxb-` bot OAuth token. The retired verifier token and slash command must not be used. The installed app and visible bot identity must be **ChatGPT Enterprise AI Agent**.

## 3. Tool catalog and authority

The CoS-bound app exposes exactly **27 agent-facing tools** and 10 registered agents. Human-only `approval.record_decision` and `reliability.human_override` remain excluded. The connected ChatGPT Slack integration is not approval authority.

## 4. Governed Slack outbound gate

Create a synthetic PENDING L4 approval owned by canonical principal `michael` with an immutable 64-hex `payload_fingerprint`. Invoke the CoS `slack-adapter` using `operation: post_approval`. PASS requires `execution_mode: SLACK_BOT_API`, a Slack-returned root thread binding, and unchanged PENDING approval state.

## 5. Human interaction gate

From the bound Slack thread, verify **Approve**, **Deny**, and **Change** buttons. Also verify case-insensitive typed `approve`, `deny`/`reject`, and `change` fallbacks. The human never types an approval ID.

PASS requires wrong user, wrong channel, wrong app, app/bot-authored replies, unbound thread, stale button value, malformed interaction, and conflicting second decision to fail closed. Same provider-event replay is idempotent.

For **Change**, the bot asks `What would you like to change?`; the next authenticated human reply becomes governed change input, supersedes the old approval, returns the task to `IN_PROGRESS`, and requires a new immutable approval before consequential action.

## 6. Provider degradation gate

Slack provider/network outage must not terminate the MCP HTTP process. `/healthz` remains available, `/readyz` fails closed when Slack HITL is required, consequential approval remains blocked, and reconnect remains bounded.

## 7. Audit and lifecycle

Verify `governance.verify_audit_chain` before and after synthetic writes. Lifecycle must preserve `COMPLETED != VERIFIED`. Synthetic task idempotency and bounded validation errors must remain intact.

## 8. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability overrides, or other real-world consequential actions during acceptance.

## 9. Pass rule

Hosted acceptance passes only when the actual v4.1.17 QNAP serving instance demonstrates release identity, healthy tunnel/runtime, `slack_hitl_ready=true`, dedicated-bot outbound identity, authenticated thread/button decisions, change workflow, authorization boundaries, TaskLedger persistence, and valid audit chain. Full production certification additionally requires `chatgpt-published-app-production-acceptance-v4.1.17.md`, zero open CRITICAL/HIGH defects, and no required acceptance blocker.
