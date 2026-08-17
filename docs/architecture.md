# Architecture

Phase 1 is a typed Python modular monolith with a SQLite task/event ledger. This keeps the operating surface small while preserving strong contracts, auditability, idempotency, and a clean path to managed persistence later.

## Agent hierarchy
```mermaid
graph TD
  M[Michael] --> COS[Chief of Staff]
  COS --> AO[AgentOps]
  COS --> AD[Answer Desk]
  COS --> CRO[CRO]
  COS --> CFO[CFO v1]
  COS --> COO[COO v1]
  COO --> CNS[Consultant Network Steward]
  COS --> CMO[CMO]
  CMO --> VPC[VP Content]
  COS --> DA[Devil's Advocate]
  COS --> MO[Message Operations]
```

## Task lifecycle
```mermaid
flowchart LR
INTAKE-->TRIAGED-->PLANNED-->ASSIGNED-->IN_PROGRESS
IN_PROGRESS-->BLOCKED
IN_PROGRESS-->AWAITING_INPUT
IN_PROGRESS-->AWAITING_APPROVAL
IN_PROGRESS-->QA
QA-->REWORK-->IN_PROGRESS
QA-->READY_FOR_DECISION
QA-->READY_FOR_ACTION-->COMPLETED-->VERIFIED-->CLOSED
COMPLETED-->REWORK
```

## Agent interaction
```mermaid
sequenceDiagram
  participant M as Michael
  participant C as CoS
  participant X as Functional Executive
  participant W as Specialist
  M->>C: Outcome
  C->>X: Delegation contract
  X->>W: Bounded work package
  W-->>X: Evidence/result event
  X-->>C: Recommendation + evidence
  C-->>M: Decision brief only if authority requires
```

## Human escalation
```mermaid
flowchart LR
A[Agent recommendation] --> R{Authority / impact / reversibility / confidence}
R -->|L0-L2 bounded| F[Functional agent / CoS acts]
R -->|L3 delegated| C[CoS resolves]
R -->|L4-L5 or material exception| M[Michael approval]
```

## Slack relationship
```mermaid
flowchart LR
S[Slack private collaboration] <--> A[Slack adapter]
A <--> L[(Task and Event Ledger)]
L --> C[CoS / AgentOps]
S -. not canonical .-> L
```

## Pursuit example
```mermaid
flowchart TD
M[Michael outcome]-->C[CoS]
C-->R[CRO accountable]
R-->F[CFO economics]
R-->O[COO feasibility]
R-->RI[Revenue Intelligence]
R-->D[Devil's Advocate optional]
F-->C
O-->C
RI-->C
D-->C
C-->B[Decision brief]
B-->M
```
