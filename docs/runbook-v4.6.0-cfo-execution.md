# Runbook v4.6.0: CFO Analytical Execution

## Deterministic calculation path

1. Confirm the CFO task and approved source inputs.
2. Select a supported operation from `chatgpt/skills/mesh-cfo/scripts/financial_math.py`.
3. Pass explicit numeric values only.
4. Capture the structured result and source assumptions in the finance evidence packet.
5. Cross-check material outputs or route to Mesh Data Analytics when the calculation depends on larger datasets, model links, transformations, or reconciliations.
6. Return an L3 recommendation. Do not convert a positive metric into approval.

## Mesh Data Analytics path

1. Confirm the work is analytical and within CFO source/decision authority.
2. Invoke `mesh-data-analytics` through `skills.invoke_governed`.
3. Require the handoff to remain `AUTHORIZATION_HANDOFF_ONLY` with result provenance required.
4. Let Mesh Data Analytics resolve the approved analytical engine and validation contract.
5. Require source identity, as-of date, definitions, transformations, reconciliation, uncertainty, and validation evidence.
6. CFO interprets the validated result and remains the recommendation owner.
7. Route consequential pricing, spending, hiring, investment, contractual, transfer, or other material action to the qualified human approval owner.

## Recurring finance cadence

- Weekly: exceptions in cash timing, AR/DSO, pipeline-to-revenue assumptions, engagement margin, utilization/cost-to-serve, forecast drivers, and upcoming decisions.
- Monthly: driver-based forecast versus actual, contribution economics, unit economics, working-capital implications, material concentration, and decision business cases.
- Quarterly: scenario reset, capital-allocation alternatives, portfolio/service-line economics, concentration/resilience, value realization, and CEO/board decision needs.

Do not create threshold policy from donor benchmarks or unsourced defaults.

## Failure handling

- Unsupported deterministic operation: stop and route to governed analytics; never extend the calculation surface ad hoc inside a decision.
- Invalid numeric input: fail closed and identify the missing/invalid field.
- Missing source or stale material input: stop or downgrade confidence; do not silently substitute a benchmark.
- Mesh Data Analytics unavailable: use another approved analytical engine only if permitted by that Skill's fallback contract; otherwise report a dependency.
- Conflicting sources: preserve both, resolve definition/period/scope, and escalate material unresolved conflict.
- Missing human approval: produce recommendation and decision conditions only; do not execute the consequential action.

## Rollback

Revert the v4.6.0 CFO registry/manifest/Skill/tests/docs commit. The canonical MCP runtime `4.0.0` and production QNAP deployment `4.4.0` are unchanged, so no QNAP rollback or restart is required.
