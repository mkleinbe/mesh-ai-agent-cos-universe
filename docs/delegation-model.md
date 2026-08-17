# Delegation Model

Phase 1 delegates work through structured contracts, not informal agent chat. Every work package remains accountable to the parent objective and visible until verified, cancelled, or explicitly superseded.

## Contract

Delegations follow `mesh.cos.delegation.v1` / `delegation.v1` and include:

- delegation ID
- task ID and optional parent task ID
- delegating agent
- exactly one accountable agent
- contributing agents
- business objective
- expected outcome
- deliverable
- success criteria
- deadline
- priority
- evidence supplied
- unresolved evidence
- constraints
- authority level
- permitted actions
- prohibited actions
- approval gates
- dependencies
- next check time
- escalation condition
- acceptance test

## Rules

1. Every delegation has exactly one accountable agent.
2. Normal depth is CoS -> functional executive -> specialist/worker.
3. Cross-functional reassignment goes through CoS.
4. A child worker cannot redefine the parent objective.
5. Delegation cannot widen authority beyond the delegator's permitted boundary.
6. Required approval cannot be delegated away.
7. Circular delegation is prohibited.
8. Duplicate active accountable ownership is prohibited.
9. Every delegated work package requires a measurable acceptance condition.
10. Failed acceptance returns the work for remediation or escalation.

## Accountability versus contribution

Accountability is singular. Contribution is plural. A CFO, COO, and Devil's Advocate may all contribute to a CRO-owned pursuit task, but the task still has one accountable owner.

## Check-ins

Delegation is not fire-and-forget. The contract carries `next_check_at` and escalation conditions so CoS/AgentOps can detect stalls, unresolved dependencies, repeated rework, or abandonment without requiring Michael to supervise agents.

## Reassignment

CoS may reallocate work among registered agents within its authority. Reassignment must preserve task history, evidence, prior decisions, and audit events. A reassignment does not erase defects or restart performance history.

## Approval boundary

An agent may delegate preparation for an L4/L5 action but not the approval obligation itself. Example: CRO may delegate proposal analysis, CFO may model economics, and COO may validate feasibility, but final pricing or material commitment remains human-gated.

## Parent objective integrity

A specialist may identify that the requested approach is infeasible or unsafe. It should raise evidence, risk, blocker, or recommendation rather than silently substituting a different business objective.
