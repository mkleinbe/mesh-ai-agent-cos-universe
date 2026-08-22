# Mesh CoS MCP

This package is the bundled Model Context Protocol transport for the Mesh AI Chief of Staff operating core. Current repository release: **`v3.0.0 Shared Mesh Message Operations`**.

## Runtime model

`mesh-cos-mcp` follows the same primary runtime pattern as Mesh Revenue Intelligence: ChatGPT launches a local stdio MCP process from the checked-in package. A separately managed remote transport is optional and is not required for Workspace Agent operation.

The TypeScript MCP layer is intentionally thin. It does not duplicate task, authority, governance, approval, reliability, AgentOps, or shared-Skill business logic. Every allowed tool call is bridged to `mesh_cos.mcp_stdio_bridge`, which creates the canonical Python `MCPRuntime` against the configured `TaskLedger` SQLite file.

```text
ChatGPT Workspace Agent
        |
        | LOCAL_STDIO
        v
node mcp/dist/index.js
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
- `MESH_COS_LEDGER_PATH`: path to the shared canonical SQLite TaskLedger. All **9 registered agents** must use the same approved path for one operating universe.
- `MESH_COS_KILL_SWITCH`: optional emergency stop. Truthy values fail closed.
- `MESH_COS_PYTHON_BIN`: optional Python executable override. Defaults to `python`.

No `MESH_COS_MCP_SERVER_URL` is required for the ChatGPT runtime.

## Shared capability boundaries

The former `devils-advocate` and `message-ops` agent IDs are not valid MCP principals in `v3.0.0`.

**Mesh Devil's Advocate** is an external shared Skill available only to Chief of Staff and CRO. Those two principals may reach it through `skills.invoke_governed` under their existing identities. The shared capability has no independent MCP identity, task ownership, canonical-state authority, approval authority, or external-action authority.

**Mesh Message Operations** is an external shared Skill available only to Chief of Staff, CRO, and CMO. It is approval-bound execution only. VP Content remains drafting/editorial-production only and receives no execution entitlement. The Skill cannot create strategy/copy, select recipients, set pricing, make commitments, establish consent/legal conclusions, or define publishing policy.

Message execution requires explicit current approval bound to the exact payload hash/version, sender, immutable audience, channel, purpose, jurisdiction, consent basis, suppressions/frequency controls, test result, approvers, and execution window. Material changes invalidate approval. Preflight, cancellation/kill-switch checks, documented connector actions, idempotency, per-attempt receipts, and observed provider-state verification remain mandatory. Requested, scheduled, sent, delivered, and replied are distinct states.

For commercial work, Mesh Revenue Intelligence remains authoritative for account identity, evidence classes, scores, stage, lifecycle, queue state, activation readiness, and prioritization. Neither shared Skill may overwrite canonical facts.

## Security and governance

The local server loads `chatgpt/mcp/mesh-cos-mcp.v1.json`, projects only the tool allowlist for the bound agent, and never exposes human-only `approval.record_decision` or `reliability.human_override` to an agent stdio process. The Python runtime independently re-authorizes the agent and tool. This gives two fail-closed enforcement layers.

Client-supplied code, import paths, callables, shell commands, and replay functions are not executable inputs. Tool arguments and bridge responses are size bounded. Errors returned to the MCP client use safe categories and do not echo raw payloads.

`TaskLedger` remains canonical. ChatGPT conversation state, Slack, connector output, shared-Skill packets/receipts, and governance Sheets are interaction or mirror surfaces.

## Development and certification

From `mcp/`:

```bash
npm ci
npm run check
```

`npm run check` performs strict TypeScript compilation, Node unit tests, a real MCP stdio smoke certification using the official MCP client and transport, and the npm security audit. The smoke test proves exact CoS tool projection, the **9-agent roster**, local canonical persistence across calls, human-only tool exclusion, shared-capability principal exclusion, and safe denial behavior.

The repository CI runs this MCP gate in addition to the Python release gates, including 100% branch-aware `mesh_cos` coverage.
