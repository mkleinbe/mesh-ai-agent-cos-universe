# Independent Verification: v4.3.0 Cross-Agent Owner Execution

## Independence boundary

Verification is evaluated against the accepted BDD scenarios, canonical Agent Registry, MCP policy, TaskLedger behavior, repository tests, release artifact, and final diff. Implementation convenience is not an acceptance criterion.

## Required acceptance evidence

| Verification area | Required evidence |
| --- | --- |
| PF-057 causal resolution | CoS-bound orchestration can route owner completion without impersonation |
| Direct reports | Registry-driven matrix for every current eligible CoS direct report |
| Nested delegation | `cmo -> vp-content` and `coo -> consultant-network-steward` |
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
| Registry future safety | ACTIVE owner-eligible agent without execution path fails readiness |
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

## Verification verdict rule

`PASS` requires all exact-candidate CI and release gates green, zero unresolved CRITICAL/HIGH security finding, no unintended authority expansion in the final diff, and no accepted behavior weakened to obtain test success.

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
