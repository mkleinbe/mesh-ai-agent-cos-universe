# Testing and Evaluation

Phase 1 is verified at the contract, state-machine, authority, security, reliability, performance, and end-to-end workflow levels. Tests are designed to reject unsafe or invalid behavior, not merely confirm happy paths.

## TDD and loop-engineering approach

The 0.2.0 remediation was executed as red-green-refactor loops:

1. Add failing acceptance/contract tests for an audited gap.
2. Implement the minimum governed behavior required to turn the tests green.
3. Refactor toward a single canonical model or service boundary.
4. Run remote CI and inspect the failing gate rather than weakening policy.
5. Add regression coverage before advancing to the next gap.

The initial remediation tests covered runtime/contract parity, canonical persistence, durable CoS orchestration, complete delegation rules, Slack signature/dedupe/thread mapping, governed functional adapters, conflict/decision records, Answer Desk behavior, AgentOps, reliability, registry overrides, metrics, and duplicate-intake prevention.

## Final pre-merge verification

The latest green remediation GitHub Actions run recorded:

- 9 JSON schemas plus positive examples validated successfully
- 44 `pytest` tests passed
- 82.67% source coverage against a 65% minimum gate
- Ruff critical correctness checks passed
- mypy passed across the source package
- pip-audit reported no known dependency vulnerabilities
- Python `compileall` passed for `src/`

## Contract tests

Each schema validates positive fixtures and rejects invalid structures where covered. Runtime persistence validates versioned objects against the same contracts. Contracts include:

- agent-record.v1
- task.v1
- delegation.v1
- agent-event.v1
- decision.v1
- conflict.v1
- approval.v1
- performance-event.v1
- performance-scorecard.v1

Runtime round-trip tests require TaskRecord, Delegation, and normalized Agent Registry records to validate against these contracts before canonical persistence.

## State-machine and outcome tests

The task lifecycle rejects invalid transitions and preserves the distinction between `COMPLETED`, `VERIFIED`, and `CLOSED`.

`VERIFIED` now requires an executed acceptance evaluator whose result is persisted with pass/fail status, evidence, reason, and timestamp. Failed verification returns work to `REWORK` rather than silently closing the task.

## Delegation, authority, and escalation tests

Coverage verifies that:

- every delegated task has one accountable owner
- normal depth remains two levels below CoS
- child work cannot redefine the parent objective or expected outcome
- authority cannot widen through delegation
- parent approval obligations cannot be delegated away
- circular delegation is rejected
- duplicate active ownership is rejected
- permitted actions must be a subset of agent authority
- agent-prohibited actions cannot be enabled by a child delegation
- cross-functional delegation/reassignment routes through CoS
- L4/L5 work fails closed without required approval
- material pricing/commercial questions escalate
- high-impact, low-confidence recommendations escalate
- cross-functional tradeoffs preserve functional truth

## Security tests

Coverage includes:

- source permission rejection
- invocation-time agent tool/source allowlists
- quarantined/retired agent invocation denial
- prompt-injection resistance, with retrieved content treated as untrusted data
- consequential Message Operations approval gating
- Slack HMAC request-signature validation and stale/invalid rejection paths
- durable duplicate Slack-event suppression
- false/missing approval rejection
- quarantine behavior after critical defects

## Reliability tests

Coverage includes:

- duplicate intake prevention with durable idempotency keys
- durable external-event idempotency
- one-task/one-Slack-thread mapping
- bounded retries and execution timeouts
- work leases/check-ins
- execution-failure audit records
- stalled-work detection
- coordination-loop detection
- explicit kill-switch behavior
- failed outcome verification and remediation

## AgentOps and performance tests

AgentOps score calculation is deterministic against the versioned `config/performance-policy.v1.json` policy. Tests cover:

- rolling scorecard persistence
- configurable weight version
- WATCH and RESTRICT behavior
- critical-defect QUARANTINE
- workload/stall signals
- defect taxonomy
- portfolio recommendations including route decrease, retraining/revision, retirement, and new-specialist recommendations when explicit evidence conditions are supplied

## Stateful Phase 1 workflow evaluations

The original 13 policy scenarios remain as regression tests. Additional stateful evaluations exercise the runtime services and canonical ledger across the six required Phase 1 workflow classes:

1. **Pursuit/proposal:** CRO accountable, CFO/COO/Devil's Advocate contributors, governed tool calls, evidence, QA, verification, and closure.
2. **Engagement economics:** CFO task reaches human L4 pricing approval, a durable decision record, verified outcome, and closure.
3. **Consultant staffing:** stale availability returns `REQUIRES_REFRESH` and blocks commitment.
4. **Marketing content:** publication remains L4 gated and cannot proceed on artifact completion alone.
5. **Team question:** Answer Desk applies access, answer, route/recommendation, approval, escalation, and evidence-block dispositions.
6. **Agent failure:** critical evidence/governance failure produces quarantine behavior while Slack request security and dedupe are enforced.

## Metrics posture

`MetricsService` deterministically derives the required Phase 1 operating measures from canonical records where evidence exists:

- work resolved without Michael
- questions deflected from Michael
- CEO touches per completed task
- first-pass acceptance and rework
- escalation quality
- task cycle and stalled-work rates
- verified outcome rate
- agent failure rate
- approval cycle time
- cross-agent conflict rate
- coordination-loop rate
- contributors per task
- cost per verified outcome only when cost telemetry actually exists

No baseline, target, or cost saving is invented.

## CI

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`, `phase1/**`, and `remediation/**` and executes:

1. Python 3.12 setup
2. editable install with development dependencies
3. contract validation
4. Ruff correctness checks
5. mypy
6. pytest with coverage gate
7. dependency vulnerability audit
8. Python compileall

A merge requires a green remote CI run on the final PR head.
