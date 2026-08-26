# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this after the **v4.1.8** `mesh-cos-mcp-deploy.sh` path reports successful deployment, verification, and post-deploy backup.

The production ChatGPT surface is the published **Mesh CoS MCP** app connected to the QNAP-hosted MCP runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 MCP authority/runtime contract remains **4.0.0**. The QNAP deployment release is independently identified as **4.1.8**.

v4.1.8 specifically closes request-schema drift, opaque validation, request-binding versus canonical lookup ambiguity, missing runtime registration for declared governed Skills, and AgentOps request-contract drift.

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

PASS requires the v4.1.8 application image, both containers healthy, and status identity:

```text
mcp_version: 4.0.0
deployment_release: 4.1.8
agent_id: cos
transport: SECURE_MCP_TUNNEL
```

## 2. Tool catalog

The CoS-bound published app must expose exactly **27 agent-facing tools**. Human-principal-only `approval.record_decision` and `reliability.human_override` must not appear. The canonical roster remains exactly 10 agents; Mesh Devil's Advocate remains a governed shared Skill rather than an agent principal.

## 3. Request-contract acceptance

### Valid intake

Create one clearly synthetic L0 task with the documented `task.intake` fields and an idempotency key. PASS requires a canonical TaskRecord and the same task ID if the request is repeated with that key.

### Invalid intake

Call `task.intake` while omitting `accountable_agent`. PASS requires:

```text
ok: false
error: validation_failed
details:
  - field: accountable_agent
    reason: required
```

No raw exception, stack trace, secret, filesystem detail, or private reasoning may appear.

### Canonical task lookup

For an existing synthetic task, `task.get` and `task.decompose` using `parent_task_id` must resolve the same canonical identifier. An undocumented alias such as `parent` must fail as request validation, not as resource `not_found`.

## 4. Governed Skill acceptance

Call `skills.invoke_governed` for CoS capability `mesh-ppmd-bot` using a synthetic, non-consequential payload. PASS requires a bounded authorization/handoff result with:

```text
status: AUTHORIZED
execution_mode: CHATGPT_SKILL_HANDOFF
agent_id: cos
capability: mesh-ppmd-bot
```

This result authorizes the ChatGPT Skill runtime handoff; it is not arbitrary QNAP code execution.

A nonexistent capability must fail closed as `not_found`. A capability known to another role but not allowlisted for CoS must fail closed as `forbidden`. Payload fields attempting to provide code, import paths, callables, shell commands, plugin executables, or Skill implementations must return `validation_failed` and must never execute.

## 5. AgentOps acceptance

`agentops.recommend` with the documented minimum contract:

```text
agent_id: cos
```

must succeed. Invalid field names or malformed values must return the same safe structured validation contract used by other tools.

## 6. Lifecycle acceptance

Use a separate synthetic task if lifecycle testing is required. Move it through a valid working path and call `task.complete` with non-empty outcome and evidence. PASS requires `status=COMPLETED` and `verified_at=null`.

Only a separate expressly authorized `task.verify` action with acceptance evidence may move it to `VERIFIED`. Verification before completion, verification without evidence, or unauthorized verification must fail closed.

## 7. Audit integrity

Call `governance.verify_audit_chain` before and after synthetic acceptance writes. PASS requires `valid: true` both times.

## 8. Multi-agent boundary

Repository/container certification establishes immutable `MESH_COS_AGENT_ID` binding and exact allowlists for all 10 agents. Do not claim a downstream agent has independently authenticated to the hosted production interface unless a distinct bound session for that agent is actually provisioned and tested. A CoS session reading another registry record is not equivalent evidence.

## 9. Consequential-action exclusion

Do not perform external sends, public publishing, client commitments, pricing or discount approvals, final staffing commitments, human approval decisions, reliability human overrides, or other consequential real-world actions during acceptance.

## 10. Pass rule

v4.1.8 is production-accepted only when the actual hosted Mesh CoS MCP app demonstrates the expected deployment envelope, exact schema behavior, safe validation, canonical TaskLedger lookup, governed Skill enforcement, AgentOps contract, lifecycle separation, authorization boundaries, and valid audit chain.
