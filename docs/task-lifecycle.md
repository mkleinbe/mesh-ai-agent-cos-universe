# Task and Outcome Lifecycle

The Phase 1 state machine is enforced in code. Tasks are managed to verified business outcome, not artifact production.

## Required task framing

Before execution, a task should identify:

- objective
- expected business outcome
- accountable owner
- contributors
- decision owner
- deadline/decision date when applicable
- deliverable contract
- success measures
- evidence requirements
- dependencies
- authority boundary
- approval requirements
- verification method / acceptance test

## Primary progression

```text
INTAKE
  -> TRIAGED
  -> PLANNED
  -> ASSIGNED
  -> IN_PROGRESS
```

From `IN_PROGRESS`, a task may move to:

- `BLOCKED`
- `AWAITING_INPUT`
- `AWAITING_APPROVAL`
- `QA`
- `CANCELLED`

From `QA`, a task may move to:

- `REWORK`
- `READY_FOR_DECISION`
- `READY_FOR_ACTION`
- `COMPLETED`

Final progression:

```text
COMPLETED -> VERIFIED -> CLOSED
```

A failed completion/verification attempt returns the task to `REWORK` or `IN_PROGRESS` as appropriate.

## State definitions

### INTAKE
Request received but not classified.

### TRIAGED
Objective, urgency, authority, and primary owner identified.

### PLANNED
Dependencies, work packages, success criteria, approval gates, and acceptance conditions identified.

### ASSIGNED
The accountable agent has accepted responsibility.

### IN_PROGRESS
Execution is underway.

### BLOCKED
Progress cannot continue because of a named dependency or blocker.

### AWAITING_INPUT
Required evidence or information is missing.

### AWAITING_APPROVAL
The work is prepared but cannot proceed without required human approval.

### QA
The output/action is being checked against evidence, governance, and acceptance criteria.

### REWORK
Acceptance criteria failed and remediation is required.

### READY_FOR_DECISION
Preparation is complete and the decision owner must choose.

### READY_FOR_ACTION
The required decision/approval is complete and the action is prepared for execution.

### COMPLETED
The executing agent believes its assigned work is finished. This is not outcome verification.

### VERIFIED
The defined acceptance test confirms the intended outcome or accepted completion condition.

### CLOSED
Administrative closure after verification and outcome recording.

### CANCELLED
The work was explicitly stopped with a recorded reason and appropriate authority.

## Completion versus verification

A generated proposal, spreadsheet, message, analysis, or code artifact does not automatically move a task to `VERIFIED`. The acceptance test must confirm the intended outcome.

Examples:

- Draft produced, but required approval missing: `AWAITING_APPROVAL`, not `COMPLETED`.
- Content draft approved internally but not yet published where publication is the outcome: `READY_FOR_ACTION`, not `VERIFIED`.
- Consultant identified but availability is stale: `AWAITING_INPUT`/refresh required, not staffing-ready.
- Agent claims work complete but QA rejects material errors: `REWORK`.

## Blockers and next checks

Blocked and awaiting-input tasks require named blockers/evidence gaps and a `next_check_at` or equivalent follow-up condition. Delegation is never fire-and-forget.

## Cancellation and supersession

Cancellation requires explicit reason and authority. Superseded work should preserve audit history and linkage rather than disappearing from the ledger.

## Auditability

Every consequential transition records actor, task/correlation identity, before/after state, authority, approval/evidence references where applicable, result/error, and idempotency information.
