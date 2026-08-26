# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this after the **v4.1.10** `mesh-cos-mcp-deploy.sh` path reports successful deployment, verification, and post-deploy backup.

The production ChatGPT surface is the published **Mesh CoS MCP** app connected to the QNAP-hosted MCP runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 authority/runtime contract remains **4.0.0**. The QNAP deployment release is independently identified as **4.1.10**.

v4.1.10 carries forward the v4.1.8 request-contract remediation and v4.1.9 documentation closeout while adding scheduled idempotency/lifecycle, official OpenAI bot-notice verification, and provider-authenticated Slack Socket Mode human approval.

## 1. Local deployment identity

After deployment, capture:

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>r.text()).then(console.log)"
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires the v4.1.10 application image, both containers healthy, and status identity:

```text
mcp_version: 4.0.0
deployment_release: 4.1.10
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_ready: true
```

Do not print the protected Slack identity, verifier credential, or Socket Mode app-level credential as part of acceptance.

## 2. Tool catalog

The CoS-bound published app must expose exactly **27 agent-facing tools**. Human-principal-only `approval.record_decision` and `reliability.human_override` must not appear. The canonical roster remains exactly 10 agents; Mesh Devil's Advocate remains a governed shared Skill rather than an agent principal.

## 3. Request-contract and scheduled idempotency acceptance

### Valid intake

Create one clearly synthetic L0 task with the documented `task.intake` fields and an explicit `idempotency_key`. Repeat the request with the same key. PASS requires the same canonical task ID on both calls.

### Invalid intake

Call `task.intake` while omitting `accountable_agent`. PASS requires bounded `validation_failed` details and no raw exception, stack trace, secret, filesystem detail, or private reasoning.

### Canonical task lookup

For an existing synthetic task, `task.get` and `task.decompose` using `parent_task_id` must resolve the same canonical identifier. An undocumented alias must fail as request validation.

## 4. Governed Skill and Slack adapter acceptance

Call `skills.invoke_governed` for CoS capability `mesh-ppmd-bot` using a synthetic, non-consequential payload. PASS requires a bounded `CHATGPT_SKILL_HANDOFF` authorization result.

The CoS `slack-adapter` is server-owned and must accept only the bot-notice binding operation:

```text
bind_notice: operation, approval_id, thread_ts, payload_fingerprint
```

Any `ingest_decision`, `approved`, actor/principal override, channel override, or arbitrary Slack event data must fail closed. `approval.record_decision` must remain unavailable to the CoS.

A successful `bind_notice` is not established by prompt or Slack text alone. The server must re-read provider state and persist a **provider-verified** binding proving the parent author is an allowlisted official OpenAI identity and that the exact Approval ID, channel/thread, approver mapping, and payload fingerprint reconcile.

The human approval path is deliberately **not** an MCP tool. It is the QNAP-hosted Socket Mode `/mesh-approval` interaction boundary defined in `chatgpt-published-app-production-acceptance-v4.1.10.md`.

## 5. AgentOps acceptance

`agentops.recommend` with the documented minimum contract (`agent_id: cos`) must succeed. Invalid field names or malformed values must return the same safe structured validation contract used by other tools.

## 6. Lifecycle acceptance

Use a separate synthetic task. Advance it through:

```text
INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA
```

Call `task.complete` with non-empty outcome and evidence. PASS requires `status=COMPLETED` and no verification yet.

Only a separate expressly authorized `task.verify` with acceptance evidence may move it to `VERIFIED`. Verification before completion, verification without evidence, or unauthorized verification must fail closed.

## 7. Audit integrity

Call `governance.verify_audit_chain` before and after synthetic acceptance writes. PASS requires `valid: true` both times.

## 8. Slack human-interaction base gate

The QNAP runtime must be configured with:

- protected approver identity file;
- read-only provider verifier `xoxb-` credential;
- read-only Socket Mode `xapp-` credential;
- `MESH_COS_SLACK_APPROVAL_COMMAND=/mesh-approval`;
- active Socket Mode connection, reflected by `slack_hitl_ready=true`.

An ordinary Slack message attributed to MK is not sufficient human-authentication evidence and must never alter canonical approval state. Full synthetic proof of the `/mesh-approval` path is performed in the production acceptance document.

## 9. Multi-agent boundary

Repository/container certification establishes immutable `MESH_COS_AGENT_ID` binding and exact allowlists for all 10 agents. Do not claim a downstream agent has independently authenticated to the hosted production interface unless a distinct bound session is actually provisioned and tested. A CoS session reading another registry record is not equivalent evidence.

## 10. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability human overrides, or any other consequential real-world action during base acceptance.

The v4.1.10 Slack acceptance uses a synthetic no-op approval only and must not create a Gmail send or external effect.

## 11. Pass rule

Base v4.1.10 hosted acceptance passes only when the actual Mesh CoS MCP app demonstrates correct deployment identity, `slack_hitl_ready=true`, exact schema behavior, safe validation, canonical TaskLedger lookup, explicit scheduled idempotency, valid lifecycle separation, governed Skill/adapter enforcement, AgentOps contract, authorization boundaries, and valid audit chain.

Full production certification additionally requires `chatgpt-published-app-production-acceptance-v4.1.10.md`, including the official OpenAI bot-authored Slack notice, the Socket Mode `/mesh-approval` human interaction, canonical approval readback, proof ordinary Slack messages cannot approve, no unauthorized external action, and required TaskLedger mirror reconciliation. Zero open CRITICAL/HIGH defects and no required acceptance blocker are mandatory.
