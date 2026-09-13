# v4.8.4 Release Record Correction

`v4.8.4 Release Record Correction` is the current repository release designation. It is a documentation and release-control PATCH that corrects the v4.8.3 human-readable inventory to include v4.6.0, which the v4.8.3 implementation did retire, and advances release ownership to v4.8.4 without rewriting the historical v4.8.3 tag or GitHub Release.

Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged.  
Production QNAP deployment: `4.4.0`, unchanged.  
Registered organization: exactly 10 agents, unchanged.

For compatibility with historical release assertions, the canonical Phase 1 authority/runtime contract **4.0.0** and production QNAP **4.4.0** remain the governing runtime boundaries.

## Release-record correction

The complete v4.8.3 implemented retirement inventory is v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.4.1, v4.4.2, v4.6.0, and v4.8.2. The prior v4.8.3 source/release record omitted v4.6.0 from that explicit list even though the workflow was correctly retired.

v4.8.4 corrects current-source documentation, retires v4.8.3 to read-only manual historical verification, extends the systemic publisher invariant through v4.8.3, and becomes the only active SemVer publisher. The v4.8.4 release job receives `contents: write` only after successful verification and publishes against exact `GITHUB_SHA`.

No ChatGPT Skill package changes in v4.8.4. The v4.8.2 ten-Skill bundle remains the manual update artifact.

## Security and scope

v4.8.4 is TARGETED release-control remediation. It does not change runtime code, agent behavior, registry state, MCP tools, credentials, OAuth, network boundaries, dependencies, QNAP production, source authority, or consequential-action approval boundaries. The pre-existing moderate Hono npm advisory remains documented baseline risk.

The fourth donor identifier remains `BLOCKED_SOURCE_IDENTIFICATION`; no fourth-source completeness is claimed.

See `docs/release-v4.8.4-release-record-correction.md`, `docs/security-review-v4.8.4-release-record-correction.md`, `docs/verification-v4.8.4-release-record-correction.md`, `docs/gap-audit-v4.8.4-release-record-correction.md`, and `CHANGELOG-v4.8.4.md`.

# v4.8.3 Historical Publisher Retirement

`v4.8.3 Historical Publisher Retirement` is the prior release-control closeout PATCH for the v4.8.x audit remediation. Post-release verification of v4.8.2 found residual historical publisher capability. v4.8.3 converted v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.4.1, v4.4.2, v4.6.0, and v4.8.2 to read-only, manual-only historical verification and added a systemic regression protecting every already-published v4.x SemVer workflow through v4.8.2.

The historical v4.8.3 GitHub Release remains unchanged. v4.8.4 is the correcting release for the prior human-readable omission of v4.6.0.

No ChatGPT Skill package changes were made in v4.8.3.

# v4.8.2 Functional Method Audit Remediation

`v4.8.2 Functional Method Audit Remediation` is the prior corrective PATCH for the v4.8.x audit findings. It added executable behavior-level evaluation gates across the existing 10 role Skill packages; ready BDD scenarios `FMR-001` through `FMR-018`; an exhaustive 49-candidate donor disposition ledger; explicit `BLOCKED_SOURCE_IDENTIFICATION` handling for the unresolved fourth donor; durable v4.8.1 release evidence; and its now-historical exact-SHA publisher.

It did not change the Python runtime version, MCP catalog, TaskLedger, Revenue Intelligence authority, agent roster/parentage, L4/L5 decision rights, external-action controls, credentials, OAuth, network boundaries, database schemas, shared PPMD/Messaging releases, or QNAP production deployment.

`tests/evaluations/test_functional_method_remediation_v482.py` executes deterministic package-local behavior gates rather than relying only on `SKILL.md` phrase presence. The v4.8.0 phrase/content contract remains structural regression coverage.

The evidenced donor repository `alirezarezvani/claude-skills` remains pinned at `19392f7a08264ed00486a251f5b2098321771f94`. Explicit dispositions cover 34 c-level-advisor, 7 business-operations, and 8 commercial candidates. The fourth donor identifier remains `BLOCKED_SOURCE_IDENTIFICATION`; no fourth-source coverage is claimed.

Mesh PPMD Bot v1.2.0 and Mesh Messaging v1.3.0 remain compatible and unchanged.

# v4.8.1 Release State Finalization

`v4.8.1 Release State Finalization` is a historical documentation and release-control PATCH. It is published at `ecb04f495910912fb9181adf3553a62a9f408f3c`; its workflow is manual historical verification only.

The canonical Phase 1 authority/runtime contract remained **4.0.0**, production QNAP remained **4.4.0**, and the organization remained exactly **10 registered agents**.

# v4.8.0 Functional Method Expansion

`v4.8.0 Functional Method Expansion` is the prior functional-capability release. It deepened the operating methods of the existing Mesh Phase 1 organization while leaving the machine-readable registry, canonical Phase 1 authority/runtime contract **4.0.0**, production QNAP **4.4.0**, and exactly **10 registered agents** unchanged.

# v4.7.0 Enterprise Consulting Skill Consumption

`v4.7.0 Enterprise Consulting Skill Consumption` is a historical repository capability release. It integrated governed enterprise consulting methods while leaving the canonical Phase 1 authority/runtime contract **4.0.0**, production QNAP **4.4.0**, and exactly **10 registered agents** unchanged.

# v4.6.0 CFO Zero-Defect Execution Remediation

`v4.6.0 CFO Zero-Defect Execution Remediation` is a historical CFO execution release. It added deterministic finance math, CFO-only governed `mesh-data-analytics`, management FP&A source scope, and behavior-level finance tests while preserving recommendation-only authority and QNAP 4.4.0.

# v4.5.2 CFO Financial Analysis Release State Finalization

Historical documentation and release-control PATCH. CFO implementation and runtime authority remained unchanged.

# v4.5.1 CFO Financial Analysis Release Closeout

Historical documentation and release-control PATCH that finalized the v4.5.0 publication evidence.

# v4.5.0 CFO Financial Analysis Capability

Historical governed financial-analysis feature release. No enterprise GL, treasury, tax, audit, trading, bank-balance, external-write authority, or QNAP deployment was introduced.

# v4.4.2 Data Intelligence Orchestration

Historical orchestration correction. Production QNAP remained 4.4.0.

# v4.4.1 Commercial Operations Orchestration

Historical orchestration correction preserving Revenue Intelligence commercial truth and event-driven HITL send isolation.

# v4.4.0 Authority Closure

Historical release identity is preserved for regression and audit continuity. The canonical Phase 1 authority/runtime contract **4.0.0** remains the current authority contract, and production QNAP **4.4.0** remains current.

# v4.3.0 Cross-Agent Owner Execution

Historical release identity `v4.3.0` is preserved. It established governed server-derived owner execution and nested child execution before later authority-closure and QNAP release trains. It does not override the current runtime or release state.

Historical v4.3.x through v4.8.x documents remain release-train evidence and do not override the current repository release.
