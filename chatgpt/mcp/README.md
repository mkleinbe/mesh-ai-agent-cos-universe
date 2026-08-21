# Mesh CoS MCP Contract

`mesh-cos-mcp.v1.json` is the protocol-facing contract for release `2.0.0`. ChatGPT uses the bundled MCP package over `LOCAL_STDIO`, following the same in-environment execution pattern used by the Mesh Revenue Intelligence Skill.

The MCP package is a transport adapter, not a second business-logic implementation.

## Runtime path

```text
Workspace Agent
  -> LOCAL_STDIO
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger
```

## Local process binding

Each process requires:

```text
MESH_COS_AGENT_ID=<registered agent id>
MESH_COS_LEDGER_PATH=.mesh-cos/task-ledger.sqlite3
MESH_COS_PYTHON_BIN=python
```

`MESH_COS_AGENT_ID` is validated against the checked-in **10 agent** allowlists. The former `devils-advocate` agent ID is not a valid MCP principal. The tool catalog exposed by the MCP server is the exact allowlist for the bound agent, excluding human-only tools.

## Shared Mesh Devil's Advocate boundary

**Mesh Devil's Advocate** is an external **shared Skill**, not an MCP agent principal. Only Chief of Staff and CRO may invoke it through `skills.invoke_governed` under their existing identities. The challenge capability has no independent MCP identity, does not own canonical state, is **advisory** only, cannot modify canonical facts, and cannot execute external actions.

For Revenue Intelligence work, canonical account identity, evidence classes, scores, stage, lifecycle, queue state, activation readiness, and prioritization remain with Revenue Intelligence. The shared Skill may challenge interpretation and decision logic without rewriting those facts.

## Enforcement order

1. Start the checked-in MCP package with a registered local agent identity.
2. Publish only the bound agent's allowed MCP tools.
3. Validate tool arguments as bounded JSON objects.
4. Bridge the request to `mesh_cos.mcp_stdio_bridge`.
5. Enter `MCPRuntime`, never a generic dynamic execution path.
6. Recheck the per-agent allowlist and canonical registry.
7. Apply source, tool, action, L0-L5 authority, approval, and reliability controls.
8. Permit governed shared-Skill invocation only where the registry and MCP allowlist both authorize it.
9. Invoke only fixed server-side handlers and registered replay executors.
10. Persist canonical state in `TaskLedger` before non-canonical responses or mirrors.
11. Emit required `decision.v2` and `agent-event.v2` governance records.

## Human-only operations

`approval.record_decision` and `reliability.human_override` are human-only. They are excluded from every agent tool catalog and require a separate authenticated human-principal path.

## Error handling

The local TypeScript MCP does not expose raw bridge stderr or arbitrary exception text to ChatGPT. Client-visible failures are reduced to safe categories and request identifiers. Request and response sizes are bounded.

## Replay safety

`reliability.replay` may execute only a server-registered replay executor referenced by canonical failure state. Client-supplied Python, import paths, shell commands, code snippets, or source-text instructions are never executable replay behavior.

## Completion and verification

`task.complete` persists accountable-owner outcome and evidence. `task.verify` is a separate acceptance action. `COMPLETED` does not imply `VERIFIED`.

## Certification

From the repository root:

```bash
cd mcp
npm ci
npm run check
```

`npm run check` compiles TypeScript, runs Node tests, launches a real stdio MCP client/server smoke path, verifies exact tool projection and human-only exclusion, verifies the 10-agent roster, writes and rereads canonical task state across separate MCP calls, checks safe denial behavior, and runs `npm audit --audit-level=high`.

## Deployment boundary

A remote MCP endpoint is optional and not required for ChatGPT-local operation. If a managed remote transport is introduced later, it must preserve the same `MCPRuntime`, registry, allowlists, authority, approval, audit, shared-Skill boundary, and canonical-state semantics. It cannot become an alternate or broader control plane.
