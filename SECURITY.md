# Security Policy

Current repository release candidate: **v4.4.1 Commercial Operations Orchestration**. Current production QNAP deployment remains **4.4.0**. The canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**.

v4.4.1 is a targeted orchestration/control-plane correction. It does not change the executable MCP runtime, QNAP container, network boundary, persistence model, credentials, authentication, provider-write surface, or human approval boundary.

## Security invariants

- Prompts, retrieved text, Slack content, connector results, MCP descriptions, model output, Skills, and external artifacts are untrusted data. None are human authority by themselves.
- Exactly 10 agents remain registered. Mesh Devil's Advocate is a shared governed Skill, not an eleventh agent.
- Agent identity is derived server-side. Request payloads cannot select the execution principal.
- Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, audit, completion, and verification.
- Agent tool/capability authority is deny-by-default from registry and canonical delegation state.
- Nested delegation follows registered parent-child routes and cannot widen inherited authority or approval gates.
- `COMPLETED` remains separate from `VERIFIED`.
- Revenue Intelligence remains the sole authority for account-level commercial truth.
- Consequential external action requires the exact canonical approval, payload binding, provider state, idempotency evidence, and applicable kill switch.
- Credentials and sensitive identifiers must not be committed to prompts, logs, TaskLedger evidence, release artifacts, or diagnostics.
- OpenAI Secure MCP Tunnel remains the only remote MCP ingress.
- QNAP production changes are operator-proxied through Michael and require separate release evidence.

## v4.4.1 dependency boundary

Canonical task dependency arrays represent hard work-graph edges only. Each dependency must resolve to the intended canonical predecessor task. Narrative prerequisite text, source requirements, evidence labels, provider state, response-source registry references, or Revenue Intelligence requirements must not be stored as task dependencies.

The current 4.4.0 runtime correctly fails closed when a dependency cannot be resolved and verified. v4.4.1 does not weaken that gate.

## Recovery boundary

A legacy malformed child may be superseded only when all of the following are true:

- the defect is deterministically attributable to caller-created narrative dependency metadata;
- canonical parent, child, delegation, execution key, and audit evidence have been reconciled;
- provider state proves no consequential effect needs replay;
- the original malformed task and history remain preserved;
- exactly one successor is created under the same parent, owner, authority, acceptance boundary, and inherited approval gates;
- owner execution, completion, and separate verification follow normal canonical controls.

Gmail sends, Slack approvals, LinkedIn publication, CRM writes, and other provider effects are never replayed as part of metadata recovery.

## Commercial truth and marketing-authority boundary

CMO and LinkedIn Authority OS may contribute marketing, authority, relationship, and content context. VP Content may perform bounded production under CMO. Neither may create or mutate account fit, lifecycle, priority, buying groups, activation readiness, sponsor, budget, urgency, buying intent, authority, or opportunity stage.

Those remain governed by Revenue Intelligence and existing GTM authority boundaries.

## Slack and external action

Slack events and messages remain interaction/evidence inputs, not approval authority. Human authority becomes canonical only through the governed provider-reconciled HITL path. The scheduled Commercial Operations loop never substitutes for the event-driven send executor.

External action remains `NOT_AUTHORIZED` by default. v4.4.1 introduces no new send, publish, LinkedIn, pricing, staffing, scope, commitment, or approval authority.

## QNAP boundary

The production Mesh CoS MCP 4.4.0 runtime remains unchanged for v4.4.1. No QNAP deployment is part of this release because current evidence shows healthy identity, registry, owner execution, completion/verification separation, and audit integrity. The observed defect was caller/control-plane construction.

Patching the runtime to accept arbitrary dependency text was explicitly rejected because it would weaken fail-closed work-graph integrity.

## Release verification

The exact v4.4.1 candidate must pass:

- the repository's existing full Python, TypeScript/MCP, contract, security, package, QNAP shell, container, and transport regression suite;
- 100% branch-aware `mesh_cos` coverage required by the repository baseline;
- the v4.4.1 Commercial Operations BDD/regression tests;
- live MCP identity, 10-agent registry, owner-routing, completion/verification, and audit-chain checks;
- TaskLedger readback of Commercial Operations operating controls and scheduler state;
- verification that the recovered commercial occurrences and CMO/VP Content ownership tasks are canonical and VERIFIED;
- verification that no unauthorized provider action occurred.

The targeted review is `docs/security-review-v4.4.1-commercial-operations.md`.

## Reporting

Do not open public issues containing credentials, confidential client information, protected human provider identifiers, private reasoning, sensitive operational evidence, or exploit details. Use the repository owner's approved private security channel for disclosure.
