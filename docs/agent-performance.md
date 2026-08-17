# Agent Performance and AgentOps

Phase 1 measures agents against verified outcomes, quality, governance, reliability, executive leverage, and efficiency. Volume of output is not a success metric.

## Scorecard categories

Initial configurable weights:

| Category | Weight | Core question |
|---|---:|---|
| Outcome Achievement | 30% | Did the assigned business outcome actually occur? |
| First-Pass Quality | 20% | Was the work accepted without material correction? |
| Escalation Judgment | 15% | Did the agent escalate material matters and avoid trivial escalation? |
| Evidence & Governance | 10% | Were provenance, factual accuracy, source authority, approvals, and data handling correct? |
| Execution Reliability | 10% | Were deadlines, blockers, dependencies, and completion handled reliably? |
| CEO Leverage | 10% | Did the work reduce Michael's required involvement while preserving decision quality? |
| Efficiency | 5% | Where telemetry exists, was cost/tool/cycle usage proportionate to verified value? |

Weights are versioned configuration, not permanent policy.

## Escalation judgment

Track at minimum:

- correct escalations
- unnecessary escalations
- missed escalations

An agent should not be rewarded for simply escalating uncertainty to Michael. It should resolve what is inside its authority and escalate only when authority, consequence, confidence, reversibility, or policy requires it.

## CEO leverage

Track:

- CEO touches
- CEO decisions required
- CEO interventions
- tasks resolved without CEO
- estimated CEO time avoided only where an explicit methodology supports the estimate

Do not fabricate time savings.

## Defects

Severity levels:

- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`

Critical examples include unauthorized external action, fabricated material evidence, confidentiality breach, prohibited-source exposure, bypassed human approval, irreversible unauthorized action, and false claim of human approval.

A critical defect triggers immediate AgentOps review and normally a `QUARANTINE` recommendation.

## Health states and routing

- `SHADOW`: limited authority, outputs reviewed
- `ACTIVE`: normal routing
- `WATCH`: elevated rework or performance degradation
- `RESTRICTED`: reduced authority/workload
- `QUARANTINED`: no new production work
- `RETIRED`: no active routing

## AgentOps recommendation set

AgentOps may recommend:

- `CONTINUE`
- `INCREASE_ROUTING`
- `DECREASE_ROUTING`
- `WATCH`
- `RESTRICT`
- `RETRAIN_OR_REVISE`
- `QUARANTINE`
- `RETIRE`
- `BUILD_NEW_SPECIALIST`

Recommendations are advisory to CoS. CoS may make bounded workload changes. Material authority changes require Michael approval.

## Rolling management signals

AgentOps should monitor task success/failure, rework, stalled tasks, missed deadlines, escalation quality, rejection reasons, error taxonomy, workload balance, repeated tool failure, repeated evidence defects, and high-cost/low-value loops.

Performance changes must be evidence-based. A single strong output does not justify expanded authority, and one low-severity defect does not automatically justify quarantine.
