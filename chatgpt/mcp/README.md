# Mesh CoS MCP Contract

`mesh-cos-mcp.v1.json` is the protocol-facing contract for release `1.1.0`. ChatGPT uses the bundled MCP package over `LOCAL_STDIO`, following the same in-environment execution pattern used by the Mesh Revenue Intelligence Skill.

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

`MESH_COS_AGENT_ID` is validated against the checked-in agent allowlists. The tool catalog exposed by the MCP server is the exact allowlist for that bound agent, excluding human-only tools.

## Enforcement order

1. Start the checked-in MCP package with a registered local agent identity.
2. Publish only the bound agent's allowed MCP tools.
3. Validate tool arguments as bounded JSON objects.
4. Bridge the request to `mesh_cos.mcp_stdio_bridge`.
5. Enter `MCPRuntime`, never a generic dynamic execution path.
6. Recheck the per-agent allowlist and canonical registry.
7. Apply source, tool, action, L0-L5 authority, approval, and reliability controls.
8. Invoke only fixed server-side handlers and registered replay executors.
9. Persist canonical state in `TaskLedger` before non-canonical responses or mirrors.
10. Emit required `decision.v2` and `agent-event.v2` governance records.

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

`npm run check` compiles TypeScript, runs Node tests, launches a real stdio MCP client/server smoke path, verifies exact tool projection and human-only exclusion, writes and rereads canonical task state across separate MCP calls, checks safe denial behavior, and runs `npm audit --audit-level=high`.

## Deployment boundary

A remote MCP endpoint is optional and not required for ChatGPT-local operation. If a managed remote transport is introduced later, it must preserve the same `MCPRuntime`, registry, allowlists, authority, approval, audit, and canonical-state semantics. It cannot become an alternate or broader control plane.

<!-- mesh-cos-v2-shared-da -->
## v2.0.0 current architecture

The live Phase 1 runtime is a **10-agent** organization. The former repository-local Devil's Advocate agent and duplicate role Skill are removed. **Mesh Devil's Advocate** is an external **shared Skill** available only to Chief of Staff and CRO through governed Skill invocation. It is **advisory** only, cannot overwrite **canonical facts**, cannot execute external actions, and returns decision authority to the owning role or qualified human. `TaskLedger` remains canonical state; ChatGPT uses `LOCAL_STDIO` through `MCPRuntime` with deny-by-default allowlists, human-only approval/override paths, `check-chatgpt-packages.py` drift enforcement, and the 100% branch-aware coverage gate. Historical references to an 11-agent roster or a local Devil's Advocate role describe superseded releases only.

