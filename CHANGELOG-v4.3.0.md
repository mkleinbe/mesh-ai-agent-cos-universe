# Mesh CoS MCP v4.3.0

## Cross-Agent Owner Execution Architecture

Deployment release `4.3.0` repairs PF-057 as a systemic delegation defect. Canonical Phase 1 authority/runtime contract remains `4.0.0`.

### Root cause

Prior delegation persisted accountable ownership without establishing an executable authenticated owner path. A CoS-bound scheduled runtime could therefore orchestrate child work to QA but could not legitimately complete work owned by CMO or another functional owner.

### Architecture

- Added governed MCP tool `delegation.execute_owner`.
- Owner identity is derived server-side from canonical delegation/task state and the Agent Registry.
- Caller-supplied principal selection is not supported.
- Parent agents cannot directly complete child-owned work.
- Owner lifecycle audit attribution records the actual owner rather than hard-coded CoS.
- Delegation creation now requires a routable target owner and validated lifecycle path.
- Registry-derived depth, lineage, authority, permitted actions, prohibited actions, and approval gates are enforced.
- Nested delegation uses the same protocol for `cmo -> vp-content` and `coo -> consultant-network-steward`.
- Future eligible agents use the same registry-driven route without new owner-specific plumbing.

### Reliability and observability

- Added owner execution route and owner execution canonical records.
- Added request-bound idempotency fingerprints and at-most-once execution claims.
- Successful exact retries return the canonical prior response.
- Changed requests under the same idempotency key fail closed.
- Ambiguous failed executions are not blindly replayed.
- Owner-routing failures record task, parent, delegation, orchestrator, owner, expected/actual principal, state, operation, authorization result, failure classification, retry eligibility, and remediation path.

### Security

- Full security review required for the new high-value authority boundary.
- Human-only operations remain inaccessible to all agent paths.
- Approval inheritance is preserved through nested delegation.
- Closed MCP schemas reject arbitrary owner/principal fields.
- MCP policy now validates the declared schema registry fail-closed and validates schema safety before catalog completeness.
- Cross-task, cross-sibling, owner-route tampering, depth/authority tampering, disabled/quarantined owner, concurrent claim, and capability-isolation tests added.

### Production readiness

- Added mandatory registry-driven owner readiness gate.
- Every ACTIVE downstream owner eligible for delegated work must have a validated owner lifecycle path.
- Added registry-driven CoS direct-report delegation test matrix.
- Added nested delegation acceptance tests.
- Added scheduled CoS cross-agent execution and idempotent-resume test.
- `COMPLETED != VERIFIED` remains unchanged.

### Least privilege

- CMO retains nested executor/decompose capability only for registered child VP Content.
- COO retains nested executor/decompose capability only for registered child Consultant Network Steward.
- CRO and CFO do not receive nested executor/decompose capability because the current registry has no ACTIVE child under those owners.
- CI now fails if nested execution authority is exposed to an agent without a registered ACTIVE child.

### Updated ChatGPT Skills

Role contracts changed for:

- `mesh-chief-of-staff`
- `mesh-agentops-controller`
- `mesh-answer-decision-desk`
- `mesh-cro`
- `mesh-cfo`
- `mesh-coo`
- `mesh-cmo`
- `mesh-message-operations`

Workspace-agent manifests changed for `cos`, `agentops`, `answer-desk`, `cro`, `cfo`, `coo`, `cmo`, and `message-ops`.

VP Content and Consultant Network Steward participate in the nested runtime path but their Skill role-contract files were not modified in this release.

### Material-turn documentation

- Added `docs/material-turn-documentation-standard.md` to codify durable documentation requirements for future material application turns.
- Added `docs/material-turn-v4.3.0.md` as the complete v4.3.0 architecture, security, migration, recovery, verification, and release record.
- Added `docs/skills-v4.3.0.md` as the v4.3.0 Skill update manifest.
- Added validated Mermaid architecture and delegated-execution sequence diagrams to the durable material-turn/release records.
- Updated `README.md` and `RELEASE.md` to point to the material-turn record and Skill manifest.

### Release governance

- v4.3.0 release publication is bound to the verified integrated `main` commit.
- Historical v4.2.3 release workflow is retained as manual-only release history and no longer runs on current PRs or `main` pushes.
- Repository merge/tag/release authorization for this turn was explicitly granted by the human release authority on August 28, 2026.
- Production QNAP deployment, canonical task recovery, and consequential external business actions remain separate authorization boundaries.

### Production recovery

Blocked canonical tasks must be resumed, not recreated by default. `task-b0b613daff51` remains an existing CMO-owned QA task and is recovered only after authorized deployment through canonical CMO completion followed by separate verification and dependency release.

### Authority boundary

No new L4/L5 authority, human approval authority, pricing authority, commercial commitment authority, staffing authority, public publishing authority, or verification authority is introduced. The new MCP operation is a governed identity-aware transport for authority already held by registered accountable owners.
