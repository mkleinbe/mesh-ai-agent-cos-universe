# Delegation Model

Delegation is a durable work contract, not an informal chat handoff. The Phase 1 runtime validates delegation rules before persisting a delegated work package.

## Normal hierarchy

```mermaid
flowchart TB
    COS[Chief of Staff]
    FE[Functional Executive]
    SW[Specialist / Worker]
    COS --> FE --> SW
```

Normal depth is limited to two levels below CoS. Deeper recursive agent trees and swarms are outside the Phase 1 operating model.

## Required contract content

A delegation must specify:

- delegation ID and task ID,
- delegating agent,
- exactly one accountable agent,
- business objective and expected outcome,
- deliverable,
- measurable success criteria,
- priority,
- authority level,
- acceptance test,
- parent task where applicable,
- contributors,
- deadline and next check where applicable,
- evidence supplied and unresolved evidence,
- constraints,
- permitted actions,
- prohibited actions,
- approval gates,
- dependencies,
- escalation condition.

## Enforcement rules

```mermaid
flowchart LR
    D[Proposed delegation] --> O{Exactly one owner?}
    O -->|no| REJ[Reject]
    O -->|yes| DEP{Depth allowed?}
    DEP -->|no| REJ
    DEP -->|yes| AUTH{Authority <= parent?}
    AUTH -->|no| REJ
    AUTH -->|yes| CIRC{Circular?}
    CIRC -->|yes| REJ
    CIRC -->|no| GATE{Parent approvals inherited?}
    GATE -->|no| REJ
    GATE -->|yes| ACT{Permitted/prohibited conflict?}
    ACT -->|yes| REJ
    ACT -->|no| ACC{Acceptance measurable?}
    ACC -->|no| REJ
    ACC -->|yes| SAVE[Persist delegation]
```

The service enforces the following constitutional rules:

1. An accountable agent is mandatory.
2. The accountable agent cannot also be listed as a contributor to the same delegation.
3. Delegation depth cannot exceed the Phase 1 limit.
4. Child authority cannot exceed parent authority.
5. Circular delegation is rejected.
6. Active ownership cannot be silently replaced when the validation context specifies the current owner.
7. Measurable success criteria and an acceptance test are required.
8. Parent approval obligations must be inherited.
9. The same action cannot be both permitted and prohibited.
10. The delegation record is persisted to canonical state after validation.

## Reassignment and remediation

Reassignment is not a deletion of history. Existing delegation and audit state must remain reconstructable. If verification fails, the work routes to `REWORK`; a new or revised delegation may be created with the same parent objective and preserved approval obligations.

## Authority and evidence

Delegation transfers responsibility for a bounded work package, not source authority. A functional worker may gather or analyze evidence, but the authoritative owner of a fact remains the source/domain owner defined by policy.
