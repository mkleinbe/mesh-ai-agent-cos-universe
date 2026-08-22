# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current release target: `v4.0.0 Chief of Staff Delegation Contract Remediation`.**

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**:

1. Chief of Staff
2. AgentOps Controller
3. Answer & Decision Desk
4. CRO
5. CFO
6. COO
7. Consultant Network Steward
8. CMO
9. VP Content
10. Message Operations

**Mesh Devil's Advocate is not an eleventh agent.** It is an external governed shared Skill, advisory only, available to Chief of Staff and CRO. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets are interaction, evidence, or mirror surfaces.

## Runtime topology

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

Every local MCP process is immutably bound to one registered identity through `MESH_COS_AGENT_ID`. All 10 agents in the same operating universe use the same approved `MESH_COS_LEDGER_PATH`. Prompt text, retrieved content, task content, delegated instructions, connectors, and shared-Skill output cannot alter identity or tool authority.

## Authority boundary

`approval.record_decision` and `reliability.human_override` exist in the MCP runtime but are **human-principal-only**. They are excluded from every agent catalog and dispatched only through the authenticated human path.

L4 requires qualified-human approval. L5 remains Michael-exclusive. Delegation preserves or narrows authority and inherited approvals, never widens or weakens them.

## Completion and verification

The canonical lifecycle separates work production from acceptance:

```text
... -> IN_PROGRESS -> QA -> COMPLETED -> VERIFIED -> CLOSED
```

`task.complete` is the accountable-owner completion operation. It requires a non-empty outcome and supporting evidence and moves eligible work to `COMPLETED` only.

`task.verify` is separate. In Phase 1 only Chief of Staff is expressly exposed that verifier operation. Passing verification requires acceptance evidence. **COMPLETED != VERIFIED.**

## Delegation model

Normal depth is CoS -> functional executive -> specialist. The governed path `Michael -> CoS -> COO -> Consultant Network Steward` is legal. Consultant Network Steward is terminal with max delegation depth 0, so any further delegation fails closed.

## Quality and release gates

The release path requires dependency integrity, TypeScript build and Node tests, local stdio MCP smoke certification, npm audit, schema validation, runtime/documentation drift validation, Workspace Agent package validation, Ruff, mypy, 100% branch-aware Python coverage, Bandit, compileall, synthetic end-to-end delegation certification, negative authority tests, and production preflight.

Historical release records remain historical. In particular, v3.0.0 documented the temporary 9-agent plus shared Message Operations architecture and must not be interpreted as current state.

See `docs/phase-1-operating-contract.md`, `docs/architecture.md`, `docs/production-readiness.md`, `docs/testing-evaluation.md`, and `RELEASE.md` for the current operational contract.