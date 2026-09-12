# v4.8.2 Requirements Traceability

| Requirement | BDD | Implementation / control | Test / evidence | Security / verification disposition |
|---|---|---|---|---|
| Behavior proof exceeds phrase presence | FMR-001 | ten role-local `scripts/fme_behavior.py` gates; structural tests retained | `test_fmr001_*`; v4.8.0 structural regression | FULL_REVIEW; exact-candidate CI required |
| CoS smallest sufficient deliberation | FMR-002 | CoS deliberation gate | `test_fmr002_*` | no authority expansion |
| Preserve independent contribution evidence and disagreement | FMR-003 | CoS synthesis gate | `test_fmr003_*` | false-consensus prohibition |
| Base / Stress / Severe and work-graph/change bounds | FMR-003 | CoS scenario/work-graph/change gates; PPMD v1.2.0 compatibility | `test_fmr003_*` | scenario evidence only; no HR authority |
| AgentOps flow diagnostics and queue assumption gate | FMR-004 | AgentOps flow/queue/boundary gates | `test_fmr004_*` | no agent/headcount/tool/authority creation |
| Answer Desk five answerability states | FMR-005 | deterministic state classifier | parametrized `test_fmr005_*` | stale/conflict routes to owner, no rewrite |
| Unsupported buyer intent remains unknown | FMR-006 | CRO buyer-intent gate | `test_fmr006_fmr007_*` | no intent fabrication |
| Pricing recommendation and discount exception remain non-approving | FMR-006 | CRO pricing/exception gates | `test_fmr006_fmr007_*` | human approval preserved |
| Forecast views and partner attribution remain distinct | FMR-006 | CRO forecast/partner gates | `test_fmr006_fmr007_*` | no external partnership commitment |
| Missing RFP proof remains GAP | FMR-007 | CRO proof gate | `test_fmr006_fmr007_*` | no invented capability/certification/reference |
| CFO output is evidence, not approval; assumptions explicit | FMR-008 | CFO finance-boundary gate | `test_fmr008_*`; CFO v4.6 behavior regressions | no pricing/discount/procurement/contract authority |
| Governed Data Analytics routing remains intact | FMR-008 | existing `GovernedAdapterRegistry` | `test_fmr008_*` | `AUTHORIZATION_HANDOFF_ONLY` |
| COO current-state evidence, ToC and queueing remain assumption-bound | FMR-004, FMR-017 | COO process/queue gates | `test_fmr004_fmr017_*` | no procurement authorization, stale availability blocked |
| Consultant freshness affects readiness; no staffing commitment | FMR-009 | Steward readiness gate | `test_fmr009_*` | final staffing remains human-governed |
| Concentration, fallback and contingency are explicit/distinct | FMR-009 | Steward risk/coverage gates | `test_fmr009_*` | no commitment created |
| Generic benchmarks contextual; CRO/CFO dependencies preserved | FMR-010 | CMO benchmark/growth gates | `test_fmr010_*` | no policy laundering |
| Change communication remains draft/analysis and publication human-gated | FMR-010 | CMO communication gate; Messaging v1.3.0 compatibility | `test_fmr010_*` | no publication authority |
| VP Content proof/inventory defects and derivative lineage | FMR-017 | VP Content inventory/lineage gates | `test_fmr017_*` | no pursuit/policy/publication authority |
| Message-specific approval, recipient/send authority, duplicate/suppression/idempotency/kill switch | FMR-011 | Message Operations execution gate | `test_fmr011_*` | fail closed before external execution |
| Donor prompt injection cannot alter authority | FMR-012 | common security guard in all ten evaluation gates plus role governance | `test_fmr012_*` | identity/tool/source/approval/action/persistence unchanged |
| Historical v4.8.1 workflow cannot reactivate | FMR-013 | workflow_dispatch-only read-only historical workflow | `test_fmr013_*`; updated v4.8.1 regression | no historical republish/tag mutation |
| v4.8.2 has own exact-SHA publisher | FMR-013 | `release-v4.8.2.yml` | targeted workflow and post-merge release proof | write permission release job only |
| v4.8.1 receipt durable after release | FMR-014 | corrected historical receipt | `test_fmr014_*`; `test_release_state_v481.py` | tag/release external evidence separated from source receipt |
| Exhaustive donor disposition | FMR-015 | 49-row ledger | `test_fmr015_*` | untrusted donor evidence only |
| Fourth donor evidenced or blocked | FMR-016 | `source-governance-v4.8.2.md` | `test_fmr016_*` | `BLOCKED_SOURCE_IDENTIFICATION` |
| Runtime, roster, parentage, PPMD/Messaging remain unchanged | FMR-018 | no runtime/registry/shared-repo change | `test_fmr018_*`; package/drift/closure checks | runtime 4.0.0, QNAP 4.4.0 |

## Release verification

Completion requires the canonical CI and v4.8.2 targeted workflow to pass on the exact final candidate, followed by merge and external confirmation that `main`, tag `v4.8.2`, and GitHub Release `v4.8.2` all resolve to the same commit.
