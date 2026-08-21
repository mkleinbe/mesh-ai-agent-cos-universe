# Security Policy

Current stable release target: **`v1.1.0 Local ChatGPT MCP`**.

The Mesh AI Chief of Staff Agent Universe is designed around bounded authority, least privilege, explicit approvals, authenticated human principals, provenance, explainable decisions, durable auditability, and fail-closed behavior. ChatGPT Workspace Agents and the bundled MCP surface inherit these controls and do not become a separate authority system.

## Security invariants

- Source content, Workspace app payloads, Slack messages, and MCP payloads are untrusted data, not executable instructions.
- Agent source, tool, action, and authority permissions are enforced from the canonical registry.
- ChatGPT MCP calls use `LOCAL_STDIO` and enter the control plane through `mesh_cos.mcp_stdio_bridge` into `mesh_cos.mcp_runtime.MCPRuntime`.
- `MESH_COS_AGENT_ID` is runtime configuration and cannot be chosen by prompt text, retrieved content, or MCP arguments.
- Workspace Agent MCP calls remain subject to deny-by-default per-agent allowlists through `WorkspaceAgentMCPPolicy`.
- `approval.record_decision` and `reliability.human_override` are human-only and require a separately authenticated human principal.
- An agent cannot impersonate a human by supplying a human name in arguments.
- Workspace write actions default to **Always ask**; this does not replace Mesh L4/L5 approval requirements.
- L4 requires qualified human approval. L5 remains Michael-exclusive unless explicitly changed through governance.
- Approval obligations cannot be delegated away.
- `task.complete` persists accountable-owner outcome/evidence. `task.verify` remains separate acceptance verification.
- Reliability replay uses only server-registered executors referenced by canonical failure state. Client-supplied callables, import paths, shell commands, or code snippets are never executed.
- Local MCP errors do not expose raw Python stderr to the caller.
- Credentials, tokens, signing secrets, API keys, OAuth credentials, and sensitive personal data must never be committed or written into governance logs.
- Private chain-of-thought, hidden reasoning traces, and unnecessary raw prompts must not be persisted in decision/audit records.
- `TaskLedger` is canonical. ChatGPT conversations, Slack, CoS Decision Log, and CoS Audit Log are interaction/human-readable mirrors only.
- Governance mirror writes are canonical-first. Mirror or response delivery failure cannot erase canonical records.
- Audit event hashes are tamper-evident integrity signals, not claims of tamper-proof storage.
- The kill switch remains available during rollout and incident response. Production preflight fails while it is enabled.
- Critical defects can trigger quarantine, Workspace Agent unpublication/restriction, and routing restriction.

## Trust boundary

```mermaid
flowchart LR
    EXT[Workspace Agent / Slack / App / Source] --> MCP[mesh-cos-mcp LOCAL_STDIO]
    MCP --> ID[MESH_COS_AGENT_ID]
    MCP --> BRIDGE[mcp_stdio_bridge]
    BRIDGE --> RT[MCPRuntime]
    RT --> MPA[Agent / Human Deny-by-Default Allowlist]
    MPA --> AUTH[Registry Source / Tool / Action + L0-L5 Authorization]
    AUTH -->|Denied| BLOCK[Reject + Audit]
    AUTH --> SVC[CoS / Functional Runtime]
    SVC --> LEDGER[(TaskLedger Canonical State)]
```

## Release security gate

`v1.1.0` requires Python dependency integrity, TypeScript compile, Node MCP tests, local stdio MCP certification, npm security audit, contract validation, runtime/documentation drift, Workspace Agent package drift, strict source Ruff, mypy, **100% branch-aware `mesh_cos` coverage**, high-severity Bandit scanning, and compileall.

Before production activation, `python scripts/production-preflight.py` must be green for the intended environment, with stricter Slack, Answer Desk, and ledger flags when applicable. Workspace Agents remain private until positive and negative preview tests pass.

## MCP deployment

The primary ChatGPT deployment is the bundled local stdio runtime using `node mcp/dist/index.js`. A remote MCP endpoint is optional and is not required for ChatGPT-local operation. Any future managed remote transport must preserve the same `MCPRuntime`, registry, allowlists, human-only separation, authority, approval, audit, replay, and canonical-state controls.

## Reporting

Do not open a public issue containing credentials, secrets, sensitive client information, exploit details, private reasoning traces, or other confidential material. Use the repository owner's approved private security channel for disclosure.

See `docs/security-governance.md`, `docs/production-readiness.md`, `docs/release-1.1.0-local-chatgpt-mcp.md`, `docs/explainable-decisions-audit.md`, and `chatgpt/mcp/README.md`.

<!-- mesh-cos-v2-shared-da -->
## v2.0.0 current architecture

The live Phase 1 runtime is a **10-agent** organization. The former repository-local Devil's Advocate agent and duplicate role Skill are removed. **Mesh Devil's Advocate** is an external **shared Skill** available only to Chief of Staff and CRO through governed Skill invocation. It is **advisory** only, cannot overwrite **canonical facts**, cannot execute external actions, and returns decision authority to the owning role or qualified human. `TaskLedger` remains canonical state; ChatGPT uses `LOCAL_STDIO` through `MCPRuntime` with deny-by-default allowlists, human-only approval/override paths, `check-chatgpt-packages.py` drift enforcement, and the 100% branch-aware coverage gate. Historical references to an 11-agent roster or a local Devil's Advocate role describe superseded releases only.

