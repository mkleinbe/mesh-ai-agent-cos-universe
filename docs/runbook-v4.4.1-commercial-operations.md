# Runbook: v4.4.1 Commercial Operations Orchestration

## Scope

Use this runbook for Commercial Operations dispatcher defects, schedule drift, malformed task dependencies, owner-routing issues, and business-versus-technical reporting defects. Do not use it as authority to modify the QNAP runtime.

QNAP changes are operator-proxied through Michael. The current v4.4.1 correction requires no QNAP action because Mesh CoS MCP 4.4.0 is healthy and the root cause is caller-constructed work metadata.

## Preflight

Before governed repair:

1. Resolve the current approved Mesh CoS deployment by canonical name.
2. Verify bound agent `cos`.
3. Verify exactly 10 ACTIVE registered agents and canonical parentage.
4. Verify `governance.verify_audit_chain` is valid.
5. Read the affected canonical task, parent, child, delegation, and audit evidence.
6. Read the TaskLedger Control Plane, Operating Guide, Preflight, Run History, Commercial Platform, and job Canonical Source.
7. Reconcile the live Scheduled Task state with `CoS - Operating Loops`.
8. Reconcile provider state before any recovery that could duplicate an external side effect.

If runtime identity, registry, or audit integrity fails, block consequential work and treat that as a platform defect. Do not use this runbook to bypass a runtime gate.

## Diagnose a dependency failure

A `dependency_unavailable` or `Task dependencies are not verified` error is not enough to conclude the runtime is defective.

Inspect every child dependency:

- If the value is a real canonical task ID, preserve it. The predecessor gate must remain fail-closed until the predecessor satisfies the lifecycle contract.
- If the value is narrative text, a source label, provider prerequisite, or evidence description, classify it as caller-construction defect.
- If mixed valid and invalid entries exist, preserve valid canonical predecessor IDs and remove the invalid narrative requirements from successor construction. Do not rewrite historical task records into success.

## Recover a malformed occurrence

Recover only when the defect is deterministic and provider state proves that no consequential side effect requires replay.

1. Preserve the original parent, execution key, malformed child, delegation, and audit trail.
2. Isolate/cancel the malformed child through the current canonical lifecycle where supported.
3. Build one successor work package with no narrative dependencies.
4. Use only real canonical predecessor task IDs when a hard predecessor exists.
5. Keep the same CoS parent, accountable owner, authority level, acceptance boundary, prohibited actions, and inherited approval gates.
6. Create/reuse one deterministic delegation.
7. Execute child lifecycle only through `delegation.execute_owner`.
8. Have the accountable owner complete after QA.
9. Have CoS verify separately from completion.
10. Complete/verify the CoS parent only after the successor result is reconciled.
11. Mirror the final state to Google TaskLedger and record the supersession/recovery evidence.

Never replay Gmail send, Slack approval, LinkedIn publication, CRM write, or other provider mutation as part of metadata recovery.

## Reconcile scheduler drift

When TaskLedger says `LOOP-COM-001` is active but the Scheduled Task is disabled or has the wrong cadence:

1. Compare automation ID, title, enabled state, time zone, and schedule to `CoS - Operating Loops` and Control Plane.
2. Preserve the automation ID.
3. Update only the expected schedule/prompt/enabled state.
4. Read back the Scheduled Task state.
5. Update Operating Loops, Preflight, Tests, and Run History with the readback evidence.

The expected Commercial Operations wake is weekdays 08:00, 10:00, 12:00, and 16:00 ET. Logical due timestamps remain authoritative.

## QNAP decision rule

Do not request or perform a QNAP deployment when all of these are true:

- bound-agent identity passes;
- registry and parentage pass;
- audit-chain validation passes;
- owner execution works through the current deployment;
- completion and verification remain separate;
- the observed defect is reproducible from caller-supplied work metadata or scheduler state.

Escalate a QNAP change only if evidence proves a runtime defect that cannot be corrected at the caller/control-plane boundary. Any such change requires a separate engineering plan, release evidence, rollback, and user-proxied QNAP operator steps.

## Rollback

For a bad orchestration configuration:

1. Disable the Commercial Operations Scheduled Task.
2. Preserve canonical MCP tasks, approvals, audit events, provider receipts, and Google Run History.
3. Restore the previous prompt from `CoS - Automation Prompt Archive`.
4. Restore the prior expected schedule if schedule configuration caused the defect.
5. Do not roll back or restart QNAP for an orchestration-only defect.
6. Re-run harmless MCP identity/registry/audit checks before re-enabling.
