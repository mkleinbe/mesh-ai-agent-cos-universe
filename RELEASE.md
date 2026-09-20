# v4.13.2 QNAP Source Identity Repair

This PATCH release corrects QNAP deployment source-identity and artifact-identity defects discovered during live Slack HITL acceptance. QNAP deployment identity advances to 4.4.1 so the release has a distinct archive and extraction root. Candidate image tags are source-commit-qualified, only the application container is forcibly recreated, and post-deploy verification requires exact agreement among release metadata, running OCI revision, and governed MCP `source_commit`.

The production Compose topology, Secure MCP Tunnel network boundary, Slack secret mounts, TaskLedger authority, 10-agent roster, and L4/L5 approval rules are unchanged. Canonical MCP authority/runtime contract remains 4.0.0.

See `docs/release-v4.13.2-qnap-source-identity.md`.

# v4.13.1 QNAP Operator Documentation Alignment

This PATCH release corrects stale QNAP v4.3.0 operator references embedded in the v4.13.0 release bundle. Runtime Slack HITL behavior remains v4.13.0-equivalent. Canonical MCP authority/runtime contract remains 4.0.0 and QNAP deployment identity remains 4.4.0.

See `docs/release-v4.13.1-qnap-doc-sync.md`.

# v4.13.0 Bidirectional Slack HITL Peer Workflow

This MINOR release corrects the Slack HITL operator experience and message identity path. It adds governed non-approval interaction threads, same-thread acknowledgments after provider reread, explicit message intent, direct CHANGES detail support, and replay-safe conversational evidence while preserving the locator-only Work dispatcher and fail-closed approval boundary.

Canonical authority/runtime contract remains 4.0.0. QNAP deployment identity remains 4.4.0 and requires exact-source candidate promotion before production activation is claimed.

See `docs/release-v4.13.0-slack-hitl-peer.md`, `docs/security-review-v4.13.0-slack-hitl-peer.md`, and `docs/verification-v4.13.0-slack-hitl-peer.md`.

# v4.12.1 CoS Delegation and Agent Reporting

This PATCH release corrects the CoS delegation request contract and failure diagnostics without changing the 10-agent roster, authority contract 4.0.0, Commercial Growth OS decision logic, or external-action boundaries. Server-derived delegation fields are no longer required caller authority inputs, agent principals cannot be invoked as Skills, and explicit parent reconciliation is documented after owner completion.

The release includes a human-installable Chief of Staff Skill bundle and an exact-current-source QNAP 4.4.0 candidate bundle. Repository publication does not itself promote QNAP or update the installed ChatGPT Skill.

See `docs/release-v4.12.1-cos-delegation-reporting.md`, `docs/security-review-v4.12.1-cos-delegation-reporting.md`, and `docs/verification-v4.12.1-cos-delegation-reporting.md`.

# v4.12.0 Commercial Growth Cadence

This MINOR release integrates Commercial Growth monthly, quarterly, scheduled, ad hoc, and supported native-event execution into the existing TaskLedger-controlled Commercial Operations model. `LOOP-COM-001` remains the single scheduled dispatcher. A scheduler wake is never business progress. Quarterly review subsumes a colliding monthly review. Polling cannot claim native-event compliance. Existing `LOOP-COM-HITL-001`, Message Operations, Revenue Intelligence, GTM Orchestrator, CRO/COO/CFO boundaries, human approval, and completion-versus-verification controls remain unchanged.

The release packages only the materially changed `mesh-chief-of-staff` Skill. ChatGPT installation remains intentionally human controlled.

# v4.10.0 Outcome-Driven Orchestration

## v4.11.1 Commercial Growth OS Skill Package Closeout

This PATCH publishes the four complete ChatGPT Skill directories changed by v4.11.0 as a checksummed human-installable bundle. It changes packaging and release completeness only. The installed ChatGPT runtime remains a separate human-controlled synchronization step and must not be reported as upgraded until re-read confirms the released content.


## v4.11.0 Commercial Growth OS Integration

This release integrates the existing CoS universe with the Commercial Growth OS while preserving TaskLedger, Revenue Intelligence, the Phase 1 agent roster, L0-L5 decision rights, Message Operations, human approvals, and completion-versus-verification separation. Release evidence is in `docs/verification-v4.11.0-commercial-growth-os.md`.


`v4.10.0 Outcome-Driven Orchestration` adds ODD business-decision semantics and AI execution-economy controls to Chief of Staff, CMO, and AgentOps role Skills.

Canonical Phase 1 authority/runtime contract **4.0.0**, unchanged.  
Production QNAP **4.4.0**, unchanged.  
Registered organization: exactly 10 agents, unchanged.

The release adds no principal or external-action authority. It separates business outcome from technical health, requires explicit business decision classes for meaningful checkpoints, converts supported internal recommendations into owned action, preserves correct no-action, and uses progressive T0-T3 evidence loading to reduce unnecessary AI/provider cost.

See `docs/release-v4.10.0-odd-outcome-delivery.md`, `docs/security-review-v4.10.0-odd-outcome-delivery.md`, `docs/verification-v4.10.0-odd-outcome-delivery.md`, and `CHANGELOG-v4.10.0.md`.

# v4.9.1 Media OS Capability Registration

`v4.9.1 Media OS Capability Registration` reconciles and releases the approved Mesh Media Production OS registry integration.

Canonical Phase 1 authority/runtime contract **4.0.0**, unchanged.  
Production QNAP **4.4.0**, unchanged until governed current-source promotion.  
Registered organization: exactly 10 agents, unchanged.

CMO receives `mesh-media-production`, `mesh-media-verification`, and `mesh-media-distribution`. VP Content receives `mesh-media-production` only, remains L2 production execution, and retains zero delegation authority. Public publishing remains human-gated. Skills remain capabilities rather than principals, canonical sources, approval authorities, or autonomous external-action executors.

v4.9.1 fixes the stale v4.7-era direct-binding regression that rejected these approved additions after PR #77, retires the already-published v4.9.0 publisher to manual read-only verification, and becomes the sole active exact-SHA SemVer publisher after full verification.

The repository release and QNAP production state remain distinct. Canonical CI produces a current-source QNAP 4.4.0 candidate with exact commit provenance. Production Media OS activation requires that candidate to be promoted through the existing transactional QNAP deployment workflow and then independently read back through Secure MCP.

See `docs/release-v4.9.1-media-os-capability-registration.md`, `docs/security-review-v4.9.1-media-os-capability-registration.md`, `docs/verification-v4.9.1-media-os-capability-registration.md`, `docs/gap-audit-v4.9.1-media-os-capability-registration.md`, and `CHANGELOG-v4.9.1.md`.

# v4.9.0 Mesh OpEx Bot Shared Capability Integration

`v4.9.0 Mesh OpEx Bot Shared Capability Integration` is the prior published repository release. It added the external governed `mesh-opex-bot` capability to the COO without creating an eleventh agent or changing runtime authority.

Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged.  
Production QNAP deployment: `4.4.0`, unchanged.  
Registered organization: exactly 10 agents, unchanged.

The COO is the sole Phase 1 consumer. The shared Skill is advisory only, modifies no canonical facts, executes no external action, and uses `mesh.opex.request.v1` and `mesh.opex.handoff.v1`. COO retains delivery feasibility/capacity/staffing authority, CoS retains TaskLedger and work-graph orchestration, CFO retains financial truth, AgentOps retains agent-workforce health, and qualified humans retain regulated and consequential decisions.

v4.9.0 is preserved as historical read-only verification. v4.9.1 owns current publication authority.

# v4.8.4 Release Record Correction

`v4.8.4 Release Record Correction` is a historical documentation and release-control PATCH that corrected the v4.8.3 human-readable inventory to include v4.6.0, which the v4.8.3 implementation did retire, without rewriting the historical v4.8.3 tag or GitHub Release.

Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged.  
Production QNAP deployment: `4.4.0`, unchanged.  
Registered organization: exactly 10 agents, unchanged.

For compatibility with historical release assertions, the canonical Phase 1 authority/runtime contract **4.0.0** and production QNAP **4.4.0** remain the governing runtime boundaries.

## Release-record correction

The complete v4.8.3 implemented retirement inventory is v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.4.1, v4.4.2, v4.6.0, and v4.8.2. The prior v4.8.3 source/release record omitted v4.6.0 from that explicit list even though the workflow was correctly retired.

No ChatGPT Skill package changes in v4.8.4. The v4.8.2 ten-Skill bundle remains the manual update artifact.

# v4.8.3 Historical Publisher Retirement

`v4.8.3 Historical Publisher Retirement` is the prior release-control closeout PATCH for the v4.8.x audit remediation. Post-release verification of v4.8.2 found residual historical publisher capability. v4.8.3 converted v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.4.1, v4.4.2, v4.6.0, and v4.8.2 to read-only, manual-only historical verification and added a systemic regression protecting every already-published v4.x SemVer workflow through v4.8.2.

No ChatGPT Skill package changes were made in v4.8.3.

# v4.8.2 Functional Method Audit Remediation

`v4.8.2 Functional Method Audit Remediation` is the prior corrective PATCH for the v4.8.x audit findings. It added executable behavior-level evaluation gates across the existing 10 role Skill packages; ready BDD scenarios `FMR-001` through `FMR-018`; an exhaustive 49-candidate donor disposition ledger; explicit `BLOCKED_SOURCE_IDENTIFICATION` handling for the unresolved fourth donor; durable v4.8.1 release evidence; and its now-historical exact-SHA publisher.

It did not change the Python runtime version, MCP catalog, TaskLedger, Revenue Intelligence authority, agent roster/parentage, L4/L5 decision rights, external-action controls, credentials, OAuth, network boundaries, database schemas, shared PPMD/Messaging releases, or QNAP production deployment.

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

Historical release identity is preserved for regression and audit continuity. The canonical Phase 1 authority/runtime contract **4.0.0** remains the current authority contract, and production QNAP **4.4.0** remains current until a later deployment is explicitly verified.

# v4.3.0 Cross-Agent Owner Execution

Historical release identity `v4.3.0` is preserved. It established governed server-derived owner execution and nested child execution before later authority-closure and QNAP release trains. It does not override the current runtime or release state.

Historical release records remain immutable snapshots and do not override the current repository release, current authority contract, or live QNAP readback.
