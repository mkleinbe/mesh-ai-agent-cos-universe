# ChatGPT Secure MCP Tunnel, Delegated Owner Execution, and Native Slack HITL Acceptance

Run this only after the **v4.3.0** QNAP deployment passes local deployment, preflight, verification, backup, and the live Slack provider-read/qnet egress-readiness gate. The published **Mesh CoS MCP** app reaches the QNAP runtime through the **OpenAI Secure MCP Tunnel**. The canonical MCP authority/runtime contract remains **4.0.0** and the deployment release is **4.3.0**.

v4.3.0 adds the governed `delegation.execute_owner` path for PF-057 while preserving the existing ChatGPT-native Slack dispatcher architecture and the v4.2.3 provider-read/qnet controls.

## 1. Local deployment identity

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires image `mesh-cos-mcp:qnap-v4.3.0`, healthy application/tunnel containers, and:

```text
mcp_version: 4.0.0
deployment_release: 4.3.0
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_mode: CHATGPT_NATIVE_EVENT_TRIGGER
slack_hitl_ready: true
```

## 2. Tool catalog and authority

The CoS-bound app exposes exactly 10 registered agents and **28 governed CoS agent tools**, including `delegation.execute_owner`. Human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent execution.

The external runtime remains process-bound to `agent_id=cos`. That transport identity must not authorize a child operation by itself. The delegated owner executor derives the canonical accountable owner server-side. The public owner-execution request must not expose an owner/principal selector.

## 3. Direct-report delegated owner matrix

Using fresh synthetic, non-consequential canonical tasks and delegations, prove each ACTIVE owner eligible for delegated work has a valid execute + complete route.

For each representative owner:

- create/use a canonical child task owned by that agent;
- create/use the canonical parent-to-child delegation;
- invoke `delegation.execute_owner` from the authorized delegator with `delegation_id`, `task_id`, allowed `tool_name`, bounded `arguments`, and a unique `idempotency_key`;
- confirm the operation is authorized by the child's allowlist rather than the parent's;
- confirm owner-scoped audit attribution;
- confirm the owner can complete its task;
- confirm direct parent `task.complete` against the child task is denied.

PASS requires no caller-selected principal, no owner substitution, no parent impersonation, and no stranded canonical child task.

## 4. Nested delegation

Prove both canonical nested paths:

- `cos -> cmo -> vp-content`
- `cos -> coo -> consultant-network-steward`

The outer owner must use its derived execution context to invoke the nested `delegation.execute_owner` route. The nested child must execute only when Agent Registry lineage, delegation ancestry/depth, task ownership, and tool permission all agree.

Zero-depth, wrong-parent, missing-child, owner mismatch, ancestry mismatch, authority mismatch, and permitted-action escalation cases must fail closed.

## 5. Idempotency and routing failure

Repeat an already successful owner execution with the same canonical inputs and idempotency key.

PASS requires the same canonical result and no second owner execution or duplicate audit write.

A conflicting retry, failed prior execution, concurrent duplicate claim, disabled/quarantined owner, missing route, or unavailable owner must not execute the operation a second time and must preserve the task/delegation for recovery.

## 6. Completion and verification boundary

Prove:

- child owner completion produces `COMPLETED`;
- parent/CoS direct completion of child-owned work is denied;
- completion does not imply `VERIFIED`;
- only the separately authorized verifier may transition to `VERIFIED`;
- verification evidence and audit remain separate from completion evidence.

## 7. Scheduled CoS-to-owner path

Use a synthetic scheduled CoS trigger that resolves to delegated CMO-owned work.

PASS requires:

```text
scheduled CoS trigger
-> canonical delegation
-> server-derived CMO owner route
-> CMO execution/completion
-> exact replay idempotency
-> separate verification
```

No schedule prompt may select or impersonate the owner.

## 8. Slack protected configuration, qnet readiness, and provider-read gate

The governed human principal is Michael/MK. The protected QNAP Slack bindings remain the approver user ID and `xoxb-` bot OAuth token. The legacy `xapp-` Socket Mode token is not required or mounted. The installed bot identity remains **ChatGPT Enterprise AI Agent** and the provider-verified Slack App ID is `A0B49RNE4K0`.

The bot must have Bot Token Scopes `chat:write` and `groups:history` and be a member of `#mesh-agent-ops`. Do not print or cat protected credential files during acceptance.

`mesh-cos-mcp-verify.sh` must already have passed its live GET/query `conversations.history` provider-read probe from the running container. Only a pre-provider qnet/network exception may retry. A Slack `ok:false` response, malformed response, invalid credential, missing scope, or missing channel access fails immediately.

## 9. Governed Slack outbound and native dispatcher gate

Create a fresh synthetic PENDING L4 approval owned by canonical principal `michael` with a new immutable 64-hex `payload_fingerprint`. Invoke the CoS `slack-adapter` using `operation: post_approval`.

PASS requires `execution_mode: SLACK_BOT_API`, a Slack-returned root thread binding, a reply-driven approval notice instructing `APPROVE`, `DENY`, or `CHANGE`, no approval buttons, and unchanged PENDING approval state.

Use the existing **Mesh Slack HITL Dispatcher**. Do not create a second task and do not pin it to this patch release. Keep the prompt label:

`Act as the production Mesh Slack HITL Dispatcher for Mesh CoS MCP v4.x.`

The dispatcher passes only root-thread timestamp and reply-message timestamp to `skills.invoke_governed` / `slack-adapter` / `reconcile_triggered_message`. It must not pass decision text, asserted sender identity, approval state, actor, principal, user ID, or an approval boolean.

## 10. Slack incident replay and human interaction matrix

From a new bound Slack thread, send an approval reply whose provider representation is `*APPROVE*`.

PASS requires the Work dispatcher records an event-triggered run; QNAP independently retrieves the exact reply through GET/query `conversations.replies`; the canonical approval becomes `APPROVED`; the task becomes `READY_FOR_ACTION`; exactly one decision is recorded; replay of the same locators is idempotent; and the audit chain remains valid.

Then verify bare and bold exact `APPROVE`, `DENY`, and `CHANGE` forms. Wrong user, wrong channel, app/bot-authored reply, root message, unbound thread, edited/deleted/unavailable message, malformed locator/formatting, stale fingerprint, conflicting decision, and provider failure must all fail closed.

For **CHANGE**, the next independently reconciled human reply becomes untrusted governed change input, supersedes the old approval, returns the task to `IN_PROGRESS`, and requires a new immutable approval before consequential action.

## 11. Audit and lifecycle

Verify `governance.verify_audit_chain` before and after synthetic writes. Owner execution audit must identify the canonical owner operation while retaining the orchestrating/delegating context. No owner event may be falsely attributed to CoS merely because the external MCP process is CoS-bound.

## 12. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability overrides, or other real-world consequential actions during acceptance.

## 13. PF-057 recovery boundary

Do not recover stranded production work until all prior acceptance sections pass. Then re-run the read-only stranded-task inventory and re-read `task-b0b613daff51`.

That task must remain the same canonical task and, if still eligible for recovery, follow:

```text
existing QA
-> canonical owner cmo
-> governed owner completion
-> COMPLETED
-> separate verification where required
-> dependent gate release
```

Do not recreate the task by default.

## 14. Pass rule

Hosted acceptance passes only when the actual v4.3.0 QNAP serving instance demonstrates release identity, healthy Secure MCP Tunnel/runtime, 10-agent registry, 28-tool CoS catalog, direct-report and nested delegated-owner execution, owner-only completion, replay idempotency, disabled-owner failure, scheduled cross-agent execution, completion/verification separation, successful live Slack provider-read/qnet readiness, dedicated-bot outbound identity, ChatGPT-native event dispatch, positive and negative Slack decisions, TaskLedger persistence, and a valid audit chain.

Full production certification additionally requires `docs/chatgpt-published-app-production-acceptance-v4.3.0.md`, zero open CRITICAL/HIGH defects, and no required acceptance blocker.
