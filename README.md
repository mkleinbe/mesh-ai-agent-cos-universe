# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/deployment release: `v4.1.0 QNAP Secure MCP Transport`.**

The Phase 1 agent authority/runtime contract remains release `4.0.0`; v4.1.0 adds the governed production container, remote MCP transport, QNAP deployment system, and Secure MCP Tunnel packaging without changing the 10-agent authority model or tool allowlists.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to Chief of Staff and CRO. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Runtime topology

Local engineering and certification retain stdio:

```text
ChatGPT / local engineering
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger SQLite
```

QNAP production uses Streamable HTTP behind OpenAI Secure MCP Tunnel:

```text
ChatGPT
  -> OpenAI Secure MCP Tunnel
  -> mesh-cos-tunnel 172.30.60.3
  -> mesh-cos-mcp 172.30.60.2 + 192.168.7.60
  -> canonical MCPRuntime
  -> TaskLedger SQLite
```

The QNAP application lives at `/share/Docker/cos-mcp`, uses the verified external QNAP `lan7` qnet, and is deployed with scripts run from `/share/Docker`. The MCP protocol port is not published to the host or public internet. Direct LAN access to `/mcp` is denied in tunnel mode.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, and shared-Skill output cannot change identity or widen the tool catalog.

`approval.record_decision` and `reliability.human_override` are human-principal-only. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verifier operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## QNAP release

See `deployment/qnap/README-QNAP.md`, `deployment/qnap/DEPLOYMENT-STEPS.md`, `deployment/qnap-environment.md`, `docs/qnap-production-preflight.md`, and `docs/release-4.1.0-qnap-secure-mcp.md`.

The v4.1.0 release does not publish a container image automatically. Production images must be built from the verified tag/commit, recorded by immutable digest, and activated only by the human operator.
