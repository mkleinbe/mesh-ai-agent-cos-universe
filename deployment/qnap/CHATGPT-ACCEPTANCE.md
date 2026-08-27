# ChatGPT Secure MCP Tunnel and Native Slack HITL Acceptance

Run this only after the **v4.2.3** QNAP deployment passes local deployment, preflight, verification, backup, and the live Slack provider-read/qnet egress-readiness gate. The published **Mesh CoS MCP** app reaches the QNAP runtime through the **OpenAI Secure MCP Tunnel**. The canonical MCP runtime remains **4.0.0** and the deployment release is **4.2.3**.

v4.2.3 preserves the ChatGPT-native Slack new-message dispatcher architecture, v4.2.1 rendered-decision compatibility, and the v4.2.2 GET/query provider transport repair while adding bounded external-egress readiness handling for freshly recreated QNAP/qnet container namespaces.

## 1. Local deployment identity

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires image `mesh-cos-mcp:qnap-v4.2.3`, healthy application/tunnel containers, and:

```text
mcp_version: 4.0.0
deployment_release: 4.2.3
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
slack_hitl_ready: true
```

## 2. Slack protected configuration, qnet readiness, and provider-read gate

The governed human principal is Michael/MK. The protected QNAP Slack bindings remain the approver user ID and `xoxb-` bot OAuth token. The legacy `xapp-` Socket Mode token is not required or mounted. The installed bot identity remains **ChatGPT Enterprise AI Agent** and the provider-verified Slack App ID is `A0B49RNE4K0`.

The bot must have Bot Token Scopes `chat:write` and `groups:history` and be a member of `#mesh-agent-ops`. Do not print or cat protected credential files during acceptance.

`mesh-cos-mcp-verify.sh` must already have passed its live GET/query `conversations.history` provider-read probe from the running container. v4.2.3 permits up to six attempts with five-second inter-attempt delay only when the provider fetch raises a network exception before Slack returns any response. A Slack `ok:false` response, malformed response, or internal verifier error fails immediately. Exhausted network readiness fails deployment and triggers transactional rollback.

That gate proves the actual mounted credential and the freshly recreated qnet namespace can reach and read the governed private channel before human acceptance begins.

## 3. Tool catalog and authority

The CoS-bound app exposes the governed Phase 1 tool catalog and exactly 10 registered agents. Human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent execution. The ChatGPT Slack trigger remains non-authoritative.

## 4. Governed Slack outbound gate

Create a fresh synthetic PENDING L4 approval owned by canonical principal `michael` with a new immutable 64-hex `payload_fingerprint`. Invoke the CoS `slack-adapter` using `operation: post_approval`.

PASS requires `execution_mode: SLACK_BOT_API`, a Slack-returned root thread binding, a reply-driven approval notice instructing `APPROVE`, `DENY`, or `CHANGE`, no approval buttons, and unchanged PENDING approval state.

## 5. Native dispatcher gate

Use the existing **Mesh Slack HITL Dispatcher**. Do not create a second task and do not pin it to this patch release. Keep the trigger and condition unchanged and retain the prompt label:

`Act as the production Mesh Slack HITL Dispatcher for Mesh CoS MCP v4.x.`

The dispatcher must continue to pass only root-thread timestamp and reply-message timestamp to `skills.invoke_governed` / `slack-adapter` / `reconcile_triggered_message`. It must not pass decision text, asserted sender identity, approval state, actor, principal, user ID, or an approval boolean.

## 6. Incident replay gate

The first live human interaction must close the prior production defects with a fresh synthetic approval.

From the new bound Slack thread, send an approval reply using Slack bold formatting and confirm the provider representation is `*APPROVE*`.

PASS requires the Work dispatcher records an event-triggered run; Mesh CoS MCP reconciliation succeeds instead of returning `execution_failed`; QNAP independently retrieves the exact reply through GET/query `conversations.replies`; the canonical approval becomes `APPROVED`; the task becomes `READY_FOR_ACTION`; exactly one decision is recorded; replay of the same locators returns the same canonical result idempotently; and the audit chain remains valid.

Do not reuse the prior v4.2.1/v4.2.2 synthetic approvals as E2E proof.

## 7. Full human interaction gate

After the incident replay passes, verify bare and bold exact `APPROVE`, `DENY`, and `CHANGE` forms.

Nested or partial formatting such as `**APPROVE**`, `*APPROVE* extra`, formatted non-decision text such as `*looks good*`, wrong user, wrong channel, app/bot-authored reply, root message, unbound thread, edited message, deleted/unavailable message, malformed locator, stale payload fingerprint, and conflicting second decision must all fail closed.

For **CHANGE**, the bot asks what should change; the next independently reconciled human reply becomes untrusted governed change input, supersedes the old approval, returns the task to `IN_PROGRESS`, and requires a new immutable approval before consequential action.

## 8. Provider degradation and diagnostic gate

Slack provider/network failure must not be converted into approval authority. Runtime reconciliation fails closed and the approval remains unresolved. Deployment verification may retry only a pre-provider network exception within its bounded readiness window. Runtime diagnostics may include only sanitized provider codes such as `missing_scope`, `invalid_arguments`, `invalid_response`, `network_error`, or `unknown_error`; they must not expose the OAuth token, Authorization header, full provider response, or `response_metadata`.

MCP HTTP health remains independently observable. QNAP does not reconnect a Slack WebSocket because no Slack WebSocket listener exists.

## 9. Audit and lifecycle

Verify `governance.verify_audit_chain` before and after synthetic writes. Lifecycle must preserve `COMPLETED != VERIFIED`. Synthetic task idempotency and bounded validation errors must remain intact.

## 10. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability overrides, or other real-world consequential actions during acceptance.

## 11. Pass rule

Hosted acceptance passes only when the actual v4.2.3 QNAP serving instance demonstrates release identity, healthy Secure MCP Tunnel/runtime, successful live Slack provider-read and qnet egress readiness, native HITL mode, dedicated-bot outbound identity, ChatGPT-native event dispatch, provider-retrieved `*APPROVE*` incident reconciliation, positive and negative synthetic decisions, CHANGE workflow, replay idempotency, authorization boundaries, TaskLedger persistence, and a valid audit chain.

Full production certification additionally requires `docs/chatgpt-published-app-production-acceptance-v4.2.3.md`, zero open CRITICAL/HIGH defects, and no required acceptance blocker.
