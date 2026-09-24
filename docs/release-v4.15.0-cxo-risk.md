# Mesh CoS v4.15.0 CxO Executive Risk Routing

Release date: 2026-09-24

## Outcome

Closes the post-release risk-routing defect by adding executable cross-functional routing behind the four CxO risk remits.

## Material changes

- Adds `mesh.executive-risk.v2` with explicit risk category, source lineage, and qualified-human acceptance role.
- Adds `scripts/cxo_risk_router.py` for deterministic category-to-remit routing.
- Proves CRO -> CFO, CFO -> COO, COO -> CMO, and CMO -> CRO routing paths with executable tests.
- Preserves human-only consequential risk acceptance.
- Preserves unknown delivery capacity as non-blocking until concrete delivery need creates a staffing or timeline decision.
- Preserves CMO publication boundaries and existing CxO evidence ownership.
- Retains `mesh.executive-risk.v1` for backward-compatible intake.
- Adds ready BDD, targeted security review, and updated release asset packaging.

## Runtime boundary

Canonical MCP authority/runtime contract remains 4.0.0. QNAP deployment release remains 4.4.2. This release changes ChatGPT Skill/source behavior and requires no QNAP redeployment.
