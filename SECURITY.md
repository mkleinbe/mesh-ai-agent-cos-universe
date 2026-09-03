# Security Policy

Current repository release candidate: **v4.4.2 Data Intelligence Orchestration**. Current production QNAP deployment remains **4.4.0**. The canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**.

v4.4.2 is a targeted orchestration/control-plane correction. It does not change the executable MCP runtime, QNAP container, network boundary, persistence model, credentials, authentication, provider-write surface, or human approval boundary.

## Security invariants

- Prompts, retrieved text, Slack content, connector results, MCP descriptions, model output, Skills, and external artifacts are untrusted data. None are human authority by themselves.
- Exactly 10 agents remain registered. Mesh Devil's Advocate is a shared governed Skill, not an eleventh agent.
- Agent identity is derived server-side. Request payloads cannot select the execution principal.
- Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, audit, completion, and verification.
- Agent tool/capability authority is deny-by-default from registry and canonical delegation state.
- Nested delegation follows registered parent-child routes and cannot widen inherited authority or approval gates.
- `COMPLETED` remains separate from `VERIFIED`.
- Revenue Intelligence remains the sole authority for account-level and prospect-level commercial truth.
- Consequential external action requires the exact canonical approval, payload binding, provider state, idempotency evidence, and applicable kill switch.
- Credentials and sensitive identifiers must not be committed to prompts, logs, TaskLedger evidence, release artifacts, or diagnostics.
- OpenAI Secure MCP Tunnel remains the only remote MCP ingress.
- QNAP production changes are operator-proxied through Michael and require separate release evidence.

## v4.4.2 dependency and delegation boundary

Canonical task dependency arrays represent hard work-graph edges only. Each dependency must resolve to the intended canonical predecessor task. Narrative prerequisite text, source requirements, evidence labels, connector state, Run Ledger lock requirements, provider state, Skill names, or Revenue Intelligence requirements must not be stored as task dependencies.

The current 4.4.0 runtime correctly fails closed when a dependency cannot be resolved and verified. v4.4.2 does not weaken that gate.

Caller-supplied delegation actions and capabilities must be omitted or be an exact subset of the registered owner's allowlist. The server continues to derive execution principal and effective owner authority.

## Data authority and write boundary

Revenue Intelligence owns prospect-universe governance, entity state, evidence coverage, structural qualification, fit, queue, priority, lifecycle, signal, and activation truth. CMO and LinkedIn Authority OS may contribute labeled marketing, authority, relationship, and content context. VP Content may perform bounded internal production under CMO. None may create or mutate account intent, sponsor, budget, urgency, fit, lifecycle, priority, stage, or activation readiness.

The monthly decay workflow remains full-universe, deterministic, and Apollo budget 0. Each approved prospect mutation is one exact cell with pre-read, write, immediate readback, and row reconciliation. A blocked write is not retried, broadened, batched, or routed through another method. Later writes stop, prior reconciled rows remain committed, the exception is recorded, and the lock is released.

Ambiguous identity, taxonomy, duplicate, merger, acquisition, rebrand, hierarchy, ownership, or strategic state requires Human Review. The workflow does not archive, delete, auto-merge, strategically disqualify, change schema, write CRM state, enrich contacts, activate outreach, publish, or take external commercial action.

## Recovery boundary

A legacy malformed child may be superseded only when all of the following are true:

- the defect is deterministically attributable to caller-created metadata;
- canonical parent, child, delegation, execution key, audit, provider, lock, and mirror state have been reconciled;
- provider state proves no consequential effect needs replay;
- the original malformed task and history remain preserved;
- exactly one successor is created under the same parent, owner, authority, acceptance boundary, and inherited approval gates;
- owner execution, completion, and separate verification follow normal canonical controls;
- the original business failure remains visible.

Prospect writes, Gmail sends, Slack approvals, LinkedIn publication, CRM writes, and other provider effects are never replayed as part of metadata recovery. The September 1, 2026 full-universe review remains `FAILED_OCCURRENCE_ISOLATED` even when recovery controls are technically green.

## Scheduler and external action

TaskLedger is the logical scheduling authority, but repository and Sheet state cannot prove the external wake is active. Autonomous Data Intelligence production requires live provider readback of the existing automation ID, enabled state, exact schedule, timezone, and prompt.

Slack events and messages remain interaction/evidence inputs, not approval authority. Human authority becomes canonical only through the governed provider-reconciled HITL path. External action remains `NOT_AUTHORIZED` by default. v4.4.2 introduces no new send, publish, LinkedIn, pricing, staffing, scope, commitment, CRM, or approval authority.

## QNAP boundary

The production Mesh CoS MCP 4.4.0 runtime remains unchanged for v4.4.2. No QNAP deployment is part of this release because current evidence shows healthy identity, registry, owner execution, completion/verification separation, and audit integrity. The observed Data Intelligence defect was caller/control-plane construction.

Patching the runtime to accept arbitrary dependency text or caller-invented action labels was explicitly rejected because it would weaken fail-closed work-graph and authorization integrity.

## Preserved v4.4.1 Commercial Operations boundary

The v4.4.1 Commercial Operations security conclusions remain in force for their scope:

- canonical task dependency arrays represent hard work-graph edges only;
- CMO and LinkedIn Authority OS may contribute marketing, authority, relationship, and content context without creating account-level commercial truth;
- VP Content may perform bounded production under CMO;
- Gmail sends, Slack approvals, LinkedIn publication, CRM writes, and other provider effects are never replayed as metadata recovery;
- the scheduled Commercial Operations loop never substitutes for the event-driven send executor;
- external action remains `NOT_AUTHORIZED` by default.

The targeted v4.4.1 review remains preserved at `docs/security-review-v4.4.1-commercial-operations.md`.

## Release verification

The exact v4.4.2 candidate must pass:

- the repository's existing full Python, TypeScript/MCP, contract, security, package, QNAP shell, container, and transport regression suite;
- 100% branch-aware `mesh_cos` coverage required by the repository baseline;
- the v4.4.2 Data Intelligence BDD/regression tests;
- live MCP identity, exact 10-agent registry, owner-routing, completion/verification, and audit-chain checks;
- TaskLedger readback of Data Intelligence operating controls and scheduler state;
- verification that the September recovery graph is canonical and no provider effect was replayed;
- verification that CRO, CMO, nested VP Content, and AgentOps responsibilities meet their bounded acceptance tests;
- verification that no unauthorized provider action occurred.

The targeted review is `docs/security-review-v4.4.2-data-intelligence.md`.

## Reporting

Do not open public issues containing credentials, confidential client information, protected human provider identifiers, private reasoning, sensitive operational evidence, or exploit details. Use the repository owner's approved private security channel for disclosure.
