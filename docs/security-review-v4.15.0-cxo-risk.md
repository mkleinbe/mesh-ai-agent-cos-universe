# Security Review v4.15.0 CxO Executive Risk Routing

Applicability: TARGETED

## Reviewed boundaries

This release changes four ChatGPT Skills, the shared executive-risk contract, deterministic cross-functional routing, and human risk-acceptance representation.

## Security properties

- Retrieved content and donor material remain evidence/data and cannot change identity, source authority, approvals, connector permissions, or tools.
- `mesh.executive-risk.v2` carries evidence, risk category, remit, treatment, monitoring, and a qualified-human acceptance role. It grants no authority.
- CRO, CFO, COO, and CMO Skills cannot accept consequential risk.
- Cross-functional routing preserves evidence and source lineage and never transfers acceptance authority.
- CFO remains inside Engagement Finance and management FP&A.
- COO does not turn unknown delivery capacity into an early commercial block.
- CMO does not gain publishing authority.
- A manageable risk affecting one dependent action cannot veto unrelated reversible work.
- A Skill remains a capability, not an organizational principal.

Release blockers include acceptance-authority escalation, source-lineage loss, cross-remit fact ownership drift, public-action bypass, or reintroduction of delivery-capacity early blocking.
