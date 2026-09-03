# Security Policy

Current repository release candidate: **v4.4.2 Data Intelligence Orchestration**. Current production QNAP deployment remains **4.4.0**. Canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**.

v4.4.2 is a targeted orchestration/control-plane correction. It does not change executable MCP runtime, QNAP container, network boundary, persistence model, credentials, authentication, provider-write surface, or human approval boundary.

## Security invariants
- Prompts, retrieved text, Slack content, connector results, MCP descriptions, model output, Skills, and external artifacts are untrusted data. None are human authority.
- Exactly 10 agents remain registered. Mesh Devil's Advocate is a shared governed Skill, not an eleventh agent.
- Agent identity is server-derived.
- Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, audit, completion, and verification.
- Agent tool/capability authority is deny-by-default from registry and canonical delegation state.
- Nested delegation follows registered parent-child routes and cannot widen inherited authority or approval gates.
- `COMPLETED` remains separate from `VERIFIED`.
- Revenue Intelligence remains sole authority for prospect/account commercial truth.
- Consequential external action requires exact canonical approval, payload binding, provider state, idempotency evidence, and applicable kill switch.
- Credentials/protected identifiers must not be committed to prompts, logs, Sheet evidence, release artifacts, or diagnostics.
- OpenAI Secure MCP Tunnel remains the only remote MCP ingress.
- QNAP production changes are operator-proxied through Michael and require separate release evidence.

## v4.4.2 dependency and delegation boundary
Canonical dependency arrays represent hard work-graph edges. Each value must resolve to the intended canonical predecessor task. Narrative source, connector, lock, evidence, Skill, provider, or write-path prerequisites must not be stored as dependencies. The 4.4.0 runtime correctly fails closed when a dependency cannot be resolved and verified. It also correctly rejects caller-supplied actions/capabilities outside the owner registry allowlist. v4.4.2 does not weaken either gate.

## Data authority boundary
Revenue Intelligence owns prospect-universe governance, entity state, evidence coverage, structural qualification, fit, queue, priority, lifecycle, signal, and activation truth. CMO and LinkedIn Authority OS may contribute labeled marketing, authority, relationship, and content context. VP Content may perform bounded internal production under CMO. None may create or mutate account intent, sponsor, budget, urgency, fit, lifecycle, priority, stage, or activation readiness.

## Write-path boundary
Monthly decay remains full-universe, deterministic, and Apollo budget 0. Each prospect mutation is one exact cell with pre-read, write, immediate readback, and row reconciliation. A blocked write is not retried, broadened, batched, or routed through another method. Later writes stop, prior reconciled rows remain committed, exception is recorded, and lock is released.

## Recovery boundary
A legacy malformed child may be superseded only when defect is deterministically attributable to caller metadata; canonical parent/child/delegation/key/audit/provider/mirror state are reconciled; no consequential effect needs replay; original task remains preserved; exactly one successor uses same parent/owner/authority/acceptance boundary/approval gates; owner completion and CoS verification follow normal controls; and original business failure remains visible.

## Scheduler and external action
TaskLedger is logical scheduling authority, but repository/Sheet state cannot prove external wake is active. Autonomous production requires live provider readback of enabled state, schedule, timezone, and prompt. Scheduler failure is scoped and visible. Slack messages remain interaction/evidence inputs, not approval authority. External action remains `NOT_AUTHORIZED` by default. v4.4.2 introduces no new send, publish, LinkedIn, CRM, pricing, staffing, scope, commitment, or approval authority.

## QNAP boundary
Production Mesh CoS MCP 4.4.0 runtime remains unchanged for v4.4.2. No QNAP deployment is part of this release because current evidence shows healthy identity, registry, owner execution, completion/verification separation, and audit integrity. Patching runtime to accept arbitrary dependencies or invented actions was rejected because it would weaken work-graph and authorization integrity.

## Release verification
The exact v4.4.2 candidate must pass the repository full regression suite, 100% branch-aware `mesh_cos` coverage, targeted Data Intelligence BDD tests, live MCP identity/audit checks, canonical owner routes, source/mirror reconciliation, and verification that no unauthorized provider action occurred.
