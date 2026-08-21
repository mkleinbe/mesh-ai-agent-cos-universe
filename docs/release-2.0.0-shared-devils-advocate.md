# v2.0.0 Shared Mesh Devil's Advocate

## Executive summary

Release `v2.0.0` is a **Breaking** change to the Mesh AI Chief of Staff workforce topology. The prior repository-local Devil's Advocate agent has been removed. Independent challenge is now supplied by the installed **Mesh Devil's Advocate** shared Skill, which is more capable and is governed as an advisory capability rather than a separate agent principal.

The resulting Phase 1 operating model contains **10 registered agents plus the shared challenge capability**.

## Why the refactor was required

The former design represented independent challenge as both an agent identity and a local role Skill. That duplicated a capability now provided more robustly by the shared Mesh Devil's Advocate Skill and unnecessarily created a separate principal, Workspace Agent, MCP allowlist, role card, and deployment surface.

The v2 design separates role accountability from reusable challenge capability:

- accountable work remains with the 10 registered agents;
- Chief of Staff and CRO may invoke the shared Mesh Devil's Advocate through `skills.invoke_governed`;
- the challenge result is advisory evidence, not canonical state or a new decision owner;
- functional truth and human decision rights remain unchanged.

## Canonical shared capability contract

`agents/registry.json` declares:

- capability: `mesh-devils-advocate`;
- display name: Mesh Devil's Advocate;
- type: shared Skill;
- deployment: `EXTERNAL_SHARED_SKILL`;
- consumers: `cos`, `cro`;
- authority: `ADVISORY_ONLY`;
- request contract: `mesh.devils-advocate.challenge-request.v1`;
- response contract: `mesh.devils-advocate.challenge-packet.v1`;
- canonical facts modified: false;
- external action included: false.

The challenge capability can test assumptions, steelman opposing positions, construct countercases, run premortems, red-team decisions, audit evidence, and identify decision conditions. It cannot become accountable owner, change canonical facts, bypass approvals, make commitments, or execute external actions.

## Revenue Intelligence boundary

When CRO invokes Mesh Devil's Advocate for commercial work, Revenue Intelligence remains authoritative for canonical account IDs, evidence classes, scores, stage, lifecycle, queue state, and activation readiness. The shared Skill may challenge interpretation, route, assumptions, capacity, evidence sufficiency, and decision logic only.

## Runtime and deployment changes

Removed:

- `agents/devils-advocate.md`;
- `chatgpt/workspace-agents/devils-advocate.json`;
- repository-local `chatgpt/skills/mesh-devils-advocate/`;
- `devils-advocate` from the MCP agent allowlist map;
- `devils-advocate` from the canonical production preflight roster.

Added or changed:

- registry `shared_capabilities` contract;
- CoS and CRO shared Skill entitlement;
- CoS/CRO Workspace Agent `shared_skills` configuration;
- governed challenge workflow language and quality checks;
- 10-agent MCP smoke certification;
- 10-agent production preflight;
- shared-capability drift enforcement;
- v2 Builder handoff and production-readiness documentation.

The execution path remains `ChatGPT Workspace Agent -> LOCAL_STDIO mesh-cos-mcp -> mesh_cos.mcp_stdio_bridge -> MCPRuntime -> TaskLedger`.

## TDD and loop engineering record

The refactor started with `tests/evaluations/test_shared_devils_advocate_integration.py` before implementation. The initial tests were intentionally red against the 11-agent architecture.

Engineering loops then exposed stale assumptions and defects in sequence, including:

1. package/runtime release expectations still set to 1.1.0;
2. stdio smoke certification still requiring 11 agents;
3. preflight and runtime/documentation drift still requiring a Devil's Advocate principal;
4. MCP package-lock metadata not yet aligned to the new semantic release;
5. Workspace Agent manifests still projecting 1.1.0 and the old roster;
6. ChatGPT package drift validation still requiring a local Devil's Advocate Skill and manifest;
7. current and historical documentation lacking an explicit v2 current-state boundary.

Each loop fixed the underlying defect and re-ran CI. No quality, security, authority, or coverage gate was relaxed.

## Governance preservation

- `TaskLedger` remains canonical state.
- `MCPRuntime` remains the sole serialized business/governance execution core.
- L4 continues to require qualified human approval.
- L5 remains Michael-exclusive.
- `approval.record_decision` and `reliability.human_override` remain human-only.
- `task.complete` remains distinct from `task.verify`.
- `decision.v2` and `agent-event.v2` remain required governance records.
- Shared challenge output does not expand source, tool, or decision authority.

## Mermaid architecture

The current architecture diagrams in `README.md` and `docs/architecture.md` show 10 agent principals with dotted governed challenge paths from Chief of Staff and CRO to the shared Mesh Devil's Advocate Skill. The corresponding Mermaid Chart has also been rendered and validated for the v2 topology.

## Release acceptance

The final release requires the full CI suite to remain green: dependency integrity, MCP npm install/build/tests/smoke/security, contract validation, runtime/documentation drift, ChatGPT package drift, Ruff, mypy, 100% branch-aware `mesh_cos` coverage, Bandit high-severity scan, and compileall.

## Production activation boundary

Repository release readiness does not itself configure external Workspace credentials, Slack secrets/channel IDs, approved source credentials, the external shared Skill's target-workspace permission, approval-owner mappings, secrets management, or Workspace RBAC/publication. Those remain environment activation tasks and must be verified in private preview.

## Semantic Tag

This release is versioned `2.0.0` and published under **Semantic Tag `v2.0.0`**. The GitHub release workflow creates `v2.0.0 Shared Mesh Devil's Advocate` from `RELEASE.md` after the release change is merged to `main`.
