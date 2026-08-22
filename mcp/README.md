# Mesh CoS MCP

This package is the bundled Model Context Protocol transport for the Mesh AI Chief of Staff operating core. Current repository release: **`v4.0.0 Chief of Staff Delegation Contract Remediation`**.

## Runtime model

ChatGPT launches the checked-in package as a local stdio MCP process. The TypeScript layer remains intentionally thin and bridges every permitted call into the canonical Python `MCPRuntime` using the configured `TaskLedger`.

```text
ChatGPT Workspace Agent
        |
        | LOCAL_STDIO
        v
node mcp/dist/index.js
        |
        v
mesh_cos.mcp_stdio_bridge
        |
        v
mesh_cos.mcp_runtime.MCPRuntime
        |
        v
TaskLedger SQLite
```

## Required environment

- `MESH_COS_AGENT_ID`: exact registered agent ID for the process.
- `MESH_COS_LEDGER_PATH`: canonical shared SQLite ledger path for the 10-agent operating universe.
- `MESH_COS_KILL_SWITCH`: optional emergency stop; truthy values fail closed.
- `MESH_COS_PYTHON_BIN`: optional Python executable override.

No remote MCP URL is required for ChatGPT-local operation.

## Roster and shared Skill boundary

The runtime contains exactly 10 registered agent principals, including Message Operations. Mesh Devil's Advocate remains an external shared Skill and is not a valid MCP principal.

## Human-only boundary

The protocol contract contains `approval.record_decision` and `reliability.human_override` so the same serialized runtime can service authenticated human actions, but neither operation appears in any agent tool catalog. Agent callers are denied. The human path requires a separately authenticated principal.

## Completion and verification

`task.complete` is the canonical owner completion operation and requires outcome plus evidence. It does not verify work. `task.verify` is separate and is exposed only to CoS in the Phase 1 agent catalogs. Passing verification requires explicit acceptance evidence.

## Security

Agent identity is process-bound. Tool arguments, prompt text, retrieved content, task content, delegated instructions, or shared-Skill output cannot select a different principal or widen the tool catalog. Tool payload sizes are bounded, errors are sanitized, and client-supplied code/import/shell execution is not supported.

## Development and certification

From `mcp/`:

```bash
npm ci
npm run check
```

`npm run check` performs strict TypeScript compilation, Node tests, a real local stdio smoke certification, and high-severity npm audit. The smoke certification proves exact CoS tool projection, the 10-agent roster, Message Operations registration, Devil's Advocate principal exclusion, human-only tool exclusion, local canonical persistence, and safe denial behavior.