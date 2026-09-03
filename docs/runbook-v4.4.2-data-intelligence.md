# Runbook v4.4.2: Data Intelligence Orchestration

## Runtime gate
Resolve current approved Mesh Chief of Staff and companion Skills by canonical name. Confirm bound agent `cos`, exactly 10 ACTIVE registry records with canonical parentage, required owner-execution and verification capabilities, idempotent task intake, and valid audit chain. Record active deployment and capability result as evidence. Do not pin execution to a fixed release.

A missing capability blocks only the affected job or external stage. Do not create Sheet COMPLETE or PASS as canonical truth.

## Select logical work
Read canonical MCP task graph, then TaskLedger operating mirrors: Control Plane, Operating Guide, Preflight, Run History, Prompt Archive, and the job canonical source. Use America/New_York. Process only the oldest outstanding `LOOP-DATA-001` occurrence unless its contract explicitly permits bounded catch-up. The monthly day-one 00:01 ET occurrence is an explicit schedule-window exception.

## Idempotency and state
Derive `<Job ID>:<logical due timestamp>` exactly. Call `task.intake` once with `accountable_agent=cos` and the execution key as `idempotency_key`. Call `task.get` and resume actual state. Check MCP, Run History, Prospect Run Ledger, connector, and provider state before mutation. Never replay passed states, terminal work, provider effects, or verified cell writes. Respect non-expired locks and leases.

## Functional ownership
For a CRO-owned job:
1. Reuse the CoS parent.
2. Reuse an existing deterministic child if present.
3. Otherwise decompose exactly one CRO child.
4. Set canonical `dependencies` only to real predecessor task IDs. Use an empty list when there is no hard predecessor.
5. Create or reuse one deterministic delegation.
6. Omit caller `permitted_actions` and `permitted_capabilities` unless each value is a literal subset of the registry record.
7. Run every child lifecycle, check-in, and completion operation through `mesh.cos.owner-execution.v2`.
8. Have CoS verify the child separately.

CMO and AgentOps follow the same direct-child pattern. VP Content is created only by CMO and executes through nested CMO delegation.

## Evaluate business state
Revenue Intelligence is authoritative for prospect universe, structural qualification, entity state, evidence coverage, queue state, fit, priority, and activation readiness. LinkedIn Authority OS evidence is optional labeled context for CMO and cannot overwrite Revenue Intelligence. Route ambiguous identity, taxonomy, duplicate, merger, acquisition, rebrand, hierarchy, ownership, or strategic state to Human Review. Apollo budget is 0.

## Monthly full-universe write path
Read Prospect Run Ledger first. Stop if another non-expired Active write run exists. Create one Active DECAY run only after all canonical and connector gates pass. Determine the complete populated universe at runtime and process rows in deterministic order. There is no arbitrary record or cell-change ceiling.

For every approved cell mutation, use the required single-cell transaction:
1. Pre-read one exact target cell.
2. Compare it with the decision expected value.
3. Write one exact cell only.
4. Immediately read back that cell.
5. Reconcile expected value, formula/validation behavior, and absence of unrelated changes.
6. Continue only after success.

After all approved fields for an account reconcile, read the governed row. Update Run ID, Last Reviewed Date, and Next Review Date through separate single-cell transactions, with review dates last.

Never archive, delete, auto-merge, strategically disqualify, activate outreach, populate contact fields, change schema, write CRM state, or take external commercial action.

## Stop and recovery
On connector safety or reconciliation failure: do not retry the blocked write; do not broaden the transaction or switch methods; do not proceed to later cells for that account; stop later prospect writes; preserve reconciled accounts; mark Partially Failed; record the exact account/cell/exception; release the lock; do not automatically roll back prior committed rows.

For malformed canonical metadata, preserve and isolate the original child. Create exactly one dependency-clean successor only after provider state proves no effect will be replayed. Do not call a missed full-universe occurrence complete.

## QA, completion, verification
After authorized evaluation, writes, and reconciliation are complete, move the accountable child from IN_PROGRESS to QA. The owner calls `task.complete` with a non-empty outcome and evidence. CoS then calls `task.verify` independently. Complete and verify the CoS parent only when its own acceptance test is satisfied. A recovery successor can be verified while the original missed occurrence remains cancelled and `FAILED_OCCURRENCE_ISOLATED`.

## Executive brief
Lead with business outcome, movement, evidence/confidence, decision/action, risks/unknowns, owner, and next due. Follow with technical health, canonical state, registry/audit, connector/lock state, reconciliation, defect/recovery, and human action. Use GREEN only when evaluated technical scope passes, DEGRADED for a contained defect with safe continuation, and FAILED when intended technical execution cannot be accepted.

## Release and rollback
Repository and TaskLedger control changes pass full CI, targeted security review, independent verification, PR review, merge to `main`, semantic tag, and GitHub Release. A live scheduler activation is accepted only with provider readback. If the operating prompt or TaskLedger configuration is unsafe, pause the external wake, preserve evidence, restore the prior prompt contract, and investigate. Do not restart or patch the healthy QNAP runtime for caller metadata, mirror, or scheduler defects.
