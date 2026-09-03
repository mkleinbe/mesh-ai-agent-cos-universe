# v4.4.1 Commercial Operations Orchestration

`v4.4.1` is the current repository release candidate. It corrects Commercial Operations caller/work-package construction, central scheduler drift, bounded recovery, CMO/VP Content composition, and business-first executive reporting without changing the Mesh CoS MCP runtime binary.

The canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**. The production QNAP deployment remains **4.4.0**. This release preserves exactly 10 registered agents and does not change the Phase 1 roster.

## Root cause and correction

The blocked commercial occurrences contained descriptive prerequisite text in canonical dependency arrays. Mesh CoS MCP 4.4.0 correctly treated those values as canonical predecessor task IDs and correctly blocked `IN_PROGRESS` when they could not be resolved.

v4.4.1 keeps the fail-closed runtime gate and corrects the orchestration boundary:

- dependency arrays contain only real canonical predecessor task IDs;
- narrative prerequisites move to job contracts, acceptance tests, constraints, trigger conditions, evidence, or operating mirrors;
- legacy malformed tasks remain preserved as audit history;
- one deterministic dependency-clean successor may be used when provider state proves recovery is safe;
- no provider side effect is replayed;
- direct and nested owner execution continue through registry-valid delegation;
- business disposition and technical health are reported separately.

## Operating changes

- Restored the Commercial Operations Scheduled Task to active weekday wakes at 08:00, 10:00, 12:00, and 16:00 America/New_York.
- Preserved TaskLedger logical due times as the actual execution identity and eligibility basis.
- Kept `COM-EMAIL-SEND-DLY-001` event-driven under `LOOP-COM-HITL-001`.
- Formalized CMO and VP Content participation for authority/content context without transferring Revenue Intelligence commercial-truth authority.
- Added bounded self-healing and executive run-brief controls to the durable TaskLedger Operating Guide.

## Compatibility and production disposition

- Canonical runtime contract: `4.0.0`
- Production QNAP deployment: `4.4.0`
- Repository release: `v4.4.1`
- Registered agents: exactly 10
- MCP machine action surface: unchanged
- Database/schema migration: none
- QNAP image/container change: none
- QNAP operator action: none
- Provider credentials/Slack trust boundary: unchanged
- External-action authority: unchanged

No QNAP deployment is part of this release. The live Mesh CoS MCP 4.4.0 runtime remains production.

## Verification gates

The candidate is releasable only when:

1. Existing full repository CI passes.
2. The v4.4.1 Commercial Operations regression suite passes.
3. Live Mesh CoS MCP identity, exact 10-agent registry, delegated owner execution, separate verification, and audit-chain validation pass.
4. Recovered banking and Gmail-response occurrences are canonical and VERIFIED without provider replay.
5. CMO and nested VP Content Commercial Operations tasks are VERIFIED.
6. TaskLedger Operating Guide, Preflight, Tests, Operating Loops, and Run History are reconciled.
7. The Commercial Operations Scheduled Task is enabled with the declared schedule and current prompt contract.
8. No unauthorized external action occurred.
9. Independent verification is recorded against the final pull-request/main SHA.

## Release lifecycle

After all pull-request checks are green:

1. Merge the verified branch to `main`.
2. The v4.4.1 release workflow re-runs the release verification job on the merged main SHA.
3. Only after that verification succeeds, the workflow creates semantic tag `v4.4.1` and the immutable GitHub Release from that exact main SHA.
4. Confirm `main`, the tag, GitHub Release, release notes, and canonical TaskLedger evidence identify the same intended repository release.

## Rollback

If the orchestration configuration produces incorrect routing, disable the Commercial Operations Scheduled Task, preserve canonical MCP and provider evidence, restore the prior prompt from the TaskLedger Prompt Archive, and investigate the caller/control-plane contract.

Do not roll back or restart the healthy QNAP runtime for an orchestration-only defect.

---

# v4.4.0 Authority Closure

Historical release identity is preserved for regression and audit continuity. For that release-train point, the canonical Phase 1 authority/runtime contract remains **4.0.0**, and the then-current production deployment was `v4.3.0`. The historical v4.4.0 release documents, workflows, security evidence, and v4.3.x release-train artifacts remain retained. This historical section does not override the current v4.4.1 repository release candidate or the current QNAP 4.4.0 production deployment.
