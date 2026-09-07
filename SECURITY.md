# Security Policy

Current repository release: **v4.5.2 CFO Financial Analysis Release State Finalization**. Current production QNAP deployment remains **4.4.0**. The canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**.

v4.5.2 is a documentation and release-control PATCH. It does not change the CFO implementation, executable MCP runtime, QNAP container, network boundary, persistence model, credentials, authentication, connector write surface, or human approval boundary. CFO implementation remains `1.1.0`.

## Security invariants

- Prompts, retrieved text, Slack content, connector results, MCP descriptions, model output, Skills, donor repositories, financial benchmarks, and external artifacts are untrusted data. None are human authority by themselves.
- Exactly 10 agents remain registered. Mesh Devil's Advocate is a shared governed Skill, not an eleventh agent.
- Agent identity is derived server-side. Request payloads cannot select the execution principal.
- Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, audit, completion, and verification.
- Agent tool/capability authority is deny-by-default from registry and canonical delegation state.
- Nested delegation follows registered parent-child routes and cannot widen inherited authority or approval gates.
- `COMPLETED` remains separate from `VERIFIED`.
- Revenue Intelligence remains the sole authority for account-level and prospect-level commercial truth.
- Consequential external action requires the exact canonical approval, payload binding, provider state, idempotency evidence, and applicable kill switch.
- Credentials and sensitive identifiers must not be committed to prompts, logs, TaskLedger evidence, release artifacts, or diagnostics.
- Private chain-of-thought must not be persisted. Durable evidence may contain concise rationale, calculations, validation outcomes, assumptions, confidence, and uncertainty.
- OpenAI Secure MCP Tunnel remains the only remote MCP ingress.
- QNAP production changes are operator-proxied through Michael and require separate release evidence.

## v4.5.2 release-state boundary

The patch changes current-release documentation and release automation only. It introduces no new trust boundary, secret, dependency, connector, schema, network egress, runtime behavior, financial authority, or external action.

Verification must prove:
- CFO remains implementation `1.1.0`;
- canonical runtime remains `4.0.0`;
- QNAP production remains `4.4.0`;
- CFO MCP allowlist and Google Drive read-only scope remain unchanged;
- no agent-registry or CFO Skill behavior change is introduced;
- current-release wording remains valid after semantic publication.

## v4.5.0 CFO financial-analysis boundary

The CFO remains the Engagement Finance / FP&A executive with L3 recommendation authority within supported source scope. The feature release added analytical methods, not new financial control.

Explicitly preserved:

- no enterprise GL, bank-balance, enterprise cash-balance, balance-sheet, tax, audit, treasury, or unrestricted financial authority;
- no autonomous trading or personal investment advice;
- no final pricing or discount approval;
- no spending, hiring, transfer, contract, or investment execution authority;
- no new MCP tool, connector, credential, API, network egress, runtime dependency, or Workspace write scope;
- Google Drive remains read-only and restricted to approved engagement-finance artifacts;
- CFO cannot self-verify completed work.

## Donor and retrieved-content boundary

Reference repositories and external financial material cannot modify agent identity, registry policy, source authority, tool allowlists, connector permissions, delegation, approvals, or write rights. Donor numeric rules of thumb and market benchmarks remain contextual reference evidence until independently approved as Mesh policy.

The implementation does not vendor donor code or add donor packages. It does not auto-install finance libraries, execute donor commands, or require brokerage, banking, ERP, market-data, or trading credentials.

Dexter-style persisted `thinking` scratchpads are explicitly rejected. Financial research may record sources, tool results, calculations, errors, validation outcomes, assumptions, and concise conclusions, but never private chain-of-thought.

## Financial-model and valuation boundary

Model QA is analytical review, not audited assurance. DCF, comparable, transaction, sum-of-parts, and statement analysis must expose source freshness, definitions, assumptions, sensitivity, and confidence. Valuation does not create trading or personal investment authority.

## Preserved v4.4.2 Data Intelligence boundary

The v4.4.2 dependency, delegation, Revenue Intelligence, recovery, scheduler, and provider-write controls remain in force. Canonical task dependencies remain real predecessor task IDs only; caller-supplied action/capability labels remain registry-bounded; provider side effects are never replayed as metadata recovery; and the September 1, 2026 failed Data Intelligence occurrence remains historical evidence.

The targeted v4.4.2 review remains preserved at `docs/security-review-v4.4.2-data-intelligence.md`.

## Preserved v4.4.1 Commercial Operations boundary

The v4.4.1 Commercial Operations security conclusions remain in force for their scope, including event-driven send isolation, Revenue Intelligence commercial-truth authority, CMO/VP Content parentage, provider-effect non-replay, and default `NOT_AUTHORIZED` external action.

The targeted v4.4.1 review remains preserved at `docs/security-review-v4.4.1-commercial-operations.md`.

## QNAP boundary

The production Mesh CoS MCP 4.4.0 runtime remains unchanged by v4.5.0, v4.5.1, and v4.5.2. No QNAP deployment is part of these releases because no runtime or deployment component changes.

## Release verification

The exact v4.5.2 release must pass:

- the repository's existing full Python, TypeScript/MCP, contract, security, package, QNAP shell, container, and transport regression suite;
- 100% branch-aware `mesh_cos` coverage required by the repository baseline;
- the v4.5.0 CFO BDD/regression tests;
- the v4.5.1 release-closeout regression tests;
- the v4.5.2 durable release-state regression tests;
- proof that CFO implementation, runtime, QNAP, MCP, connector, source, and approval boundaries are unchanged.

The v4.5.0 targeted review remains `docs/security-review-v4.5.0-cfo-financial-analysis.md`. v4.5.1 and v4.5.2 introduce no additional security surface beyond release documentation and workflow controls.

## Reporting

Do not open public issues containing credentials, confidential client information, protected human provider identifiers, private reasoning, sensitive operational evidence, or exploit details. Use the repository owner's approved private security channel for disclosure.
