# v4.14.0 CxO Executive Risk Management Architecture

The four CxO Skills use one additive shared risk contract, `mesh.executive-risk.v1`. Each CxO owns risk recommendation only within its existing functional remit. Cross-functional risk is routed to the correct owner. Consequential acceptance remains with the qualified human authority.

```mermaid
flowchart LR
  D[Decision] --> C[CxO risk analysis]
  C --> R[mesh.executive-risk.v1]
  R --> X{Outside current remit?}
  X -->|Yes| O[Owning CxO]
  X -->|No| T[Treatment or test]
  O --> T
  T --> A[Devil's Advocate independent challenge]
  A --> H{Consequential acceptance?}
  H -->|Yes| Q[Qualified human authority]
  H -->|No| M[Monitor and continue]
  Q --> M
  M --> F[Feedback and review]
```

The shared contract does not create enterprise risk truth. It standardizes decision-support handoff fields, treatment ownership, monitoring, escalation, reversibility, residual risk, and acceptance ownership.
