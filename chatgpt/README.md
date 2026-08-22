# ChatGPT Workspace Agent Packages

Current repository release target: **`4.0.0`**.

This directory projects the canonical Mesh CoS organization into ChatGPT Workspace Agent deployment packages. It does not replace the Python control plane and does not move canonical state into ChatGPT.

## Contents

- `skills/`: exactly 10 validated repository-local role Skills.
- `workspace-agents/`: exactly 10 Workspace Agent manifests aligned to repository release `4.0.0`.
- `mcp/mesh-cos-mcp.v1.json`: local stdio MCP contract with per-agent allowlists and a separate human-only allowlist.
- `workspace-agent-builder-prompt.md`: deployment handoff for the canonical 10-agent organization.

The 10 agents are Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

Mesh Devil's Advocate is external to the Workspace Agent roster. It is a governed shared Skill attached only to CoS and CRO and remains advisory-only.

## Runtime path

```text
Workspace Agent
  -> MESH_COS_AGENT_ID
  -> LOCAL_STDIO
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> MCPRuntime
  -> TaskLedger
```

All 10 agents in one operating universe share the same approved `MESH_COS_LEDGER_PATH` while retaining distinct immutable identities.

## Authority and lifecycle

No agent catalog may expose `approval.record_decision` or `reliability.human_override`. Those operations are available only through the authenticated human-principal path.

Appropriate accountable owners use `task.complete` with outcome and evidence. Completion produces `COMPLETED`, not `VERIFIED`. `task.verify` is separate and, in the Phase 1 agent projection, is exposed only to Chief of Staff.

## Packaging rules

Role Skill MCP allowlists, manifest MCP allowlists, Builder allowlists, registry principals, and the canonical MCP contract must match exactly. CI treats drift as a release defect.

Workspace agents remain Private until authority-negative tests, identity-spoofing tests, lifecycle tests, delegation-depth tests, shared-Skill tests, local MCP certification, and production preflight pass.