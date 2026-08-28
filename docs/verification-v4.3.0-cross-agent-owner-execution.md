# Independent Verification: v4.3.0 Cross-Agent Owner Execution

## Independence boundary

Verification is evaluated against the accepted BDD scenarios, canonical Agent Registry, MCP policy, TaskLedger behavior, repository tests, release artifact, security review, and final authority diff. Implementation convenience is not an acceptance criterion.

The exact candidate revision is bound by the successful final CI run's `GITHUB_SHA`, the QNAP release bundle's `release-metadata.txt`, and OCI revision label. This document intentionally does not hard-code a commit hash that would become stale when the receipt itself is committed.

## Required acceptance evidence

| Verification area | Required evidence |
| --- | --- |
| PF-057 causal resolution | CoS-bound orchestration can route owner completion without impersonation |
| Direct reports | Registry-driven matrix for every ACTIVE downstream owner |
| Nested delegation | `cmo -> vp-content` and `coo -> consultant-network-steward` |
| Nested least privilege | Child executor/decompose exposed only to parents with registered ACTIVE children |
| Zero-depth agents | Further delegation denied |
| Functional isolation | Owner receives only owner-authorized capability surface |
| Parent impersonation | Direct parent child-completion attempt denied |
| Child impersonation | Child cannot invoke parent-only authority |
| Audit identity | Lifecycle and owner-execution evidence name the actual owner/executing principal |
| Retry/idempotency | Exact retry reused; changed payload under same key denied |
| Dependencies | Predecessor release follows canonical state exactly once |
| Completion vs verification | `COMPLETED` and `VERIFIED` remain distinct |
| Approval inheritance | Nested work retains inherited and target-owner gates |
| Runtime unavailability | Fail-closed routing diagnosis with recoverable canonical state |
| Scheduled execution | Scheduled CoS trigger traverses owner boundary and resumes idempotently |
| Registry future safety | ACTIVE downstream owner without execution path fails readiness |
| TaskLedger | Canonical state remains authoritative |
| Nondelegated regression | Existing CoS-owned workflows continue to pass |
| Security | FULL_REVIEW has no unresolved blocking finding |
| Release integrity | Exact candidate package, OCI provenance, QNAP and modern MCP checks pass |

## Scenario traceability

- DLG-001: CoS-owned completion
- DLG-002: registry-driven CoS direct-report matrix
- DLG-003: CMO to VP Content
- DLG-004: COO to Consultant Network Steward
- DLG-005: zero-depth delegation denial
- DLG-006: owner substitution denial
- DLG-007: functional authority isolation
- DLG-008: owner completion attribution
- DLG-009: parent direct completion denial
- DLG-010: completion/verification separation
- DLG-011: idempotent retry
- DLG-012: owner runtime unavailable
- DLG-013: disabled/quarantined owner
- DLG-014: approval inheritance
- DLG-015: Message Operations consequential boundary
- DLG-016: dependency release
- DLG-017: nested return path

## Final authority-diff rule

The release may expand authority only where PF-057 requires transport or owner-lifecycle capability:

- CoS: one new server-owned `delegation.execute_owner` transport operation;
- every downstream accountable owner: only the lifecycle tools needed to operate and complete its own canonical work;
- CMO and COO: nested child execution/decomposition because the current registry contains VP Content and Consultant Network Steward beneath them;
- CRO and CFO: no new child executor/decompose authority because the current registry contains no child beneath them;
- all agents: no human-only approval or reliability override authority;
- non-verifier agents: no `task.verify` authority.

Any broader change is a verification defect even if tests pass.

## Verification verdict rule

`PASS` requires all exact-candidate CI and release gates green, zero unresolved CRITICAL/HIGH security finding, no unintended authority expansion in the final diff, and no accepted behavior weakened to obtain test success.

A successful CI run is necessary but not sufficient. The independent verifier must also confirm requirement/spec/code/security drift is absent on the same candidate revision. The final conversation/report records the exact candidate SHA and successful run ID after those checks complete.

`PASS` does not authorize production deployment. Deployment and stranded-task recovery remain human-authorized operations.

## Production verification sequence after deployment

1. verify dual release identity `4.0.0 / 4.3.0`;
2. verify 10-agent registry and 28-tool CoS catalog;
3. verify audit chain;
4. run one non-consequential direct delegation per eligible functional owner;
5. run both permitted nested delegation paths using synthetic work;
6. run scheduled cross-agent resume/idempotency validation;
7. confirm no unauthorized external action occurred;
8. build the final stranded-task recovery inventory;
9. re-read `task-b0b613daff51` before recovery;
10. recover only tasks whose current canonical state still matches the governed recovery criteria.

## Candidate disposition

Until the exact final CI run and final diff are both green, disposition remains `PENDING_EXACT_CANDIDATE_EVIDENCE`. Once both pass, the verifier may record `PASS / VERIFIED_CANDIDATE` without implying production acceptance.
