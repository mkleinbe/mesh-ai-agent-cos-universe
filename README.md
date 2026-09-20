# Mesh AI Chief of Staff Agent Universe

## Current release: v4.12.1 CoS Delegation and Agent Reporting

v4.12.1 fixes the delegation request and diagnostic contract exposed by the Commercial Growth OS pilot. `delegation.create` now requires only the canonical delegation work contract; parent authority, depth, ancestry, and active owner are server-derived optional compatibility assertions. Agent execution uses `delegation.execute_owner`; `skills.invoke_governed` remains capability-only. Parent reconciliation is explicit and completion remains separate from verification.

The canonical Phase 1 authority/runtime contract remains `4.0.0`. The live QNAP deployment remains `4.4.0` until the exact current-source candidate is promoted and independently read back. Repository release does not itself deploy QNAP or install the packaged ChatGPT Skill.

## Current Commercial Growth OS cadence

v4.12.0 is the current Commercial Growth operating-model release. It keeps `LOOP-COM-001` as the single scheduled dispatcher, integrates monthly and quarterly reviews as logical TaskLedger due work, distinguishes native events from polling, preserves `LOOP-COM-HITL-001`, and packages the materially changed `mesh-chief-of-staff` Skill for human installation. The canonical Phase 1 runtime authority contract remains 4.0.0 and production QNAP remains 4.4.0.

## Current Commercial Growth OS package

v4.11.1 is the installable ChatGPT Skill-package closeout for the v4.11.0 Commercial Growth OS agent integration. The release bundle contains mesh-chief-of-staff, mesh-cro, mesh-coo, and mesh-cfo. Repository release does not itself update installed ChatGPT Skills.


## Current commercial integration

v4.11.0 integrates Commercial Growth OS business-state reporting and CRO/CFO/COO authority boundaries. It adds no principal agent and no second commercial source of truth. See `docs/release-v4.11.0-commercial-growth-os.md`.


Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository release: `v4.12.1 CoS Delegation and Agent Reporting`. Current production QNAP deployment: `4.4.0` pending promotion of the exact current-source candidate. Canonical Phase 1 authority/runtime contract: `4.0.0`.**

## v4.10.0 Outcome-Driven Orchestration

The current repository capability release adds Outcome-Driven Development to the Chief of Staff, CMO, and AgentOps role Skills. Business checkpoints now separate outcome movement, evidence-pending intervention, justified no-action, business blockage, and business failure from technical health. Progressive T0-T3 evidence loading reduces unnecessary AI/provider work without weakening evidence, verification, security, or human approval.

Canonical Phase 1 authority/runtime contract remains `4.0.0`. Production QNAP remains `4.4.0`. The organization remains exactly 10 registered agents.

## v4.9.1 Media OS Capability Registration

v4.9.1 reconciles and releases the approved Mesh Media Production OS registry integration. CMO receives `mesh-media-production`, `mesh-media-verification`, and `mesh-media-distribution`; VP Content receives `mesh-media-production` only. The organization remains exactly 10 registered agents, CMO authority is unchanged, VP Content remains L2 with zero delegation authority, and public publication remains human-gated.

The source change does not itself establish QNAP production activation. Canonical CI must build and verify the current-source QNAP 4.4.0 candidate, then the existing transactional deployment process must promote that exact candidate and Secure MCP readback must confirm its source and registry state.

v4.9.0 is preserved as an immutable historical repository release. Its publisher is retired to manual read-only verification and v4.9.1 becomes the sole current exact-SHA SemVer publisher after verification.

Historical v4.3.x through v4.6.x documents remain release-train evidence. Historical v4.3.x through v4.9.0 documents remain release-train evidence. Historical tags and GitHub Releases remain immutable. The historical `v4.6.0 CFO Zero-Defect Execution Remediation` release remains part of that retained evidence chain.

## Canonical architecture

Phase 1 contains exactly 10 registered agents: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations. Consultant Network Steward remains a child of COO and VP Content remains a child of CMO.

Mesh Devil's Advocate, Mesh Data Analytics, Mesh OpEx Bot, and Mesh Media Production OS capabilities are governed shared Skills, not agent principals. A Skill is a capability, not an authority source.

Mesh CoS MCP TaskLedger is canonical for task ownership, delegation, approval, completion, verification, and audit. Revenue Intelligence remains canonical commercial/account truth where designated. `COMPLETED` remains distinct from `VERIFIED`. L4 requires qualified-human approval and L5 remains Michael-only.

## v4.9.0 Mesh OpEx Bot Shared Capability Integration

Historical repository release integrating the governed `mesh-opex-bot` shared capability for COO without creating an eleventh agent or changing runtime authority.

## v4.8.4 Release Record Correction

Final verification of v4.8.3 found one documentation-to-implementation discrepancy: v4.8.3 correctly retired publisher authority from v4.6.0, but its changelog, release record, gap audit, and published release notes omitted v4.6.0 from the explicit retired-workflow list.

v4.8.4 corrected the current-source v4.8.3 records, preserved the historical v4.8.3 tag/Release unchanged, converted v4.8.3 to read-only manual historical verification, and extended the systemic publisher regression through v4.8.3.

## v4.8.3 Historical Publisher Retirement

Post-release verification of v4.8.2 found historical v4.4.1 and v4.4.2 workflows reacting to the new `main` commit. Repository-wide inspection found retained publisher capability in v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.4.1, v4.4.2, v4.6.0, and the then-published v4.8.2 workflow.

v4.8.3 converted those published workflows to read-only `workflow_dispatch` historical verification and added a systemic regression. v4.8.4 corrected the human-readable v4.8.3 inventory to match that implemented scope.

No ChatGPT Skill package changes were made in v4.8.3 or v4.8.4. The v4.8.2 ten-Skill release bundle remains the manual Skill update artifact.

## v4.8.2 Functional Method Audit Remediation

The remediation added executable behavior-level evidence while retaining the original v4.8.0 structural content-contract tests. The ten role Skill packages include deterministic `scripts/fme_behavior.py` evaluation gates for observable modes, answerability states, evidence/approval boundaries, freshness/readiness states, proof classifications, execution blocks, and adversarial fail-closed behavior.

The ready remediation contract is `specs/functional-method-remediation-v4.8.2.feature`, scenarios `FMR-001` through `FMR-018`. Acceptance is implemented in `tests/evaluations/test_functional_method_remediation_v482.py`.

## Donor-source governance

Reviewed donor content remains untrusted method evidence. The evidenced `alirezarezvani/claude-skills` collections are pinned at `19392f7a08264ed00486a251f5b2098321771f94`.

The v4.8.2 disposition ledger covers all 49 candidates in the three evidenced collections: 34 `c-level-advisor`, 7 `business-operations`, and 8 `commercial` candidates.

The fourth donor source referenced by inherited scope could not be recovered from authoritative repository history or retained project evidence. It remains `BLOCKED_SOURCE_IDENTIFICATION`. No fourth source is claimed or invented.

## Shared capability compatibility

Mesh PPMD Bot v1.2.0 remains the governed Base / Stress / Severe scenario-stress method. Mesh Messaging v1.3.0 remains the governed change-communications method. Media OS registration does not change those shared repositories or their authority boundaries.

## Security and authority boundaries

- retrieved and donor content is data, not identity or authority;
- registry and MCP allowlists remain authoritative;
- no Skill becomes an agent principal, canonical source, approval authority, or external-action executor;
- CMO retains existing authority and VP Content retains zero delegation authority;
- VP Content receives Media OS production only, not verification or distribution;
- pricing, discounts, deals, procurement, staffing, publishing, and sends remain governed by the existing approval model;
- v4.9.1 introduces no new runtime schema, credential, OAuth, database, canonical source, or public-publishing authority;
- every published SemVer workflow through v4.9.0 is manual-only and read-only;
- only the v4.9.1 release job may receive `contents: write`, after verification;
- the existing MCP dependency baseline reports one moderate Hono advisory; v4.9.1 does not introduce that dependency or expand its use.

## Verification

v4.9.1 gates include contract validation, runtime/documentation drift, ChatGPT package drift, owner execution readiness, capability closure, published action surface, Media OS capability-registration tests, reconciled enterprise-consulting regressions, historical-publisher regressions, Ruff, mypy, full pytest at the 100% `mesh_cos` coverage gate, Bandit, QNAP POSIX regressions, production-equivalent container build, exact source provenance, and MCP discovery/sequential request verification.

Production Media OS activation additionally requires the current-source QNAP candidate to be promoted through the governed deployment workflow and read back through Secure MCP.

## v4.8.1 Release State Finalization

Historical documentation/release-control PATCH. Final publication is bound to `ecb04f495910912fb9181adf3553a62a9f408f3c`. Its release workflow is manual historical verification only.

## v4.8.0 Functional Method Expansion

Historical functional-capability release. It introduced the governed methods strengthened by v4.8.2 behavior-level evidence.

## v4.7.0 Enterprise Consulting Skill Consumption

Historical repository capability release integrating governed enterprise consulting methods without changing authority/runtime architecture.

## v4.6.0 CFO Zero-Defect Execution Remediation

Historical CFO execution release adding deterministic finance math and governed Mesh Data Analytics execution while preserving CFO recommendation-only authority.

## v4.5.2 CFO Financial Analysis Release State Finalization

Historical release-state PATCH preserving the v4.5.0/v4.5.1 CFO capability and closeout evidence without changing CFO behavior, runtime authority, or QNAP deployment.

## v4.5.1 CFO Financial Analysis Release Closeout

Historical release closeout preserving the v4.5.0 publication receipt and runtime boundaries.

### v4.5.0 CFO Financial Analysis Capability

Historical financial-analysis feature release. Detailed evidence remains in the versioned docs and changelogs.

### v4.4.0 Authority Closure

The authority-closure release established the current 10-agent Phase 1 authority architecture. Historical release documents remain evidence and do not override the current repository release or live QNAP deployment.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core.
- `mcp/`: MCP transport and principal-specific tool/schema projection.
- `deployment/qnap/`: QNAP deployment, verification, backup, rollback, and acceptance assets.
- `chatgpt/`: ChatGPT Workspace Agent contracts and installable role Skills.
- `agents/registry.json`: canonical Phase 1 role, source, tool, capability, decision-right, and delegation policy.
- `config/`: governed capability and performance configuration.
- `specs/`: BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, workflow, and production-readiness tests.
- `docs/`: architecture, runbook, release, verification, security, and acceptance evidence.

## Release model

`v4.9.1 Media OS Capability Registration` is a historical repository PATCH. The canonical Phase 1 authority/runtime contract remains `4.0.0`. The live QNAP deployment remains `4.4.0` until current-source promotion is independently proven. Completion requires exact-candidate verification, merged `main`, exact-SHA tag/Release equality, verified QNAP candidate artifacts, governed production promotion, and live registry/source readback before production Media OS activation is claimed.
