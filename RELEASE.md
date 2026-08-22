# v3.0.0 Shared Mesh Message Operations

`v3.0.0` is a breaking workforce-topology release for the Mesh AI Chief of Staff universe. It removes the repository-local Message Operations agent and duplicate role Skill, then uses the already-built external **Mesh Message Operations** Skill as a governed shared execution capability.

## Breaking change

The canonical Phase 1 organization changes from 10 registered agent principals to **9 agents plus two shared capabilities**: Mesh Devil's Advocate and Mesh Message Operations. Consumers that assumed a `message-ops` agent ID, Workspace Agent manifest, role card, MCP principal, or repository-local `chatgpt/skills/mesh-message-operations/` package must migrate to the shared-capability model.

The shared `mesh-message-operations` Skill is attached only to Chief of Staff, CRO, and CMO. It is invoked through `skills.invoke_governed`, not through agent delegation. VP Content remains drafting/editorial-production only and does not receive execution authority.

## Shared Message Operations contract

- Display name: **Mesh Message Operations**
- Deployment: `EXTERNAL_SHARED_SKILL`
- Consumers: `cos`, `cro`, `cmo`
- Authority: `APPROVAL_BOUND_EXECUTION_ONLY`
- Request contract: `mesh.messaging.execution-request.v1`
- Response contract: `mesh.messaging.execution-receipt.v1`
- Creates strategy or copy: `false`
- Approval may be inferred or broadened: `false`
- Preview is approval: `false`
- Canonical commercial state modified: `false`
- Canonical consent or legal state modified: `false`
- Per-message approval required: `true`
- Documented connector action required: `true`
- Idempotency required: `true`
- Post-send observed-state verification required: `true`

The capability executes only an exact individually approved communication. It requires batch preview, per-message preflight, explicit approval bound to message ID/payload hash, sender, recipient, channel, operation and execution window, consent/suppression/jurisdiction/frequency/thread checks, cancellation and kill-switch checks immediately before execution, a unique idempotency key, an authorized documented connector action, per-attempt receipts, and observed provider-state verification after execution. Material payload or control-state changes invalidate approval and return the message to preflight.

The capability does not create campaign strategy, pursuit strategy, message copy, legal conclusions, consent decisions, canonical account state, or lifecycle state. It does not turn preview, silence, an old approval, or connector capability into authorization. It cannot use undocumented mutating endpoints or claim a send succeeded when provider state cannot be verified.

## Existing shared Devil's Advocate contract

The v2.0.0 Mesh Devil's Advocate refactor remains intact. `mesh-devils-advocate` is still an external shared Skill available only to Chief of Staff and CRO, advisory-only, unable to mutate canonical facts or execute external actions, and unable to become the decision owner.

For Revenue Intelligence work, canonical account IDs, evidence classes, scores, stage, lifecycle, queue state, activation readiness, and prioritization remain authoritative. Neither shared Skill may overwrite those facts.

## What changed

- Removed `message-ops` from the canonical Agent Registry and production preflight roster.
- Removed the Message Operations role card, Workspace Agent manifest, repository-local Skill package, and MCP agent principal.
- Added `mesh-message-operations` to the versioned `shared_capabilities` registry contract.
- Added the shared execution entitlement only to Chief of Staff, CRO, and CMO.
- Preserved VP Content as drafting/editorial-production only, with no shared execution entitlement.
- Moved approved Gmail/Slack execution access to the entitled CoS/CRO/CMO Workspace manifests using `WRITE_WITH_APPROVAL`, while preserving **Always ask** and exact Message Operations Connector Action Constraints.
- Preserved LinkedIn as non-publishing, AuthoredUp as draft/analytics only, and Apollo as research/enrichment only. This release does not create autonomous public publishing or outbound sequencing.
- Updated the Workspace projection to exactly 9 registered agents and removed the Message Operations MCP principal.
- Preserved the bundled `LOCAL_STDIO` MCP path and `MCPRuntime` as the sole business/governance execution core.
- Updated MCP stdio certification, package/runtime drift validation, preflight, tests, Builder handoff, role/workflow documentation, release documentation, and Mermaid architecture for the shared capability model.
- Preserved human-only approval/reliability operations, L4/L5 gates, completion-versus-verification separation, canonical audit/decision records, deny-by-default tool projection, and TaskLedger canonical state.

## TDD and loop engineering

The change began with a test-only acceptance commit that intentionally failed against the 10-agent model. Subsequent loops remove the embedded principal, reconcile the registry and Workspace projection, update the MCP surface, preserve execution safety controls from the already-built Mesh Message Operations Skill, and drive every release gate back to green without weakening coverage or authority requirements.

The acceptance contract proves that:

- no `message-ops` agent principal remains;
- the repository contains exactly 9 Workspace Agent manifests;
- no duplicate repository-local Mesh Message Operations Skill remains;
- only CoS, CRO, and CMO receive the shared execution entitlement;
- VP Content remains drafting-only;
- Message Operations cannot create strategy/copy, infer or broaden approval, treat preview as approval, or mutate canonical commercial/consent/legal state;
- Message Operations requires exact per-message approval, documented connector execution, idempotency, kill-switch/cancellation checks, per-attempt receipts, and post-send verification;
- the MCP has no Message Operations agent allowlist while the authorized consumers retain governed Skill invocation;
- the existing shared Devil's Advocate architecture remains intact;
- the release identity is `3.0.0` / `v3.0.0`.

## Release quality gates

Release acceptance requires all of the following to pass on the final PR head and merged `main`:

- Python dependency integrity;
- `npm ci` for the MCP package;
- strict TypeScript compilation;
- Node MCP unit tests;
- real local stdio MCP smoke certification using the 9-agent roster;
- npm audit at high severity;
- all contract fixtures;
- runtime/documentation drift validation;
- Workspace Agent package/shared-Skill drift validation;
- strict source Ruff plus critical test/script lint;
- mypy;
- **100% branch-aware `mesh_cos` coverage**;
- Bandit high-severity scan;
- compileall.

No release gate may be relaxed as part of this change.

## Production activation boundary

The repository does not fabricate target-Workspace app authentication, Gmail/Slack credentials, the dedicated Answer Desk Slack channel, approved source credentials, shared Skill availability/permissions, production approval-owner mappings, jurisdiction/consent determinations, Google Sheets write credentials, secrets management, or Workspace publication/RBAC configuration. Those remain target-environment dependencies and must pass private-preview testing before activation.

A separately deployed remote MCP service remains optional. ChatGPT-local operation continues through `LOCAL_STDIO` using `node mcp/dist/index.js` and the canonical `mesh_cos.mcp_runtime.MCPRuntime` control plane.

## Release identity

- Semantic version: `3.0.0`
- Semantic Tag: `v3.0.0`
- Release title: `v3.0.0 Shared Mesh Message Operations`
- Canonical workforce: 9 agent principals
- Shared challenge capability: `mesh-devils-advocate`
- Shared execution capability: `mesh-message-operations`
- Shared execution consumers: Chief of Staff, CRO, CMO
- ChatGPT MCP transport: `LOCAL_STDIO`
- Local entry point: `node mcp/dist/index.js`
- Canonical runtime: `mesh_cos.mcp_runtime.MCPRuntime`
- Canonical state: `TaskLedger`

See `docs/release-3.0.0-shared-message-operations.md` for the detailed release record.
