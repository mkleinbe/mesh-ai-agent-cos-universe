# Testing and Evaluation

Phase 1 is verified at the contract, state-machine, authority, security, reliability, performance, and scenario levels. Tests are designed to reject unsafe or invalid behavior, not merely confirm happy paths.

## Local pre-merge verification

Recorded for the Phase 1 release candidate:

- 9 JSON schemas plus positive examples validated successfully
- 40 `pytest` tests passed
- Python `compileall` passed for `src/`
- 13 required Phase 1 evaluation scenarios are represented

Two implementation defects found during pressure testing were corrected before the release candidate was finalized. Remote GitHub Actions results must be treated separately from local verification. If no remote run is surfaced, that is not equivalent to a passing remote CI run.

## Contract tests

Each schema validates positive fixtures and rejects invalid structures where covered. Contracts include:

- agent-record.v1
- task.v1
- delegation.v1
- agent-event.v1
- decision.v1
- conflict.v1
- approval.v1
- performance-event.v1
- performance-scorecard.v1

Backward-compatibility policy is documented in `contracts/BACKWARD_COMPATIBILITY.md`.

## State-machine tests

The task lifecycle rejects invalid transitions and preserves the distinction between `COMPLETED`, `VERIFIED`, and `CLOSED`. Failed acceptance/verification can return work to `REWORK` or execution rather than silently closing the task.

## Authority and escalation tests

Tests verify that:

- agents cannot widen authority through delegation
- approval obligations cannot be delegated away
- L4/L5 work fails closed without required approval
- material pricing/commercial questions escalate
- high-impact, low-confidence recommendations escalate
- cross-functional tradeoffs route through CoS while preserving functional truth

## Security tests

Coverage includes:

- source permission rejection
- prompt-injection resistance, with retrieved content treated as untrusted data
- confidentiality and prohibited-source boundaries
- unauthorized external-action handling
- quarantine behavior after critical defects

## Reliability tests

Coverage includes:

- duplicate Slack/event delivery idempotency
- no duplicate work creation from repeated events
- stalled-work detection
- coordination-loop detection
- explicit kill-switch behavior

## Performance tests

AgentOps score calculation is deterministic against versioned weights. Tests cover health/routing implications such as WATCH behavior and critical-defect quarantine.

## Required Phase 1 evaluation scenarios

1. Routine team question is resolved without Michael.
2. Pricing question is escalated.
3. CRO/CFO disagreement is resolved through CoS framing while preserving functional authority.
4. COO blocks infeasible staffing.
5. Stale consultant availability is identified instead of treated as confirmed.
6. CMO/VP Content produces a draft while publication remains approval-gated.
7. Repeated QA failure drives an AgentOps WATCH recommendation.
8. Critical unauthorized-action attempt causes quarantine behavior.
9. Duplicate Slack event is safely ignored.
10. Repetitive agent conversation without state/evidence progress is flagged as a coordination loop.
11. Missing source authority prevents false certainty.
12. High-impact, low-confidence recommendation escalates.
13. A completed artifact that fails outcome verification returns to rework.

## Metrics posture

The implementation is designed to support measurement of CEO deflection, CEO touches, first-pass quality, rework, escalation quality, cycle time, stalled work, verified outcomes, agent failures, approval cycle time, cross-agent conflicts, coordination loops, contributors per task, and cost per verified outcome where telemetry exists.

No baseline or target values are invented. Evidence must be collected before thresholds, scorecard weights, or autonomy are changed.

## CI

`.github/workflows/ci.yml` runs on pull requests and pushes to `main` and `phase1/**` and executes:

1. Python 3.12 setup
2. editable install with development dependencies
3. contract validation
4. `pytest`
5. Python `compileall`

A merge decision must distinguish local verification from remotely observed CI status.
