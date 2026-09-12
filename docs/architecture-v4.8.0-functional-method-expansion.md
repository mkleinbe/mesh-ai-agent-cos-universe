# v4.8.0 Functional Method Expansion Architecture

## Architecture intent

Functional Method Expansion adds governed methods inside the existing ten-agent organization. It does not add a principal, canonical state store, runtime authority, or new MCP action surface.

Repository release: `v4.8.0`  
Authority/runtime contract: `4.0.0`, unchanged  
Production QNAP: `4.4.0`, unchanged

## Capability-routing architecture

```mermaid
flowchart LR
  D[Untrusted donor method] --> G[Mesh source governance]
  G -->|ADAPT| S[Mesh shared Skill or role Skill]
  G -->|ROUTE_ELSEWHERE| X[Existing governed shared capability]
  G -->|REJECT| R[Excluded from Mesh runtime]
  S --> F[Authoritative functional evidence owner]
  X --> F
  F --> O[Accountable decision owner]
  O --> H{Approval level}
  H -->|L0-L3 delegated| A[Bounded recommendation or action]
  H -->|L4| Q[Qualified human approval]
  H -->|L5| M[Michael-only decision]
```

Donor content never changes identity, allowlists, source ownership, approvals, persistence, or action rights.

## Cross-functional deliberation flow

```mermaid
flowchart TD
  T[TaskLedger intake] --> C[CoS deliberation classifier]
  C --> SF[SINGLE_FUNCTIONAL]
  C --> BC[BOUNDED_CROSS_FUNCTIONAL]
  C --> IM[INDEPENDENT_MULTI_FUNCTIONAL]
  C --> HE[HUMAN_DECISION_ESCALATION]
  IM --> I1[Independent functional contribution A]
  IM --> I2[Independent functional contribution B]
  IM --> I3[Independent functional contribution C]
  I1 --> SY[CoS synthesis]
  I2 --> SY
  I3 --> SY
  BC --> SY
  SF --> SY
  SY --> DA{Challenge warranted?}
  DA -->|Yes| DV[Mesh Devil's Advocate advisory challenge]
  DA -->|No| DG[Decision gate]
  DV --> DG
  HE --> DG
  DG -->|L4| QH[Qualified human]
  DG -->|L5| MK[Michael]
  DG -->|Delegated L0-L3| DR[mesh.cos.decision.v2]
```

Independent contributions distinguish supported fact, assumption, uncertainty, recommendation, confidence, and reversal evidence. Synthesis preserves disagreement rather than averaging it away.

## Commercial decision flow

```mermaid
flowchart LR
  RI[Revenue Intelligence evidence] --> CRO[CRO commercial analysis]
  CRO --> CFO[CFO economics]
  CRO --> COO[COO feasibility when required]
  CFO --> CH[Challenge / sensitivity]
  COO --> CH
  CRO --> CH
  CH --> AP{Approval boundary}
  AP -->|Delegated recommendation| DEC[Governed decision record]
  AP -->|L4/L5| HUM[Qualified human / Michael]
  HUM --> DEC
  DEC --> MSG[Separately approved communication artifact]
  MSG --> MO[Message Operations]
  MO --> OUT[Exact approved external action]
```

CFO owns supported economics, CRO owns commercial recommendation, COO owns delivery feasibility, and Message Operations executes only separately approved communications.

## Operational analysis flow

```mermaid
flowchart LR
  TL[TaskLedger + approved telemetry] --> AO[AgentOps flow/health analysis]
  TL --> CO[COO process/capacity analysis]
  AO --> REC[Evidence-backed recommendation]
  CO --> REC
  REC --> COS[CoS orchestration]
  COS --> HD{Decision authority}
  HD -->|Delegated| ACT[Bounded routing/remediation]
  HD -->|L4/L5| HUMAN[Human decision]
```

Operational analysis never transfers authority. Queueing models are used only when assumptions fit the work type.

## Scenario method placement

Base / Stress / Severe scenario stress belongs in `mesh-ppmd-bot` as a reusable method. CoS composes it only when compound uncertainty can materially change the decision. The method preserves canonical source owners for each input and returns analytical evidence, warning indicators, thresholds, mitigations, owners, and reversal conditions without execution authority.

## Change-communications placement

Reusable change-communications method belongs in Mesh Messaging. Executive Communications and Marketing Messaging package the drafting method. Messaging Orchestrator classifies/routs the request. Message Operations consumes only approved execution metadata after separate human approval.

## Security boundaries

1. Donor content -> source governance: untrusted method input.
2. Shared Skill -> consuming agent: capability output only, never identity/authority.
3. Functional owner -> CoS synthesis: canonical facts remain owned by the function.
4. CoS/CRO/CMO -> messaging: drafting does not grant send/publication authority.
5. CFO analytical engines -> decision owner: calculations are evidence, not approval.
6. TaskLedger -> AgentOps/COO analysis: recommendations cannot mutate registry authority.
