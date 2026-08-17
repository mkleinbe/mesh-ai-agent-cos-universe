# Architecture

Phase 1 is a typed Python modular monolith with a SQLite canonical operating ledger. The architecture intentionally keeps the runtime surface small while preserving strong contracts, durable state, explicit authority, auditability, idempotency, and a clean path to managed persistence later.

## Runtime layers

```mermaid
flowchart TD
  U[Human / Slack / API Intake] --> COS[CoSService]
  COS --> AUTH[Authority + Approval]
  COS --> DEL[DelegationService]
  COS --> EXEC[AgentExecutionService]
  EXEC --> FG[FunctionalRuntime + AuthorizationGateway]
  FG --> SK[Injected Mesh Skills / Sources]
  COS --> GOV[GovernanceService]
  COS --> VER[Acceptance Verification]
  COS --> L[(Canonical SQLite Ledger)]
  AUTH --> L
  DEL --> L
  EXEC --> L
  GOV --> L
  VER --> L
  SL[SlackAdapter] <--> L
  AO[AgentOpsService] <--> L
  AD[AnswerDeskService] <--> L
  REG[Canonical AgentRegistry] --> AUTH
  REG --> FG
```

The ledger persists tasks, events, delegations, approvals, decisions, conflicts, performance events, scorecards, registry changes, verification results, Slack mappings, metrics, idempotency state, and work leases.

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

## Canonical contracts

Nine versioned contracts define the consequential operating objects: AgentRecord, TaskRecord, Delegation, AgentEvent, Decision, Conflict, Approval, PerformanceEvent, and PerformanceScorecard. Runtime persistence validates versioned objects against these schemas.

`agents/registry.json` is the canonical agent-definition source. Runtime health changes are overlays persisted in the ledger and audited rather than silently rewriting the source file.

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
QA-->READY_FOR_ACTION-->COMPLETED
READY_FOR_DECISION-->AWAITING_APPROVAL-->READY_FOR_ACTION
COMPLETED-->VERIFIED-->CLOSED
COMPLETED-->REWORK
```

`COMPLETED` is an execution assertion. `VERIFIED` requires an acceptance evaluator to execute and persist a pass/fail record with evidence. Failed verification routes back to remediation.

## Agent interaction

```mermaid
sequenceDiagram
  participant M as Michael
  participant C as CoSService
  participant X as Functional Executive
  participant W as Specialist
  participant L as Ledger
  M->>C: Outcome
  C->>L: Create canonical task
  C->>X: Governed work package
  X->>W: Bounded delegation
  W-->>L: Evidence/result event
  X-->>L: Recommendation + evidence
  C->>L: Verify acceptance outcome
  C-->>M: Decision brief only if authority requires
```

## Human escalation

```mermaid
flowchart LR
A[Agent recommendation] --> R{Authority / impact / reversibility / confidence}
R -->|L0-L2 bounded| F[Functional agent / CoS acts]
R -->|L3 explicitly delegated| C[CoS resolves]
R -->|L4-L5 or material exception| M[Human / Michael approval]
```

L4 and L5 approval records remain canonical outside Slack. Message Operations cannot execute consequential external sends without a recorded approval reference.

## Functional execution

`FunctionalRuntime` composes injected real Mesh capabilities rather than duplicating them. `AuthorizationGateway` checks the canonical registry before each invocation for agent health, allowed tool/skill, and source authorization. Missing production invokers fail as unavailable rather than being represented as connected.

## Slack relationship

```mermaid
flowchart LR
S[Slack private collaboration] <--> A[SlackAdapter]
A <--> L[(Canonical Ledger)]
L --> C[CoS / AgentOps]
S -. never canonical .-> L
```

The adapter implements Slack Web API posting, v0 signature verification, durable duplicate-event suppression, and one-task/one-thread mapping. The current agent-operations channel is `#mesh-agent-ops` / `C0BRL4GCL3A`.

## AgentOps and observability

AgentOps consumes durable tasks, performance events, metrics, and health history. Versioned scoring policy lives in `config/performance-policy.v1.json`. AgentOps recommendations can change workload/routing within bounded authority; material authority expansion remains Michael-exclusive.

## Pursuit example

```mermaid
flowchart TD
M[Michael outcome]-->C[CoS]
C-->R[CRO accountable]
R-->F[CFO economics contributor]
R-->O[COO feasibility contributor]
R-->RI[Revenue Intelligence]
R-->D[Devil's Advocate]
F-->L[(Ledger evidence)]
O-->L
RI-->L
D-->L
L-->C
C-->V[Acceptance verification]
V-->B[Decision brief]
B-->M
```

## Persistence boundary

SQLite is appropriate for Phase 1/local or single-instance operation. Multi-instance or horizontally scaled deployment should migrate behind the existing persistence boundary rather than changing the operating contracts or authority model.
