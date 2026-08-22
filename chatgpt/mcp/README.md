# Mesh CoS MCP Contract

`mesh-cos-mcp.v1.json` is the protocol-facing contract for release `4.0.0`. ChatGPT uses the bundled MCP package over `LOCAL_STDIO`.

The MCP package is a transport adapter, not a second business-logic implementation.

## Runtime path

```text
Workspace Agent
  -> MESH_COS_AGENT_ID
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger
```

The canonical MCP principal roster contains exactly 10 agents. Mesh Devil's Advocate is not an MCP principal.

## Agent versus human catalogs

`agent_tool_allowlists` is deny-by-default and keyed by the 10 registered agent identities. `human_tool_allowlist` is a separate catalog containing exactly:

- `approval.record_decision`
- `reliability.human_override`

No agent allowlist may contain either human-only operation. Agent stdio servers project only the allowlist for their bound `MESH_COS_AGENT_ID`. `MCPRuntime.call_agent` independently denies human-only tools. `MCPRuntime.call_human` requires an authenticated non-empty human principal.

## Completion contract

`task.complete` is exposed to appropriate accountable owners. The runtime requires owner-or-CoS write access, a valid completion state, a non-empty outcome, and supporting evidence. Successful completion produces `COMPLETED` only.

`task.verify` is separate. It is exposed only to CoS in the Phase 1 agent catalog and requires explicit acceptance evidence for a passing result.

## Delegation

`delegation.create` requires a registered direct child. Delegated authority cannot exceed parent authority, parent approval gates cannot be dropped, and depth cannot exceed the Phase 1 ceiling. The legal depth-2 specialist path is CoS -> COO -> Consultant Network Steward.

## Identity and content safety

Prompt text, retrieved content, task content, delegated instructions, connector output, and Skill output cannot modify `MESH_COS_AGENT_ID`, add tools to the projected catalog, or create a human principal.

## Certification

`npm run check` runs TypeScript build, Node tests, a real local stdio smoke test, and npm audit. The smoke test certifies the 10-agent roster, human-only exclusion, Devil's Advocate principal exclusion, local canonical persistence, and safe denial behavior.