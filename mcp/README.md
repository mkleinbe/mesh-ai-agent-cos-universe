# Mesh CoS MCP

This package is the bundled Model Context Protocol transport for the Mesh AI Chief of Staff operating core.

## Runtime model

`mesh-cos-mcp` now follows the same primary runtime pattern as Mesh Revenue Intelligence: ChatGPT launches a local stdio MCP process from the checked-in package. A separately managed remote transport is optional and is not required for Workspace Agent operation.

The TypeScript MCP layer is intentionally thin. It does not duplicate task, authority, governance, approval, reliability, or AgentOps business logic. Every allowed tool call is bridged to `mesh_cos.mcp_stdio_bridge`, which creates the canonical Python `MCPRuntime` against the configured `TaskLedger` SQLite file.

```text
ChatGPT Workspace Agent
        |
        | local stdio MCP
        v
mcp/dist/index.js
        |
        | bounded JSON bridge
        v
mesh_cos.mcp_stdio_bridge
        |
        v
mesh_cos.mcp_runtime.MCPRuntime
        |
        v
TaskLedger SQLite
```

## Required runtime environment

- `MESH_COS_AGENT_ID`: the exact canonical agent ID for the Workspace Agent launching this MCP process.
- `MESH_COS_LEDGER_PATH`: path to the shared canonical SQLite TaskLedger. All 11 agents must use the same approved path for one operating universe.
- `MESH_COS_KILL_SWITCH`: optional emergency stop. Truthy values fail closed.
- `MESH_COS_PYTHON_BIN`: optional Python executable override. Defaults to `python`.

No `MESH_COS_MCP_SERVER_URL` is required for the ChatGPT runtime.

## Security and governance

The local server loads `chatgpt/mcp/mesh-cos-mcp.v1.json`, projects only the tool allowlist for the bound agent, and never exposes human-only `approval.record_decision` or `reliability.human_override` to an agent stdio process. The Python runtime independently re-authorizes the agent and tool. This gives two fail-closed enforcement layers.

Client-supplied code, import paths, callables, shell commands, and replay functions are not executable inputs. Tool arguments and bridge responses are size bounded. Errors returned to the MCP client use safe categories and do not echo raw payloads.

`TaskLedger` remains canonical. ChatGPT conversation state, Slack, connector output, and governance Sheets are interaction or mirror surfaces.

## Development and certification

From `mcp/`:

```bash
npm ci
npm run check
```

`npm run check` performs strict TypeScript compilation, Node unit tests, and a real MCP stdio smoke certification using the official MCP client and transport. The smoke test proves exact CoS tool projection, local canonical persistence across calls, human-only tool exclusion, and safe denial behavior.

The repository CI runs this MCP gate in addition to the Python release gates, including 100% branch-aware `mesh_cos` coverage.

<!-- mesh-cos-v2-shared-da -->
## v2.0.0 current architecture

The live Phase 1 runtime is a **10-agent** organization. The former repository-local Devil's Advocate agent and duplicate role Skill are removed. **Mesh Devil's Advocate** is an external **shared Skill** available only to Chief of Staff and CRO through governed Skill invocation. It is **advisory** only, cannot overwrite **canonical facts**, cannot execute external actions, and returns decision authority to the owning role or qualified human. `TaskLedger` remains canonical state; ChatGPT uses `LOCAL_STDIO` through `MCPRuntime` with deny-by-default allowlists, human-only approval/override paths, `check-chatgpt-packages.py` drift enforcement, and the 100% branch-aware coverage gate. Historical references to an 11-agent roster or a local Devil's Advocate role describe superseded releases only.

