# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository release: `v4.7.0 Enterprise Consulting Skill Consumption`. Current production QNAP deployment: `4.4.0`. Canonical Phase 1 authority/runtime contract: `4.0.0`.**

v4.7.0 integrates the released Mesh enterprise consulting enhancements into Chief of Staff, CRO, CFO, COO, CMO, and Answer & Decision Desk role guidance without changing the machine-readable registry, direct Skill arrays, L0-L5 authority, canonical sources, TaskLedger ownership, external-action controls, or production runtime. It adds no new MCP tool, connector, credential, database schema, QNAP deployment, autonomous communication, or consequential approval authority.

## Canonical architecture

Phase 1 contains exactly 10 registered agents: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations. Mesh Devil's Advocate remains a governed shared Skill, not an eleventh agent.

Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, completion, verification, and audit. Google TaskLedger, Prospect Universe, Slack, Gmail, connectors, Workspace state, and conversation history are scheduling, interaction, evidence, or mirror surfaces. `COMPLETED` remains distinct from `VERIFIED`.

## v4.7.0 Enterprise Consulting Skill Consumption

v4.7.0 consumes the newly released consulting-method capabilities through existing Skill bindings and governed delegation:

- Chief of Staff uses Mesh PPMD Bot v1.1+ for falsification-first Day-1 hypotheses, decision-linked synthesis, decision memos, outcome-first meetings, and artifact-first workshops.
- CRO consumes Revenue Intelligence v1.4+, Firm 360 v1.5+, Competitive Displacement v1.14+, GTM Orchestrator v2.3+, Buyer Psychology v3.1+, and Devil's Advocate v1.4+ through existing registry bindings.
- CFO contributes evidence-bound financial analysis, risks, mitigations, sensitivities, reversal conditions, and next tests to decision packages without receiving a new direct Skill binding.
- COO contributes delivery evidence, workstream outputs, owners, commitments, and approval dependencies to meetings and workshops without receiving a new direct Skill binding.
- CMO uses its existing Executive Communications binding for Mesh Messaging v1.2+ decision memos; Mesh Design System / Artifact Designer v0.4+ critic findings remain review inputs and do not transfer design or publication authority.
- Answer & Decision Desk may use approved decision artifacts as permission-scoped evidence but cannot promote draft hypotheses, syntheses, memos, workshop outputs, or critic findings into policy, precedent, or approval.

Key controls:

- skill capability is not agent authority;
- exactly 10 registered agents remain canonical;
- machine-readable direct Skill bindings and shared capabilities remain unchanged;
- Revenue Intelligence remains canonical for designated commercial and stakeholder truth;
- unsupported stakeholder power, stance, interest, dependency, budget authority, or purchase intent remains unknown;
- hypothesis confidence is not a deterministic score or approval input;
- decision memos do not approve themselves;
- meeting and workshop artifacts do not create commitments beyond delegated authority;
- critic readiness does not authorize publication or replace Mesh design authority;
- Message Operations and human approval remain the external communication execution boundary;
- `COMPLETED` remains distinct from `VERIFIED`.

Current v4.7.0 material:

- `specs/enterprise-consulting-skill-consumption-v4.7.0.feature`
- `tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py`
- `docs/enterprise-consulting-skill-consumption-v4.7.0.md`
- `docs/architecture-v4.7.0-enterprise-consulting.md`
- `docs/security-review-v4.7.0-enterprise-consulting.md`
- `docs/release-v4.7.0-enterprise-consulting.md`
- `docs/verification-v4.7.0-enterprise-consulting.md`
- `CHANGELOG-v4.7.0.md`

## v4.6.0 CFO Zero-Defect Execution Remediation

v4.6.0 closed the CFO execution and verification gaps identified after v4.5.x. CFO implementation is `1.2.0`; it retains L3 recommendation authority while gaining a deterministic core calculator and a CFO-only `mesh-data-analytics` shared Skill handoff for approved spreadsheet/model analysis, research, validation, visualization, and finance artifacts.

Key controls:

- exactly 10 registered agents remain canonical;
- `mesh-data-analytics` is an external shared Skill, not an agent principal;
- CFO MCP allowlist is unchanged and no human-only tool is added;
- management FP&A expands approved analytical source scope without creating GL, treasury, bank-balance, tax, or audit authority;
- core NPV, IRR, payback, discounted payback, break-even, runway, contribution-margin, and LTV:CAC calculations are reproducible through `chatgpt/skills/mesh-cfo/scripts/financial_math.py`;
- material spreadsheet, model, research, visualization, and durable-artifact work routes through governed Mesh Data Analytics with provenance and validation;
- historical v4.5.x release workflows are manual-only and cannot fail a later `main`;
- repository release, agent implementation, canonical runtime contract, and QNAP deployment identities are explicit and separate.

Current v4.6.0 material:

- `specs/cfo-execution-remediation-v4.6.0.feature`
- `tests/evaluations/test_cfo_execution_v460.py`
- `docs/cfo-execution-remediation-v4.6.0.md`
- `docs/architecture-v4.6.0-cfo-execution.md`
- `docs/security-review-v4.6.0-cfo-execution.md`
- `docs/runbook-v4.6.0-cfo-execution.md`
- `docs/release-v4.6.0-cfo-execution.md`
- `docs/verification-v4.6.0-cfo-execution.md`

## v4.5.2 CFO Financial Analysis Release State Finalization

v4.5.2 removed pre-publication `release candidate` wording from current-release pointers so the tagged source remained accurate after semantic publication.

Preserved without behavioral change:

- CFO implementation `1.1.0`;
- canonical Phase 1 runtime `4.0.0`;
- production QNAP Mesh CoS MCP `4.4.0`;
- exactly 10 registered agents;
- CFO L3 recommendation authority and Engagement Finance / FP&A domain;
- exact CFO MCP allowlist and Google Drive read-only scope;
- qualified-human approval gates;
- no autonomous trading, personal investment advice, enterprise GL/treasury/tax/audit authority, or private financial-reasoning persistence.

Current v4.5.2 material:

- `CHANGELOG-v4.5.2.md`
- `docs/material-turn-v4.5.2.md`
- `docs/release-authorization-v4.5.2.md`
- `docs/release-v4.5.2-release-state-finalization.md`
- `tests/evaluations/test_cfo_release_state_v452.py`

## v4.5.1 CFO Financial Analysis Release Closeout

v4.5.1 synchronized repository documentation with the completed v4.5.0 publication state and recorded final main/tag/release evidence. It was a documentation and release-control patch only.

## v4.5.0 CFO Financial Analysis Capability

v4.5.0 is the feature release that expanded the governed analytical depth of the CFO to implementation `1.1.0`. The CFO remains the Engagement Finance / FP&A executive with the same L3 recommendation boundary, source authority, parentage, delegation depth, MCP allowlist, read-only Workspace app scope, and qualified-human approval requirements.

v4.5.0 added:

- ROI, NPV, IRR, payback, break-even, and internal investment business-case methods;
- driver-based forecasting and forecast-versus-actual decomposition;
- unit economics, supported runway/burn, cash-conversion, and working-capital analysis;
- financial-model formula integrity, tie-out, and scenario QA;
- bounded financial-statement analysis and valuation using DCF, comparable, transaction, and sum-of-parts methods where applicable;
- WACC, terminal-value, source-freshness, scenario, and sensitivity controls;
- evidence-backed financial research planning, provenance, freshness, validation, and confidence;
- explicit prohibitions against autonomous trading, personal investment advice, external benchmark-as-policy behavior, and private financial-reasoning persistence.

Donor repositories are synthesized as reference material only. No donor code, packages, credentials, APIs, connectors, execution permissions, or numeric policies are imported.

Published v4.5.0 evidence:

- semantic tag `v4.5.0` and GitHub Release target `075eb8de04d6035a16ff2b6a24d2106ef8783b95`;
- ordinary main CI `34148492601`: SUCCESS;
- dedicated release workflow `34148492715`: SUCCESS;
- `docs/verification-v4.5.0-cfo-financial-analysis.md` records the final release receipt.

## v4.4.2 Data Intelligence correction

The September 2026 Data Intelligence occurrence was blocked because caller-created work packages placed narrative source, lock, connector, Skill, and evidence prerequisites in the CRO child's canonical dependency array. Mesh CoS MCP 4.4.0 correctly treated those values as predecessor task IDs and failed closed. A caller attempt to provide friendly delegation action labels was also correctly denied when those labels exceeded the CRO registry allowlist.

v4.4.2 fixes the caller and control-plane contract instead of weakening the runtime:

- canonical dependencies contain only actual predecessor task IDs;
- narrative prerequisites move to job contracts, acceptance tests, constraints, trigger conditions, evidence, or operating mirrors;
- caller action and capability lists are omitted or constrained to exact registry subsets;
- the malformed September child is preserved and cancelled through the accountable owner;
- exactly one deterministic dependency-clean recovery successor is allowed when provider state proves no effect will be replayed;
- the missed September full-universe review remains `FAILED_OCCURRENCE_ISOLATED` and is never converted into technical or business success;
- Chief of Staff orchestrates and verifies, CRO owns governed Data Intelligence execution, Revenue Intelligence remains authoritative for prospect and account commercial truth, CMO owns executive and authority-context framing, VP Content produces bounded reporting through CMO, and AgentOps owns reliability evidence;
- LinkedIn Authority OS remains labeled context only and cannot create account intent, sponsor, budget, urgency, lifecycle, priority, stage, or activation truth;
- business outcome and technical health are reported separately;
- the monthly full-universe, Apollo-budget-0, exact single-cell pre-read/write/readback/reconciliation contract is preserved;
- the external Scheduled Task remains wake transport and cannot be considered production-active without live enabled-state, schedule, timezone, and prompt readback.

The detailed v4.4.2 architecture and operating runbook remain preserved:

- `docs/data-intelligence-orchestrator-v4.4.2.md`
- `docs/architecture-v4.4.2-data-intelligence.md`
- `docs/runbook-v4.4.2-data-intelligence.md`
- `docs/security-review-v4.4.2-data-intelligence.md`
- `docs/release-v4.4.2-data-intelligence.md`

## v4.4.1 Commercial Operations correction

The Commercial Operations incidents were caused by caller-created work packages placing narrative prerequisite text in canonical task dependency arrays. The 4.4.0 runtime correctly treats each dependency as a canonical predecessor task ID and correctly failed closed.

v4.4.1 therefore fixes the caller/control-plane contract rather than weakening or redeploying the runtime:

- canonical dependencies contain only real canonical predecessor task IDs;
- narrative prerequisites move to job contracts, acceptance tests, constraints, trigger conditions, evidence, or operating mirrors;
- legacy malformed children are preserved and may be superseded once by a deterministic dependency-clean successor when provider state proves recovery is safe;
- business outcome and technical health are reported separately;
- CMO and VP Content participate through canonical parentage without gaining Revenue Intelligence commercial-truth authority;
- the central Commercial Operations scheduler is aligned to weekdays 08:00, 10:00, 12:00, and 16:00 America/New_York;
- `COM-EMAIL-SEND-DLY-001` remains isolated under the event-driven HITL loop and is never converted to polling.

The v4.4.1 material remains preserved:

- `docs/architecture-v4.4.1-commercial-operations.md`
- `docs/commercial-operations-orchestrator-v4.4.1.md`
- `docs/runbook-v4.4.1-commercial-operations.md`
- `docs/security-review-v4.4.1-commercial-operations.md`
- `docs/release-v4.4.1-commercial-operations.md`

## Production runtime and authority boundaries

The current production QNAP deployment is `4.4.0`. The Mesh CoS MCP 4.4.0 runtime remains production and is unchanged by repository capability release v4.7.0.

Key invariants remain:

- server-derived agent identity;
- exactly 10 registered agents with canonical parentage;
- deny-by-default tool/capability authority;
- `mesh.cos.owner-execution.v2` for delegated owner execution;
- human-only operations excluded from agent action surfaces;
- Revenue Intelligence as the sole account-level commercial-truth authority;
- exact canonical approval before consequential external action;
- no autonomous public publishing, prospect email send, LinkedIn action, pricing/scope commitment, trading action, or approval on Michael's behalf;
- OpenAI Secure MCP Tunnel as the only remote MCP ingress;
- QNAP changes remain operator-proxied through Michael.

## Data Intelligence ownership

- Chief of Staff: occurrence orchestration, work-graph integrity, scoped recovery, cross-functional coordination, and separate verification.
- CRO: accountable execution of governed Data Intelligence work assigned through TaskLedger.
- Revenue Intelligence: prospect-universe governance, structural qualification, entity state, evidence coverage, fit, queue, priority, lifecycle, signal, and activation truth.
- CMO: executive framing plus labeled marketing and authority context that cannot create commercial truth.
- VP Content: bounded internal reporting production under CMO.
- AgentOps Controller: defect classification, self-healing evidence, scheduler drift, release gating, and post-deployment health.
- LinkedIn Authority OS: authority, relationship, content, and performance context only.

## Commercial Operations ownership

- Chief of Staff: occurrence orchestration, work-graph integrity, scoped recovery, cross-job coordination, and separate verification.
- CRO: commercial analysis and governed seller-support work.
- Revenue Intelligence: account fit, lifecycle, priority, buying groups, activation readiness, commercial evidence, and buyer-response interpretation.
- CMO: marketing and authority strategy that may inform commercial context.
- VP Content: bounded content production under CMO.
- GTM Orchestrator: governed activation.
- Messaging Governance and Message Operations: exact approval and execution boundaries.
- LinkedIn Authority OS: authority, relationship, content, and performance context only.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core.
- `mcp/`: remote MCP transport and principal-specific tool/schema projection.
- `deployment/qnap/`: QNAP deployment, verification, backup, rollback, and acceptance assets for QNAP releases.
- `chatgpt/`: ChatGPT app contracts and package evidence.
- `config/`: governed capability and performance configuration.
- `specs/`: BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, scheduled-workflow, and production-readiness tests.
- `docs/`: architecture, material-turn, runbook, release, verification, security, and production-acceptance evidence.

## Verification

The repository release train retains full CI gates including:

```bash
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
python scripts/check-owner-execution-readiness.py
python scripts/check-capability-closure.py
python scripts/check-published-action-surface.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
pytest -q tests/evaluations/test_phase1_role_model_consistency.py
pytest -q tests/evaluations/test_cfo_financial_analysis_v450.py
pytest -q tests/evaluations/test_cfo_release_closeout_v451.py
pytest -q tests/evaluations/test_cfo_release_state_v452.py
pytest -q tests/evaluations/test_cfo_execution_v460.py
pytest -q tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py
```

GitHub CI also retains the existing TypeScript/MCP, QNAP shell/security, container, packaging, and transport checks. Passing these checks does not imply a new QNAP deployment.

## Release model

`v4.7.0` is the MINOR repository capability release for backward-compatible enterprise consulting skill consumption. It changes role guidance and release governance only. The canonical Phase 1 runtime remains `4.0.0`; CFO implementation remains `1.2.0`; production QNAP remains `4.4.0`.

No QNAP deployment is part of v4.7.0.

## Historical release-train evidence

The `v4.6.0 CFO Zero-Defect Execution Remediation`, `v4.5.2 CFO Financial Analysis Release State Finalization`, `v4.5.1 CFO Financial Analysis Release Closeout`, `v4.4.2 Data Intelligence Orchestration`, `v4.4.1 Commercial Operations Orchestration`, and `v4.4.0 Authority Closure` baselines remain preserved. Historical v4.3.x through v4.6.x documents remain release-train evidence and do not override the current v4.7.0 repository capability release.
