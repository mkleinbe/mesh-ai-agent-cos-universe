# v1.1.0 Local ChatGPT MCP

`v1.1.0` refactors the Mesh AI Chief of Staff MCP so the governed CoS runtime can execute inside the ChatGPT environment through a bundled local stdio MCP package, following the same architectural pattern used by the Mesh Revenue Intelligence Skill.

## What changed

- Replaced the required remote HTTPS MCP deployment model with `LOCAL_STDIO` for ChatGPT operation.
- Added the checked-in TypeScript MCP package under `mcp/` using the official Model Context Protocol SDK.
- Added `mesh_cos.mcp_stdio_bridge` as the bounded JSON bridge into the existing Python `MCPRuntime`.
- Preserved `mesh_cos.mcp_runtime.MCPRuntime` as the sole business/governance execution core.
- Added immutable per-process agent binding through `MESH_COS_AGENT_ID`.
- Added shared canonical local state through `MESH_COS_LEDGER_PATH`.
- Preserved exact per-agent MCP allowlists and deny-by-default policy.
- Kept `approval.record_decision` and `reliability.human_override` human-only and outside every agent catalog.
- Added local MCP argument bounds, safe error categories, raw-stderr suppression, and no client-supplied code execution.
- Added real stdio MCP certification that verifies tool projection, human-only exclusion, canonical persistence across calls, and safe denial behavior.
- Added TypeScript build/tests and npm security audit to release CI.
- Removed the remote `MESH_COS_MCP_SERVER_URL` requirement from ChatGPT activation.
- Updated all 11 Workspace Agent manifests, role production-readiness references, Builder instructions, preflight, tests, and current operating documentation for the local runtime.

## Preserved governance

The deployment change does not broaden agent authority. `TaskLedger` remains canonical. L4 continues to require qualified human approval. L5 remains Michael-exclusive. `task.complete` remains separate from `task.verify`. Replay remains restricted to server-registered executors referenced by canonical failure state. `decision.v2` and `agent-event.v2` remain the explainability and audit contracts.

## Release quality gates

Release acceptance requires:

- Python dependency integrity;
- `npm ci` for the MCP package;
- TypeScript compilation;
- Node MCP unit tests;
- local stdio MCP smoke certification;
- npm audit at high severity;
- contract validation;
- runtime/documentation drift validation;
- Workspace Agent package drift validation;
- strict source Ruff;
- mypy;
- **100% branch-aware `mesh_cos` coverage**;
- Bandit high-severity scan;
- compileall.

## Production activation boundary

The repository does not fabricate Workspace app credentials, Slack secrets, the dedicated Answer Desk Slack channel, approval-owner mappings, source credentials, automatic Google Sheets credentials, secrets management, monitoring, or Workspace publication/RBAC configuration. Those remain target-environment dependencies.

A separately deployed remote MCP service is optional and is not required for ChatGPT-local operation.

## Release identity

- Semantic version: `1.1.0`
- Semantic Tag: `v1.1.0`
- Release title: `v1.1.0 Local ChatGPT MCP`
- ChatGPT MCP transport: `LOCAL_STDIO`
- Local entry point: `node mcp/dist/index.js`
- Canonical runtime: `mesh_cos.mcp_runtime.MCPRuntime`
- Canonical state: `TaskLedger`
- Workspace Agent count: 11

See `docs/release-1.1.0-local-chatgpt-mcp.md` for the detailed release record.
