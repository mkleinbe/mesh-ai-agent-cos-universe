# Decision Rights

Phase 1 uses six authority levels, L0 through L5. Authority is explicit, cannot be self-expanded, and is enforced together with registry source/tool/action policy, approval requirements, explainable-decision logging, Workspace Agent connector controls, and shared-Skill boundaries.

## Authority ladder

| Level | Default behavior | Decision logging |
|---|---|---|
| **L0** | Retrieve/synthesize authorized facts. | Audit consequential access/action. |
| **L1** | Execute established approved policy. | Audit required; decision record when interpretation is material. |
| **L2** | Make reversible internal judgments inside explicit guardrails. | `decision.v2` for material choices/recommendations. |
| **L3** | Recommend, or decide only where explicitly delegated. | `decision.v2` with evidence, alternatives, criteria, risk, confidence, reversal conditions. |
| **L4** | Qualified human approval required before execution. | Approval reference and named qualified human required. |
| **L5** | Michael-exclusive unless governance explicitly changes. | Michael is decision owner/approver. |

## Core rules

- Authority is a maximum ceiling, not a requirement to exercise it.
- A delegated child cannot have more authority than its parent work package.
- Source, tool, app, MCP, connector, or shared-Skill access never creates decision authority.
- Approval obligations cannot be delegated away.
- No agent or Skill may infer approval from historical preference, silence, conversational tone, calendar state, connector capability, or approval of another version.
- Monetary thresholds are not invented. If a required threshold is not configured, treat the action as approval-required.
- L4 requires a qualified human. L5 remains Michael-exclusive.
- Every material recommendation or decision must create an explainable `decision.v2` record without persisting private chain-of-thought.
- `TaskLedger` is canonical for approvals, decisions, tasks, verification, and consequential audit state.

## Shared capability decision boundaries

Release `v3.0.0` contains exactly 9 registered agent principals plus governed external shared Skills. Shared Skills are not delegated agents, task owners, decision owners, approval authorities, or MCP principals.

### Mesh Devil's Advocate

**Mesh Devil's Advocate** is available only to Chief of Staff and CRO through `skills.invoke_governed`. It is advisory only. It may challenge assumptions, evidence sufficiency, interpretation, routing, premortems, capacity, and decision conditions, but cannot modify canonical facts, execute external actions, or widen caller authority.

### Mesh Message Operations

**Mesh Message Operations** is available only to Chief of Staff, CRO, and CMO through `skills.invoke_governed`. It is an approval-bound execution capability, not a strategy, writing, recipient-selection, pricing, commitment, consent, legal, or publishing-policy authority.

Execution requires explicit, current, revocable approval bound to the exact payload hash/version and execution context, including sender identity and monitored reply path, immutable audience definition/count, channel, purpose, jurisdiction, consent basis, suppressions/exclusions/frequency controls, test result, required approvers, and execution window. Any material change invalidates approval and returns the item to preflight.

Preview is not approval. A draft request is not approval. Prior approval is not approval. Connector capability is not approval. Silence is not approval.

Immediately before execution, cancellation and kill-switch state must be rechecked. Execution must use a documented connector action with an idempotency key and per-attempt receipt. Requested, scheduled, sent, delivered, and replied are distinct states. Observed delivery or reply may be claimed only from evidence.

VP Content remains drafting/editorial-production only and has no Mesh Message Operations execution entitlement.

## Canonical fact ownership

For commercial work, Mesh Revenue Intelligence remains authoritative for canonical account identity, evidence classes, scores, stage, lifecycle, queue state, activation readiness, and prioritization. CFO remains authoritative for engagement finance and FP&A analysis. COO remains authoritative for delivery feasibility, capacity, and resource readiness. Neither shared Skill may rewrite those functional facts.

## Workspace Agent write approvals

ChatGPT Workspace Agent write-action approval is an additional product-level control, not a substitute for Mesh decision rights. Checked-in Workspace Agent manifests default write actions to **Always ask**.

A Workspace approval click cannot grant authority denied by the Mesh registry, satisfy an L5 decision unless Michael is the authorized decision owner, remove an inherited approval obligation, or convert a prohibited action into a permitted one. A recorded Mesh approval also does not disable **Always ask** unless a narrowly documented administrative exception is explicitly configured.

Connector Action Constraints narrow app behavior further. LinkedIn remains non-publishing. Apollo remains research/enrichment only. Mesh Message Operations may execute only documented supported connector actions after exact approval and preflight.

## Role identity, authority, and version provenance

- `agent_id` and canonical `display_name` identify who acted.
- `authority_level`, approval evidence, and registry policy establish what that role was allowed to decide or execute.
- `skill_agent_version`, model version, and repository release metadata establish which implementation produced a recommendation or action.
- A software version change does not rename a role or expand authority.
- A shared Skill name does not create a durable agent identity or independent decision principal.

## Change control

Any authority, accountable-domain, agent-principal, or shared-capability-entitlement change requires corresponding registry, test, documentation, governance-policy, Workspace Agent manifest/Skill, MCP allowlist, and audit/version updates. Material authority expansion is governed and cannot be performed by the affected agent.

See `explainable-decisions-audit.md` for canonical decision fields and mirror controls.
