# Security Review: v4.4.0 Authority Closure

## Classification

Security applicability: **FULL_REVIEW**.

Reason: this change materially modifies MCP authorization, human approval resolution, agent identity, nested delegation, consequential-action gating, persistence/audit behavior, CI/release controls, and ChatGPT publication contracts.

## Trust boundaries reviewed

- ChatGPT Workspace model/Skill reasoning boundary
- Mesh CoS MCP public tool surface
- Python MCP runtime authorization boundary
- Canonical TaskLedger persistence boundary
- Registry and agent allowlists
- Delegation and nested-delegation routes
- Human approval records and Slack HITL reconciliation
- Message Operations consequential-write boundary
- QNAP container/runtime boundary
- Secure MCP Tunnel
- GitHub CI, artifact, and release provenance
- ChatGPT workspace publication snapshot

## Security properties

### SEC-440-001 Canonical principal derivation
Delegated execution principal must be derived from canonical task/delegation state. Request data cannot select the child owner.

Status: PASS in source and tests.

### SEC-440-002 Canonical L4/L5 approval
L4/L5 operations must resolve an APPROVED canonical TaskLedger approval for the exact task and required action. Approval owner and decision actor must match. L5 must resolve to Michael.

Status: PASS in source and tests.

### SEC-440-003 Delegation capability intersection
A delegated owner may invoke a Skill capability only when it is both registered for that owner and explicitly included in the delegation's `permitted_capabilities`.

Status: PASS. Rejected capability attempts produce a canonical failed owner-execution receipt.

### SEC-440-004 Nested authority containment
Nested owner execution must descend from the current canonical delegated task and from the registered parent-child relationship. Cross-task reads/writes and unrelated registry reads must fail closed.

Status: PASS in source and targeted regression tests.

### SEC-440-005 Human/verifier separation
Human-only tools and `task.verify` must not be reachable through delegated owner execution. `COMPLETED` must not imply `VERIFIED`.

Status: PASS.

### SEC-440-006 Logical Skill-agent provenance
A Skill handoff must not claim that a separate Workspace Agent process executed. Execution mode and result provenance must identify the logical Skill-agent boundary.

Status: PASS in source contract.

### SEC-440-007 Publication snapshot integrity
Production publication acceptance requires exact action-name and input-schema equality against the actual ChatGPT workspace snapshot. Source-only validation must not report publication PASS.

Status: PASS in source tooling; **external workspace acceptance remains a human publication gate** until an actual snapshot is supplied.

### SEC-440-008 Runtime provenance
Operators must be able to distinguish runtime contract, deployment release, source commit, and action/schema publication digest.

Status: PASS in source. Production observation requires deployment of the v4.4.0 image.

## Review evidence

- TypeScript build and MCP tests
- npm high-severity audit
- Python contract validation
- runtime/documentation drift checks
- 10-agent package/allowlist checks
- owner-execution readiness checks
- capability-closure checks
- published action/schema source-contract checks
- Ruff and mypy
- pytest with 100% branch-aware coverage required
- Bandit high-severity scan
- QNAP POSIX shell regression suite
- production-equivalent container build
- modern MCP transport discovery/sequential-call test
- immutable candidate artifact and checksum generation

## Findings

### SEC-440-F01 Caller-trusted approval metadata
Severity: Critical authorization defect in pre-v4.4 behavior.

Remediation: canonical approval resolution implemented. Caller-provided approval metadata is corroborative only and must match canonical evidence.

Retest: required and covered.

### SEC-440-F02 Delegated role capability overreach
Severity: High.

Remediation: canonical `permitted_capabilities` intersection and nested-scope enforcement.

Retest: required and covered.

### SEC-440-F03 Rejected delegated capability lacked durable execution receipt
Severity: Medium auditability defect.

Remediation: capability authorization is evaluated inside the claimed owner-execution transaction so failure state and route receipts are preserved.

Retest: required and covered.

### SEC-440-F04 Workspace publication drift can survive server updates
Severity: High operational/governance risk.

Remediation: exact action+schema attestation and source-only non-PASS state. Remaining workspace refresh/publish step is outside this repository's authority.

Retest: required after human workspace publication.

## Residual risk

- The source cannot prove the frozen ChatGPT workspace snapshot until an administrator refreshes/recreates and publishes the app and supplies the resulting action+schema snapshot.
- The current QNAP production deployment remains on its existing release until a human deploys the v4.4.0 artifact. Source and candidate-container verification do not constitute production deployment verification.
- External provider behavior for Slack/Gmail remains subject to provider availability and credentials, but consequential action remains fail-closed behind canonical approval.

## Disposition

**SOURCE/RELEASE-CANDIDATE SECURITY: PASS when final exact-tree CI and independent verification are green.**

**PRODUCTION/WORKSPACE SECURITY ACCEPTANCE: BLOCKED on the explicitly human-controlled deployment and ChatGPT publication steps.**
