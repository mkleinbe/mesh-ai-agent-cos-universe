# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.1.10 Scheduled Automation and Slack HITL Hardening`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, scheduled execution, Slack HITL, request contract, and release evidence without widening the Phase 1 agent authority model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface:

```text
ChatGPT / Mesh CoS MCP app
  -> OpenAI Secure MCP Tunnel
  -> mesh-cos-tunnel 172.30.60.3
  -> mesh-cos-mcp 172.30.60.2 + 192.168.7.60
  -> canonical mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger SQLite
```

Local engineering and deterministic certification retain stdio:

```text
local MCP client
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> canonical MCPRuntime
  -> TaskLedger SQLite
```

The QNAP application lives at `/share/Docker/cos-mcp`, uses the verified external QNAP `lan7` qnet, and is deployed with scripts run from `/share/Docker`. The MCP protocol port is not published to the host or public internet. Production `/mcp` requests are accepted only from the Secure MCP Tunnel sidecar private source address.

## Dual release identity

Successful governed tool envelopes for v4.1.10 must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.10
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`. When Slack HITL is required, readiness also reports `slack_hitl_ready=true` only while the authenticated Socket Mode boundary is active.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## v4.1.10 hardening

v4.1.10 closes production-acceptance defects in scheduled exact-once execution and Slack human approval:

1. Scheduled logical occurrences pass an immutable execution identity as the explicit `task.intake.idempotency_key`.
2. Scheduled execution progresses through `INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA` before `task.complete`; `task.verify` remains separate.
3. Governed Slack HITL notices are valid only when provider state attributes the parent to the official ChatGPT or ChatGPT Agents Slack identity.
4. The Slack identity for MK is protected runtime configuration and is never committed or logged.
5. The existing CoS `slack-adapter` exposes `bind_notice` only. Agents cannot ingest, infer, or submit a human approval decision.
6. Canonical Slack human decisions enter through a separately authenticated, non-MCP Slack Socket Mode `/mesh-approval` interaction boundary.
7. Ordinary Slack messages remain non-authoritative even when attributed to the configured human identity.
8. `approval.record_decision` and `reliability.human_override` remain human-principal-only.
9. QNAP file-mounts the Slack approver identity, provider-verifier bot credential, and Socket Mode app-level credential and fails production readiness when required HITL controls cannot initialize/remain active.
10. The generic user-scoped Slack connector is not a governed notice-author or human-approval transport. If the official OpenAI Workspace Agent delivery path is unavailable, the workflow fails closed as `BLOCKED_CHATGPT_AGENT_TRANSPORT`.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, Slack text, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verification operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

Repository, CI, container, and release-package verification do not prove the newly deployed on-premises serving instance, the official OpenAI Workspace Agent Slack delivery configuration, or the live Socket Mode human-interaction path.

After deploying v4.1.10, execute the synthetic hosted acceptance in `docs/chatgpt-published-app-production-acceptance-v4.1.10.md`. Production certification requires the actual bot-authored HITL notice, proof an ordinary APPROVE message remains non-authoritative, a provider-authenticated `/mesh-approval` interaction by MK, fresh canonical approval readback, valid audit chain, zero unauthorized external actions, and required TaskLedger operating-mirror reconciliation.

Current operator and release references:

- `SECURITY.md`
- `RELEASE.md`
- `docs/production-readiness.md`
- `docs/slack-agent-protocol.md`
- `docs/qnap-security-review-v4.1.10.md`
- `docs/release-4.1.10-scheduled-slack-hitl.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.10.md`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `deployment/qnap/install-checklist.md`
- `deployment/qnap/upgrade-checklist.md`

Historical versioned documents remain retained as release-train evidence.
