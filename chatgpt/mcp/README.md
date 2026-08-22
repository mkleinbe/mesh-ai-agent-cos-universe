# Mesh CoS MCP Contract

`mesh-cos-mcp.v1.json` is the protocol-facing contract for release `3.0.0`. ChatGPT uses the bundled MCP package over `LOCAL_STDIO`.

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

```text
MESH_COS_AGENT_ID=<registered agent id>
MESH_COS_LEDGER_PATH=.mesh-cos/task-ledger.sqlite3
MESH_COS_PYTHON_BIN=python
```

`MESH_COS_AGENT_ID` is validated against the checked-in **9 agent** allowlists. `devils-advocate` and `message-ops` are not valid MCP principals. The tool catalog exposed by the server is the exact deny-by-default allowlist for the bound agent, excluding human-only tools.

## Shared capability boundary

**Mesh Devil's Advocate** is an external shared Skill, not an MCP agent principal. Only Chief of Staff and CRO may invoke it through `skills.invoke_governed`. It is advisory only and cannot modify canonical facts or execute external actions.

**Mesh Message Operations** is an external shared Skill, not an MCP agent principal. Only Chief of Staff, CRO, and CMO may invoke it through `skills.invoke_governed`. VP Content has no entitlement. It is approval-bound execution only and cannot create strategy/copy, select recipients, set pricing, make commitments, determine consent/legal status, or define publishing policy.

Entitlement to `skills.invoke_governed` is necessary but never sufficient for message execution. Message Operations must validate explicit current approval bound to the exact payload hash/version, sender, immutable audience, channel, purpose, jurisdiction, consent basis, exclusions/frequency controls, test result, approvers, and execution window. Material changes invalidate approval. Execution must preserve preflight, kill-switch/cancellation checks, documented connector actions, idempotency, per-attempt receipts, and observed provider-state verification.

## Enforcement order

1. Start the checked-in MCP package with a registered local agent identity.
2. Publish only the bound agent's allowed MCP tools.
3. Validate tool arguments as bounded JSON objects.
4. Bridge the request to `mesh_cos.mcp_stdio_bridge`.
5. Enter `MCPRuntime`, never a generic dynamic execution path.
6. Recheck the per-agent allowlist and canonical registry.
7. Apply source, tool, action, L0-L5 authority, approval, and reliability controls.
8. Permit governed shared-Skill invocation only where registry entitlement and MCP policy both authorize it.
9. Invoke only fixed server-side handlers and registered replay executors.
10. Persist canonical state in `TaskLedger` before non-canonical responses or mirrors.
11. Emit required `decision.v2` and `agent-event.v2` governance records.

## Human-only operations

`approval.record_decision` and `reliability.human_override` are **human-only**. They are excluded from every agent tool catalog and require a separate authenticated human-principal path.

## Error, replay, and verification safety

The local TypeScript MCP does not expose raw bridge stderr or arbitrary exception text to ChatGPT. Request and response sizes are bounded.

`reliability.replay` may execute only a server-registered executor referenced by canonical failure state. Client-supplied Python, import paths, shell commands, code snippets, or source-text instructions are never executable replay behavior.

`task.complete` persists accountable-owner outcome and evidence. `task.verify` remains separate. `COMPLETED` does not imply `VERIFIED`. A successful message connector attempt does not prove delivery or reply without observed provider evidence.

## Certification

```bash
cd mcp
npm ci
npm run check
```

`npm run check` compiles TypeScript, runs Node tests, launches a real stdio MCP smoke path, verifies exact tool projection and human-only exclusion, verifies the 9-agent roster and shared-capability principal exclusion, writes/rereads canonical task state across calls, checks safe denial behavior, and runs `npm audit --audit-level=high`.

## Deployment boundary

A remote MCP endpoint is optional and not required for ChatGPT-local operation. Any future managed transport must preserve the same `MCPRuntime`, registry, exact allowlists, authority, approval, audit, shared-Skill boundaries, and canonical-state semantics.
