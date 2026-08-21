# v2.0.0 Shared Mesh Devil's Advocate

`v2.0.0` is a breaking workforce-topology release for the Mesh AI Chief of Staff universe. It removes the repository-local Devil's Advocate agent and duplicate role Skill, then replaces that capability with the more robust shared **Mesh Devil's Advocate** Skill.

## Breaking change

The canonical Phase 1 organization changes from 11 registered agent principals to **10 agents plus one shared challenge capability**. Consumers that assumed a `devils-advocate` agent ID, Workspace Agent manifest, role card, MCP principal, or repository-local `chatgpt/skills/mesh-devils-advocate/` package must migrate to the shared capability model.

The shared `mesh-devils-advocate` Skill is attached only to Chief of Staff and CRO. It is invoked through `skills.invoke_governed`, not through agent delegation.

## Shared challenge contract

- Display name: **Mesh Devil's Advocate**
- Deployment: `EXTERNAL_SHARED_SKILL`
- Consumers: `cos`, `cro`
- Authority: `ADVISORY_ONLY`
- Request contract: `mesh.devils-advocate.challenge-request.v1`
- Response contract: `mesh.devils-advocate.challenge-packet.v1`
- Canonical facts modified: `false`
- External action included: `false`

The capability may steelman a proposal, construct countercases, test assumptions, run premortems/red-team analysis, audit evidence sufficiency, and challenge decision conditions. It does not become the decision owner and returns authority to the owning agent or qualified human.

For Revenue Intelligence work, canonical account IDs, evidence classes, scores, stage, lifecycle, queue state, and activation readiness remain authoritative. Mesh Devil's Advocate may challenge interpretation, route, assumptions, capacity, evidence sufficiency, and decision logic without overwriting those facts.

## What changed

- Removed `devils-advocate` from the canonical Agent Registry and production preflight roster.
- Removed the Devil's Advocate role card, Workspace Agent manifest, repository-local Skill package, and MCP agent principal.
- Added a versioned `shared_capabilities` contract to `agents/registry.json`.
- Added `mesh-devils-advocate` entitlement to Chief of Staff and CRO only.
- Preserved `request_devils_advocate_review` as a CRO capability, now implemented through the shared Skill boundary.
- Updated the 10 Workspace Agent manifests to release `2.0.0`; CoS/CRO explicitly attach the shared Skill.
- Preserved the bundled `LOCAL_STDIO` MCP path and `MCPRuntime` as the sole business/governance execution core.
- Updated production preflight, MCP smoke certification, package drift validation, runtime/documentation drift validation, and acceptance tests for the 10-agent model.
- Updated README, architecture, agent registry, governance, security, testing, runbook, Builder handoff, role documentation, historical-current-state notes, release documentation, and Mermaid architecture.
- Preserved human-only approval/reliability operations, L4/L5 gates, completion-versus-verification separation, canonical audit/decision records, and deny-by-default tool projection.

## TDD and loop engineering

The change began with a test-only acceptance commit that intentionally failed against the 11-agent model. Subsequent loops exposed and corrected stale assumptions in the MCP release contract, stdio smoke certification, preflight roster, package-lock metadata, Workspace Agent manifests, package/documentation drift gates, and current documentation. Release gates were not weakened to make the refactor pass.

The acceptance contract proves that:

- no `devils-advocate` agent principal remains;
- the repository contains exactly 10 Workspace Agent manifests;
- no duplicate repository-local Mesh Devil's Advocate Skill remains;
- only CoS and CRO receive the shared challenge entitlement;
- challenge authority is advisory and cannot mutate canonical facts or external actions;
- the MCP has no Devil's Advocate agent allowlist while CoS/CRO retain governed Skill invocation;
- the release identity is `2.0.0` / `v2.0.0`.

## Release quality gates

Release acceptance requires all of the following to pass on the final PR head and merged `main`:

- Python dependency integrity;
- `npm ci` for the MCP package;
- strict TypeScript compilation;
- Node MCP unit tests;
- real local stdio MCP smoke certification using the 10-agent roster;
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

The repository does not fabricate target-Workspace app authentication, Slack credentials, the dedicated Answer Desk Slack channel, approved source credentials, shared Skill availability/permissions, production approval-owner mappings, Google Sheets write credentials, secrets management, or Workspace publication/RBAC configuration. Those remain target-environment dependencies and must pass private-preview testing before activation.

A separately deployed remote MCP service remains optional. ChatGPT-local operation continues through `LOCAL_STDIO` using `node mcp/dist/index.js` and the canonical `mesh_cos.mcp_runtime.MCPRuntime` control plane.

## Release identity

- Semantic version: `2.0.0`
- Semantic Tag: `v2.0.0`
- Release title: `v2.0.0 Shared Mesh Devil's Advocate`
- Canonical workforce: 10 agent principals
- Shared challenge capability: `mesh-devils-advocate`
- ChatGPT MCP transport: `LOCAL_STDIO`
- Local entry point: `node mcp/dist/index.js`
- Canonical runtime: `mesh_cos.mcp_runtime.MCPRuntime`
- Canonical state: `TaskLedger`

See `docs/release-2.0.0-shared-devils-advocate.md` for the detailed release record.
