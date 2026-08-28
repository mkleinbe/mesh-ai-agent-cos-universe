# Mesh CoS MCP v4.3.0 Cross-Agent Owner Execution Security Review

- Review class: `FULL_REVIEW`
- Scope: PF-057 systemic delegation remediation
- Canonical authority/runtime contract: `4.0.0`
- Candidate deployment release: `4.3.0`
- Production predecessor: `4.2.3`
- Canonical state: `TaskLedger`
- Human release authority: retained

## Executive security conclusion

PF-057 exposed an authority-transport gap: delegation could establish canonical ownership without establishing a governed execution path under the new owner's identity. The remediation introduces a server-owned, delegation-bound execution boundary. That boundary derives the acting owner from canonical TaskLedger and Agent Registry state, re-authorizes every requested tool against the derived owner's allowlist, scopes execution to the canonical task/delegation relationship, and records both expected and actual execution identity.

The design does not permit the scheduler, CoS, prompt content, task content, retrieved data, model output, connector data, or caller arguments to select an arbitrary acting principal. Delegation transfers bounded work authority only. Identity remains immutable.

The final authority-diff review also applies least privilege to nested execution. In the current 10-agent registry, only CMO and COO have registered ACTIVE children, so only those functional agents receive `delegation.execute_owner` plus `task.decompose` for nested child execution. CRO retains its pre-existing bounded `delegation.create` surface but receives no child executor/decompose grant; CFO receives no child executor/decompose grant. Future child registration requires a separate governed registry and allowlist change.

Security disposition is `PASS_CANDIDATE` only when the exact release candidate passes the full repository, security, packaging, container, and modern MCP verification gates. The exact revision is bound by the successful CI run's `GITHUB_SHA` and the release bundle's `release-metadata.txt`; this document intentionally does not hard-code a self-referential commit hash. Production deployment and recovery remain human-authorized operations.

## Security invariants

1. The authoritative operation actor must possess the canonical identity and authority required for the operation.
2. `TaskLedger` remains canonical operating state.
3. The Agent Registry remains canonical for parentage, health, delegation depth, role authority, required approvals, permitted actions, and prohibited actions.
4. The external runtime principal remains immutable.
5. The caller cannot supply an arbitrary execution principal.
6. Parent agents cannot directly complete child-owned work.
7. Child agents do not inherit parent-only authority.
8. Human-only tools remain inaccessible to every agent execution path.
9. Approval requirements survive permitted delegation.
10. `COMPLETED != VERIFIED`.
11. Repeated execution is request-bound and idempotent.
12. Untrusted model or retrieved content is never authentication or authorization evidence.
13. Nested child-executor authority is exposed only where the live registry contains an ACTIVE canonical child and the parent is permitted to delegate.

## Authority derivation

The server-owned owner executor resolves authority as:

```text
delegation_id
-> canonical delegation record
-> canonical task_id
-> canonical accountable_owner
-> canonical Agent Registry record
-> owner MCP allowlist
-> task-scoped arguments
-> authorized operation
```

The caller supplies the operation request, task/delegation locators, and an idempotency key. The caller does not supply the acting owner. Any owner-like field outside the closed request schema is rejected.

## Threat model and disposition

| Threat | Control | Disposition |
| --- | --- | --- |
| Agent impersonation | Owner identity is derived server-side from canonical delegation/task state; direct owner substitution is rejected. | Mitigated |
| Confused deputy | Delegator identity, canonical parent task, child task, owner, lineage, and task scope are checked before dispatch. | Mitigated |
| Owner-ID tampering | No owner field exists in the public executor request schema; canonical owner is read from TaskLedger/delegation. | Mitigated |
| Caller-supplied principal escalation | External runtime identity is process-bound; executor cannot accept a caller-selected principal. | Mitigated |
| Forged delegation | Executor requires an existing canonical delegation record whose delegator matches the authenticated caller. | Mitigated |
| Stale delegation | Canonical task owner and delegation owner must still agree at execution time. | Mitigated |
| Replay | Request fingerprint binds delegation, task, operation, and arguments to the idempotency key. | Mitigated |
| Cross-task authority reuse | Task-scoping rejects operations outside the canonical delegated task and nested descendant relationship. | Mitigated |
| Task-ID substitution | Executor task_id must equal the canonical delegation task_id. | Mitigated |
| Authorization bypass | Derived owner is re-authorized against the deny-by-default MCP policy on every operation. | Mitigated |
| Approval bypass | Approval gates are inherited and unioned with target-owner requirements; human-only approval recording is excluded. | Mitigated |
| Delegation-depth bypass | Parentage and canonical depth are derived from the live registry; client depth/ancestry hints must match canonical state. | Mitigated |
| Privilege inheritance | Child execution uses only the child's registry and MCP policy, not the parent's tool surface. | Mitigated |
| Excessive capability exposure | Owner lifecycle is available to accountable owners; nested child-executor/decompose authority is restricted to current registered parent-child routes. | Mitigated |
| Functional source-authority leakage | Role-specific capabilities and source authority remain attached to the derived owner contract. | Mitigated |
| Disabled/quarantined agent execution | Owner must be ACTIVE and routable before delegation persists and again before execution. | Mitigated |
| Completion without evidence | Existing lifecycle requires non-empty outcome, acceptance test, and outcome evidence. | Mitigated |
| Fraudulent audit attribution | Lifecycle actor is explicitly passed as the authenticated/derived owner and owner-execution audit records identify orchestrator, owner, and executing principal separately. | Mitigated |
| Completion/verification conflation | `task.complete` reaches `COMPLETED`; `task.verify` remains separate and explicitly allowlisted. | Mitigated |
| Prompt-driven identity changes | Closed schemas and immutable runtime identity treat prompt/task/retrieved/model content as data only. | Mitigated |
| Malicious retrieved content | Retrieved content cannot alter registry, task owner, runtime principal, allowlist, or approval state. | Mitigated |
| Concurrent execution race | Canonical idempotent claim plus request fingerprint prevents duplicate execution through the same request key. | Mitigated |
| Duplicate completion | Lifecycle state and owner-execution idempotency prevent a second canonical completion effect. | Mitigated |
| Orphaned delegated tasks | Delegation creation fails closed unless the owner is currently routable and has the validated lifecycle path. | Mitigated |
| Cyclic delegation | Direct-child registry constraint plus canonical lineage and existing circularity validation reject cycles. | Mitigated |
| Human authority fabrication | `approval.record_decision` and reliability override remain human-principal-only and cannot be invoked through owner execution. | Mitigated |
| Schema-registry substitution | MCP policy validates the declared schema registry fail-closed and validates schema safety before catalog completeness. | Mitigated |

## Idempotency and ambiguous failures

Owner execution persists an at-most-once claim before the owner operation runs. A successful request can be replayed only with the same idempotency key and exact request fingerprint, in which case the canonical cached response is returned.

A key reused with different task, delegation, operation, or arguments is rejected. If execution fails after the claim and the external effect could be ambiguous, the executor does not blindly retry. The failure remains explicit for governed remediation. This prevents a recovery mechanism from duplicating consequential effects.

## Approval inheritance

Delegation approval gates are the union of:

- inherited canonical parent delegation gates;
- explicitly retained gates on the child delegation;
- target-owner registry `required_approvals`.

A caller cannot remove inherited approvals. Message Operations remains separately constrained by approved-artifact and human-approval requirements. The owner executor is transport, not approval authority.

## Runtime availability and failure handling

Before delegation persistence and again before owner execution, the owner must be ACTIVE and routable. Failures are classified and recorded with:

- canonical task;
- parent task;
- delegation;
- orchestrator;
- accountable owner;
- executing principal;
- expected principal;
- task state;
- attempted operation;
- authorization result;
- failure classification;
- retry eligibility;
- remediation path.

The remediation never substitutes another agent to make progress.

## Security tests

The release candidate includes explicit negative coverage for:

- direct CoS completion of a child task;
- arbitrary owner fields;
- cross-sibling delegation execution;
- task-ID and delegation-ID mismatch;
- owner-route tampering;
- owner change after delegation;
- unavailable and quarantined owners;
- zero-depth delegation attempts;
- permitted-action elevation;
- parent authority/depth/ancestry/active-owner tampering;
- human-only operation invocation;
- functional capability leakage;
- idempotency-key reuse with changed payload;
- concurrent claim behavior;
- malformed and substituted schema registries;
- nested delegation relationship tampering;
- cross-task Skill and decomposition attempts;
- completion/verification separation;
- approval inheritance;
- dependency release ordering;
- registry-driven nested authority requiring an actual registered ACTIVE child.

## Residual risk

1. The server-owned executor becomes a high-value internal authority boundary. Continued schema, policy, audit, and idempotency testing is mandatory.
2. Availability of a functional owner runtime can still block work. The required behavior is explicit fail-closed state and governed recovery, not identity substitution.
3. Production TaskLedger may contain pre-remediation delegated work without an owner-execution-route record. Recovery must derive and validate a route from canonical existing task/delegation state rather than recreate the task.
4. Production acceptance must use non-consequential synthetic work before recovering real blocked tasks.
5. Codex Security scan evidence is not claimed unless separately produced by that environment; repository security evidence consists of the FULL_REVIEW threat analysis, negative tests, Bandit, npm audit/security checks, schema-policy checks, release controls, and independent final diff review.

No residual security finding authorizes widening agent, human, source, approval, commercial, publishing, staffing, pricing, or release authority.

## Release gate

Security approval requires all of the following on the exact candidate commit:

- all Python tests pass with 100% branch-aware coverage;
- TypeScript MCP build/test/smoke/security passes;
- npm audit has no high-severity blocker;
- Bandit passes at the repository-defined threshold;
- registry-driven owner readiness passes for every eligible ACTIVE downstream owner;
- direct-report and nested delegation behavior passes;
- QNAP POSIX regressions pass;
- deterministic candidate bundle and checksum pass;
- production container provenance checks pass;
- modern MCP discovery/sequential transport checks pass;
- final diff review finds no unintended authority expansion.

Production remains unchanged until human release authorization.
