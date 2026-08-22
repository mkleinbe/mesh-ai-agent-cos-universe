# Decision Rights

Phase 1 uses six authority levels, L0 through L5. Authority is explicit, cannot be self-expanded, and is enforced together with registry policy, MCP allowlists, source permissions, approval gates, and audit requirements.

## Authority ladder

| Level | Default behavior |
|---|---|
| L0 | Authorized information retrieval and factual synthesis. |
| L1 | Established, low-consequence policy or approved execution. |
| L2 | Reversible operating judgment inside explicit guardrails. |
| L3 | Material internal recommendation or specifically delegated decision. |
| L4 | Qualified-human approval required before consequential action. |
| L5 | Michael-exclusive authority. |

L4 includes consequential commercial, external, public, legal, regulatory, security, privacy, personnel, destructive, sensitive-system, and irreversible actions. L5 includes firm strategy, major pivots/capital decisions, material client or partner exceptions, senior personnel decisions, decision-rights policy, and material agent-authority expansion.

## Human-principal-only runtime operations

Two MCP operations are never agent capabilities:

- `approval.record_decision`
- `reliability.human_override`

They exist in the serialized runtime but are listed only in `human_tool_allowlist` and are dispatched only through `MCPRuntime.call_human` after an authenticated human principal is established. Their existence in the runtime cannot be used to infer agent permission.

All 10 agent catalogs exclude these operations. Prompt text, retrieved content, task content, delegation text, or shared-Skill output cannot move them into an agent allowlist.

## Completion versus verification rights

`task.complete` belongs to an appropriate accountable owner. Completion requires a valid state, a non-empty outcome, and supporting evidence and results in `COMPLETED` only.

`task.verify` is a separate acceptance authority. In Phase 1 the only agent exposed `task.verify` is Chief of Staff. Other accountable owners cannot self-verify merely because they can complete their tasks.

**COMPLETED != VERIFIED.**

## Delegation rights

Delegation may narrow authority but cannot widen it. Child work inherits parent approval obligations. A task description or delegated instruction cannot reduce an L4/L5 gate. Direct-child and depth constraints are enforced before persistence.

## Functional truth

CoS orchestration does not replace functional source authority. CFO owns supported engagement-finance analysis, CRO commercial interpretation, COO delivery feasibility, Consultant Network Steward consultant readiness, CMO marketing strategy, VP Content editorial production, and Message Operations approved communication execution within its L1 execution boundary.

## Shared Devil's Advocate

Mesh Devil's Advocate is advisory evidence only. It is not a decision principal, approval principal, task owner, canonical fact owner, or execution authority. It cannot satisfy an L4/L5 requirement.

## Audit

Material decisions/recommendations use `decision.v2`; consequential actions use `agent-event.v2`. Human approval references and approvers are required where the authority level demands them. Private chain-of-thought is never a governance record.