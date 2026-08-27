# ChatGPT Secure MCP Tunnel and Native Slack HITL Acceptance

Run this only after the **v4.2.1** QNAP deployment passes local deployment, preflight, verification, and backup. The published **Mesh CoS MCP** app reaches the QNAP runtime through the **OpenAI Secure MCP Tunnel**. The canonical MCP runtime remains **4.0.0** and the deployment release is **4.2.1**.

v4.2.1 preserves the v4.2.0 ChatGPT-native Slack new-message dispatcher architecture and patches the provider decision parser to accept Slack's observed one-layer whole-message bold representation such as `*APPROVE*` without broadening the exact command vocabulary.

## 1. Local deployment identity

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires image `mesh-cos-mcp:qnap-v4.2.1`, healthy application/tunnel containers, and:

```text
mcp_version: 4.0.0
deployment_release: 4.2.1
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
slack_hitl_ready: true
```

## 2. Slack protected configuration

The governed human principal is Michael/MK. The protected QNAP Slack bindings remain the approver user ID and `xoxb-` bot OAuth token. The legacy `xapp-` Socket Mode token is not required or mounted. The installed bot identity remains **ChatGPT Enterprise AI Agent**.

v4.2.1 requires no new Slack scope or credential. Do not print or cat protected credential files during acceptance.

## 3. Tool catalog and authority

The CoS-bound app exposes exactly **27 agent-facing tools** and 10 registered agents. Human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent execution. The ChatGPT Slack trigger remains non-authoritative.

## 4. Governed Slack outbound gate

Create a synthetic PENDING L4 approval owned by canonical principal `michael` with an immutable 64-hex `payload_fingerprint`. Invoke the CoS `slack-adapter` using `operation: post_approval`.

PASS requires `execution_mode: SLACK_BOT_API`, a Slack-returned root thread binding, a reply-driven approval notice instructing `APPROVE`, `DENY`, or `CHANGE`, no approval buttons, and unchanged PENDING approval state.

## 5. Native dispatcher gate

Use the existing **Mesh Slack HITL Dispatcher**. Do not create a second task. Keep the trigger and condition unchanged and update only the task prompt release label from `v4.2.0` to `v4.2.1` using `docs/chatgpt-native-slack-dispatcher-v4.2.1.md`.

The dispatcher must continue to pass only root-thread timestamp and reply-message timestamp to `skills.invoke_governed` / `slack-adapter` / `reconcile_triggered_message`. It must not pass decision text, asserted sender identity, approval state, actor, principal, user ID, or an approval boolean.

## 6. Incident replay gate

The first live human interaction must reproduce the v4.2.0 failure shape.

From a bound synthetic Slack thread, send an approval reply using Slack bold formatting and confirm the Slack provider text is `*APPROVE*`.

PASS requires:

- the Work dispatcher records an event-triggered run;
- Mesh CoS MCP reconciliation succeeds instead of returning `INVALID_ARGUMENT / execution_failed`;
- the canonical approval becomes `APPROVED`;
- the task becomes `READY_FOR_ACTION`;
- exactly one decision is recorded;
- replay of the same locators returns the same canonical result idempotently.

## 7. Full human interaction gate

After the incident replay passes, verify bare and bold exact `APPROVE`, `DENY`, and `CHANGE` forms.

Nested or partial formatting such as `**APPROVE**`, `*APPROVE* extra`, formatted non-decision text such as `*looks good*`, wrong user, wrong channel, app/bot-authored reply, root message, unbound thread, edited message, deleted/unavailable message, malformed locator, stale payload fingerprint, and conflicting second decision must all fail closed.

For **CHANGE**, the bot asks what should change; the next independently reconciled human reply becomes untrusted governed change input, supersedes the old approval, returns the task to `IN_PROGRESS`, and requires a new immutable approval before consequential action.

## 8. Provider degradation gate

Slack provider/network failure must not be converted into approval authority. Reconciliation fails closed and the approval remains unresolved. MCP HTTP health remains independently observable. QNAP does not reconnect a Slack WebSocket because no Slack WebSocket listener exists.

## 9. Audit and lifecycle

Verify `governance.verify_audit_chain` before and after synthetic writes. Lifecycle must preserve `COMPLETED != VERIFIED`. Synthetic task idempotency and bounded validation errors must remain intact.

## 10. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability overrides, or other real-world consequential actions during acceptance.

## 11. Pass rule

Hosted acceptance passes only when the actual v4.2.1 QNAP serving instance demonstrates release identity, healthy Secure MCP Tunnel/runtime, native HITL mode, dedicated-bot outbound identity, ChatGPT-native event dispatch, provider-retrieved `*APPROVE*` incident reconciliation, positive and negative synthetic decisions, CHANGE workflow, replay idempotency, authorization boundaries, TaskLedger persistence, and a valid audit chain.

Full production certification additionally requires `docs/chatgpt-published-app-production-acceptance-v4.2.1.md`, zero open CRITICAL/HIGH defects, and no required acceptance blocker.
