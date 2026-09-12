# v4.8.0 Requirements Traceability Matrix

| Requirement | BDD | Implementation target | Verification |
|---|---|---|---|
| Preserve 10-agent roster, parentage, TaskLedger, L4/L5, completion != verification | FME-001..003 | registry unchanged; CoS governance text | `test_fme_001_002_003_governance_invariants` + Phase 1 regressions |
| Deliberation classifier and independent cross-functional synthesis | FME-004..006 | `mesh-chief-of-staff`, `agents/cos.md` | CoS content tests + independent verification |
| Scenario Base/Stress/Severe with cascade/reversal conditions | FME-007 | `mesh-ppmd-bot` shared method + CoS composition | PPMD behavior tests + CoS consumption test |
| Strategic work-graph and change-readiness diagnostics | FME-008..009 | CoS role guidance | CoS content tests |
| AgentOps flow intelligence and guarded queueing | FME-010..011 | AgentOps Skill/role | AgentOps content tests |
| Answerability/source health states | FME-012 | Answer Desk Skill/role | Answer Desk content tests |
| CRO pricing, policy, forecasting, partnerships, channel, RFP | FME-013,015..017 | CRO Skill/role | CRO content tests |
| Correct deal discount economics | FME-014 | CFO deterministic math + CRO/CFO method contract | exact 100/20/30 regression + malformed input tests |
| CFO commercial economics | FME-018 | CFO Skill/role + existing analytics composition | CFO content and math regressions |
| COO process/capacity/vendor/procurement analysis | FME-019 | COO Skill/role | COO content tests |
| Consultant network concentration/freshness/contingency | FME-020 | Network Steward Skill/role | Steward content tests |
| CMO growth/change methods | FME-021 | CMO Skill/role + Messaging shared method | CMO and Messaging tests |
| VP Content proof/inventory lineage | FME-022 | VP Content Skill/role | VP Content content tests |
| Message Ops metadata remains execution-only | FME-023 | Message Ops Skill/role + Messaging execution boundary | Message Ops tests + Messaging regressions |
| Shared Skills never become principals/authority | FME-024 | all changed Skill governance; security review | governance tests + FULL_REVIEW receipt |
| Donor provenance and explicit rejection decisions | source governance | `docs/source-governance-v4.8.0.md` | docs audit |
| Capability routing and deliberation/commercial/ops architecture | documentation | `docs/architecture-v4.8.0-functional-method-expansion.md` | documentation verification |
| Repository release is v4.8.0 while runtime contract stays 4.0.0 and QNAP stays 4.4.0 | release | README, RELEASE, changelog, release docs, workflow | release-state tests + tag/release alignment |
