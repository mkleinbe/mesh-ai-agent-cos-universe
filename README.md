# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment release: `v4.1.6 Secure MCP Published App Production Identity`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, and release evidence without widening the Phase 1 agent authority model or tool allowlists.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to Chief of Staff and CRO. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

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

`v4.1.6` makes the production serving release observable without changing the canonical authority contract.

Successful governed tool envelopes report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.6
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. `approval.record_decision` and `reliability.human_override` remain human-principal-only and absent from every agent catalog. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verifier operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

The published ChatGPT app has passed the ten-call sequential read-only acceptance sequence through the OpenAI Secure MCP Tunnel without HTTP 502, `invalid_session`, reconnect, or container restart. That baseline established hosted transport stability and identified the missing deployment-release observability now addressed by v4.1.6.

After deploying v4.1.6, repeat hosted acceptance and require the dual release identity above on every successful governed tool response.

Current operator and release references:

- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `docs/qnap-production-preflight.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.6.md`
- `docs/qnap-security-review-v4.1.6.md`
- `docs/release-4.1.6-secure-mcp-published-app-identity.md`

Production images are built from the verified release bundle/tag, recorded by immutable image identity, and activated through the governed QNAP deployment path.
