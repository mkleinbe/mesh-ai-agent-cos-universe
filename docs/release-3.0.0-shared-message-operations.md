# v3.0.0 Shared Mesh Message Operations

**Status:** breaking semantic release candidate  
**Semantic Tag:** `v3.0.0`  
**Release title:** `v3.0.0 Shared Mesh Message Operations`

## Breaking topology change

Release `v3.0.0` removes the repository-local `message-ops` agent principal and duplicate local `mesh-message-operations` role Skill. The Phase 1 workforce becomes **9 registered agents plus two governed shared Skills**:

- **Mesh Devil's Advocate** remains an external advisory shared Skill available only to Chief of Staff and CRO.
- **Mesh Message Operations** becomes an external approval-bound execution shared Skill available only to Chief of Staff, CRO, and CMO.

Message Operations is not a Workspace Agent, MCP principal, delegated worker, decision owner, or canonical source. VP Content remains drafting/editorial-production only and cannot invoke external message execution.

## Shared Mesh Message Operations contract

The external Skill preserves the already-built execution workflow rather than reimplementing messaging inside the CoS repository. It owns batch preview, per-message preflight, exact approval binding, cancellation and kill-switch checks, idempotency, documented connector execution, per-attempt receipts, and observed-state verification.

It does not create strategy or copy. It cannot infer, broaden, reuse, or manufacture approval. Preview is not approval. It cannot modify canonical commercial, account, lifecycle, consent, legal, or jurisdiction state. An approved message may execute only while its exact payload hash, sender, recipient, channel, operation, execution window, consent/suppression/jurisdiction/frequency/thread state, approval, kill-switch state, and cancellation state remain valid.

Every material change invalidates prior approval and returns the message to preflight. Every attempted message receives a separate receipt. A provider response is not treated as confirmed success until observed provider state is re-read. Unknown or unverifiable state remains unknown or blocked.

## Consumer boundaries

### Chief of Staff

May invoke Mesh Message Operations for an exact approved communication after orchestration, content preparation, and required human approval are complete. It does not gain a general external-send permission.

### CRO

May invoke Mesh Message Operations for exact approved commercial communications. Revenue Intelligence remains authoritative for canonical account identity, evidence, scores, stage, lifecycle, queue state, activation readiness, and prioritization. Message execution cannot rewrite those facts.

### CMO

May invoke Mesh Message Operations for exact approved marketing communications where a documented supported connector action exists. LinkedIn remains non-publishing and AuthoredUp remains draft/analytics only. This release does not grant autonomous public publishing.

### VP Content

Remains a production specialist. It may create message-ready or publication-ready content, but it has no shared Message Operations entitlement and no external execution authority.

## MCP and canonical state

The runtime remains `Workspace Agent -> LOCAL_STDIO -> node mcp/dist/index.js -> mesh_cos.mcp_stdio_bridge -> MCPRuntime -> TaskLedger`.

`message-ops` is removed from MCP agent allowlists. CoS, CRO, and CMO retain `skills.invoke_governed` for their explicitly entitled shared Skill calls. Human-only `approval.record_decision` and `reliability.human_override` remain outside every agent allowlist.

`TaskLedger` remains canonical. Message previews, approval packets, connector responses, execution receipts, ChatGPT transcripts, Slack, and governance Sheets are evidence or interaction surfaces, not alternate canonical state.

## TDD and loop engineering

The refactor begins with a failing acceptance suite against the prior 10-agent topology. The implementation then reconciles the registry, role cards, Workspace Agent manifests, shared Skill entitlements, MCP principals and allowlists, production preflight, local stdio certification, package/runtime versions, tests, documentation, Mermaid architecture, release metadata, and Builder handoff.

The release cannot merge until the final PR head passes the full repository release suite without weakening any gate.

## Release quality gates

The final PR head and merged `main` must pass:

- Python dependency integrity
- `npm ci`
- strict TypeScript compilation
- Node MCP unit tests
- real local stdio MCP smoke certification against the **9-agent** roster
- npm audit at high severity
- contract/schema validation
- runtime/documentation drift validation
- ChatGPT Workspace Agent package/shared-Skill drift validation
- strict source Ruff
- critical Ruff checks for tests/scripts
- mypy
- **100% branch-aware `mesh_cos` coverage**
- Bandit high-severity scan
- compileall

## Production activation boundary

Repository release does not fabricate Workspace authentication, Gmail/Slack credentials, Answer Desk channel configuration, shared Skill availability, connector capabilities, source permissions, approval-owner mappings, consent/jurisdiction decisions, secrets management, or RBAC/publication state. Those remain target-environment dependencies and must pass private preview and production preflight.

## Migration summary

Consumers must stop treating `message-ops` as an agent ID. Invoke `mesh-message-operations` only through the governed shared-Skill boundary from CoS, CRO, or CMO. Do not delegate tasks to it, create an MCP principal for it, or install the deleted duplicate local role Skill. Preserve exact-message human approval and all existing preflight/receipt/verification controls.
