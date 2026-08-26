# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this only after the **v4.1.11** versioned deployment path reports successful candidate health, promotion, verification, and post-deploy backup.

The production ChatGPT surface is the published **Mesh CoS MCP** app connected to the QNAP-hosted runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 authority/runtime contract remains **4.0.0**. The QNAP deployment release is independently identified as **4.1.11**.

v4.1.11 carries forward the v4.1.10 scheduled idempotency/lifecycle and Slack HITL hardening while correcting the QNAP release staging and promotion contract.

## 1. Local deployment identity

Capture:

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>r.text()).then(console.log)"
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires application image `mesh-cos-mcp:qnap-v4.1.11`, both containers healthy, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.11
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_ready: true
```

Do not print protected Slack or tunnel files as part of acceptance.

## 2. Release-staging evidence

Confirm the retained release directory exists at `/share/Docker/cos-mcp/releases/v4.1.11`. Active `.env`, active Compose, and active `release-metadata.txt` must all identify the promoted v4.1.11 deployment. The staged `release-metadata.txt` commit must match the released artifact commit. Do not delete the versioned release directory during acceptance.

## 3. Tool catalog

The CoS-bound published app must expose exactly **27 agent-facing tools**. Human-principal-only `approval.record_decision` and `reliability.human_override` must not appear. The canonical roster remains exactly 10 agents; Mesh Devil's Advocate remains a governed shared Skill rather than an agent principal.

## 4. Request-contract and scheduled idempotency acceptance

Create one synthetic L0 task with the documented `task.intake` fields and an explicit `idempotency_key`. Repeat the request with the same key. PASS requires the same canonical task ID on both calls.

Call `task.intake` while omitting `accountable_agent`. PASS requires bounded `validation_failed` details and no raw exception, stack trace, secret, filesystem detail, or private reasoning.

For an existing synthetic task, `task.get` and `task.decompose` using `parent_task_id` must resolve the same canonical identifier. An undocumented alias must fail as request validation.

## 5. Governed Skill and Slack adapter acceptance

Call `skills.invoke_governed` for an authorized CoS Skill using a synthetic, non-consequential payload. PASS requires bounded `CHATGPT_SKILL_HANDOFF` authorization behavior.

The CoS `slack-adapter` remains notice-binding only. It may bind provider-verified notice evidence but cannot ingest, infer, or submit a human approval decision. Any human-decision fields or operations must fail closed. `approval.record_decision` remains unavailable to the CoS.

The human approval path is deliberately **not** an MCP tool. It is the QNAP-hosted authenticated Socket Mode `/mesh-approval` interaction boundary tested in `chatgpt-published-app-production-acceptance-v4.1.11.md`.

## 6. AgentOps acceptance

`agentops.recommend` with the documented minimum contract must succeed. Invalid field names or malformed values must return the same safe structured validation contract used by other tools.

## 7. Lifecycle acceptance

Use a separate synthetic task and advance it through:

```text
INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA
```

Call `task.complete` with non-empty outcome and evidence. PASS requires `status=COMPLETED` and no verification yet. Only a separate authorized `task.verify` with acceptance evidence may move it to `VERIFIED`.

## 8. Audit integrity

Call `governance.verify_audit_chain` before and after synthetic acceptance writes. PASS requires `valid: true` both times.

## 9. Slack human-interaction base gate

The runtime must have the protected approver identity, provider verifier bot credential, Socket Mode app credential, `/mesh-approval` command configuration, and active Socket Mode connection reflected by `slack_hitl_ready=true`.

Ordinary Slack text attributed to MK is not sufficient human-authentication evidence and must never alter canonical approval state.

## 10. Multi-agent boundary

Repository/container certification establishes immutable `MESH_COS_AGENT_ID` binding and exact allowlists for all 10 agents. A CoS session reading another registry record is not equivalent to a separately authenticated downstream-agent hosted session.

## 11. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability human overrides, or other consequential real-world actions during acceptance. Slack acceptance uses a synthetic no-op approval only.

## 12. Pass rule

Base v4.1.11 hosted acceptance passes only when the actual Mesh CoS MCP app demonstrates correct dual release identity, `slack_hitl_ready=true`, exact schema behavior, safe validation, canonical TaskLedger lookup, scheduled idempotency, lifecycle separation, governed Skill/adapter enforcement, AgentOps contract, authorization boundaries, and valid audit chain.

Full production certification additionally requires `chatgpt-published-app-production-acceptance-v4.1.11.md`, including the official OpenAI bot-authored notice, authenticated `/mesh-approval` human interaction, canonical approval readback, proof ordinary Slack text cannot approve, no unauthorized external action, and required TaskLedger mirror reconciliation. Zero open CRITICAL/HIGH defects and no required acceptance blocker are mandatory.
