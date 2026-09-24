# v4.15.0 CxO Executive Risk Routing Architecture

The four CxO Skills use `mesh.executive-risk.v2` for new risk handoffs. Historical v1 records remain readable. The deterministic router assigns risk categories to CRO, CFO, COO, or CMO while preserving a qualified-human acceptance principal.

```mermaid
flowchart LR
  D[Decision] --> C[CxO risk analysis]
  C --> R[mesh.executive-risk.v2]
  R --> M[Deterministic category to remit router]
  M --> CRO[CRO]
  M --> CFO[CFO]
  M --> COO[COO]
  M --> CMO[CMO]
  CRO --> T[Treatment and monitoring]
  CFO --> T
  COO --> T
  CMO --> T
  T --> A[Devil's Advocate independent challenge]
  A --> H[Qualified human acceptance role]
  H --> F[Feedback and review]
```

A Skill may recommend treatment but never becomes the risk-acceptance principal. Unknown delivery capacity does not block early pursuit. Capacity becomes decision relevant only when concrete delivery need and a staffing or timeline commitment coexist.
