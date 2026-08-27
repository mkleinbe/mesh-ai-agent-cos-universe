# ChatGPT Secure MCP Tunnel and Native Slack HITL Acceptance

Run this only after the **v4.2.0** QNAP deployment passes local deployment, preflight, verification, and backup. The published **Mesh CoS MCP** app reaches the QNAP runtime through the **OpenAI Secure MCP Tunnel**. The canonical MCP runtime remains **4.0.0** and the deployment release is **4.2.0**.

v4.2.0 replaces QNAP-hosted Slack Socket Mode ingress with one ChatGPT-native Slack new-message dispatcher task. The trigger is non-authoritative. QNAP independently re-reads the exact Slack provider message before TaskLedger authority can change.

## 1. Local deployment identity

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires image `mesh-cos-mcp:qnap-v4.2.0`, healthy application/tunnel containers, and:

```text
mcp_version: 4.0.0
deployment_release: 4.2.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
slack_hitl_ready: true
```

## 2. Slack protected configuration

The governed human principal is Michael/MK. The protected QNAP Slack bindings are the approver user ID and `xoxb-` bot OAuth token. The legacy `xapp-` Socket Mode token is **not required or mounted** in v4.2.0. The installed app and visible bot identity remain **ChatGPT Enterprise AI Agent**.

Do not print or cat protected credential files during acceptance.

## 3. Tool catalog and authority

The CoS-bound app exposes exactly **27 agent-facing tools** and 10 registered agents. Human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent execution. The ChatGPT Slack trigger is not approval authority.

## 4. Governed Slack outbound gate

Create a synthetic PENDING L4 approval owned by canonical principal `michael` with an immutable 64-hex `payload_fingerprint`. Invoke the CoS `slack-adapter` using `operation: post_approval`.

PASS requires:

- `execution_mode: SLACK_BOT_API`;
- a Slack-returned root thread binding;
- a reply-driven approval notice instructing `APPROVE`, `DENY`, or `CHANGE`;
- no approval buttons;
- unchanged PENDING approval state.

## 5. Native dispatcher gate

Configure exactly one Mesh Slack HITL Dispatcher using `docs/chatgpt-native-slack-dispatcher-v4.2.0.md`.

Preferred Slack trigger filter:

- new channel message;
- channel `C0BRL4GCL3A`;
- sender `U01KG3CNYHK`;
- thread reply when supported.

The dispatcher must pass only root-thread timestamp and reply-message timestamp to `skills.invoke_governed` / `slack-adapter` / `reconcile_triggered_message`. It must not pass decision text, asserted sender identity, approval state, actor, principal, or an approval boolean.

## 6. Human interaction gate

From a bound synthetic Slack thread, verify case-insensitive typed `APPROVE`, `DENY`, and `CHANGE`.

PASS requires server-side provider reconciliation of the exact Slack reply and canonical TaskLedger state before mutation. Wrong user, wrong channel, app/bot-authored reply, root message, unbound thread, edited message, deleted/unavailable message, malformed locator, unrecognized decision, stale payload fingerprint, and conflicting second decision all fail closed. Same-message trigger replay is idempotent.

For **CHANGE**, the bot asks what should change; the next independently reconciled human reply becomes untrusted governed change input, supersedes the old approval, returns the task to `IN_PROGRESS`, and requires a new immutable approval before consequential action.

## 7. Provider degradation gate

Slack provider/network failure must not be converted into approval authority. Reconciliation fails closed and the approval remains unresolved. MCP HTTP health must remain independently observable. QNAP does not reconnect a Slack WebSocket because no Slack WebSocket listener exists in v4.2.0.

## 8. Audit and lifecycle

Verify `governance.verify_audit_chain` before and after synthetic writes. Lifecycle must preserve `COMPLETED != VERIFIED`. Synthetic task idempotency and bounded validation errors must remain intact.

## 9. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability overrides, or other real-world consequential actions during acceptance.

## 10. Pass rule

Hosted acceptance passes only when the actual v4.2.0 QNAP serving instance demonstrates release identity, healthy Secure MCP Tunnel/runtime, native HITL mode, dedicated-bot outbound identity, ChatGPT-native event dispatch, server-side provider reconciliation, positive and negative synthetic decisions, CHANGE workflow, replay idempotency, authorization boundaries, TaskLedger persistence, and a valid audit chain.

Full production certification additionally requires `docs/chatgpt-published-app-production-acceptance-v4.2.0.md`, zero open CRITICAL/HIGH defects, and no required acceptance blocker.