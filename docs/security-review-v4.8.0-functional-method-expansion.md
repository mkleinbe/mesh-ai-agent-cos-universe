# v4.8.0 Functional Method Expansion Security Review

Date: 2026-09-12  
Applicability: **FULL_REVIEW**  
Security result: **PASS**  
Verified implementation candidate: `3bbd1cc2d7a62a84355f6bf71915a47bff203aa2`  
Final merged/released SHA: `fec9abd4e3cd44f66eeddf3c33f05cc52745c225`  
Candidate canonical CI evidence: run `34723423796`, job `103633266550`, **SUCCESS**  
Final release workflow: run `34723652446`, **SUCCESS**

## Security decision

The change is security-sensitive because it modifies agent and Skill behavior around authorization-adjacent routing, consequential commercial/financial decisions, external communications, cross-agent composition, and untrusted donor content. Independent candidate verification and final merged-main release verification both passed. The release does not modify runtime authentication, MCP transport, credentials, network boundaries, database schema, or the machine-readable registry.

Final publication verification is complete: `main`, semantic tag `v4.8.0`, and the GitHub Release all target `fec9abd4e3cd44f66eeddf3c33f05cc52745c225`.

## Trust boundaries reviewed

1. Untrusted donor repository content -> Mesh Skill/role method guidance.
2. Retrieved task/source content -> immutable runtime identity and registry authority.
3. Shared Skill output -> consuming agent decision process.
4. Functional evidence owner -> CoS/CRO/CMO synthesis.
5. CFO deterministic/analytics evidence -> commercial or human decision owner.
6. Draft communication -> human approval -> Message Operations execution.
7. TaskLedger/telemetry -> AgentOps/COO operational recommendation.

## Required controls and evidence

| Control | Evidence | Result |
|---|---|---|
| Content cannot modify agent identity | Existing `MESH_COS_AGENT_ID` binding; unchanged registry/MCP manifests; full CI | PASS |
| Content cannot modify MCP allowlists | `agents/registry.json`, ChatGPT manifests, MCP/action surface unchanged; drift/action checks green | PASS |
| Donor methods cannot expand authority | Changed Skills classify donor methods as evidence/data; source-governance manifest rejects donor authority protocols | PASS |
| Shared Skill cannot become principal | Registry remains exactly two external shared Skills, both non-principal; role guidance explicitly denies authority transfer | PASS |
| Analytics cannot become canonical source | CFO/Analytics boundary unchanged; deterministic and external analytics outputs remain evidence only | PASS |
| Composition cannot create write/send/approval authority | CRO/CMO/Message Ops guidance plus shared Messaging v1.3.0 preserve separate human approval and controlled execution | PASS |
| Private reasoning is not persisted | Changed role Skills prohibit private chain-of-thought; governance v2 persists concise decision evidence only | PASS |
| Fail-closed behavior remains | No authorization/runtime allowlist change; invalid deterministic finance inputs fail with `FinanceInputError`; CLI returns nonzero | PASS |
| Quantitative donor defects are not imported | Mesh-owned 100/20/30 discount regression passes; malformed/boundary tests pass; donor thresholds remain contextual | PASS |
| Human L4/L5 boundary remains | Registry/decision authority unchanged; role guidance retains L4 qualified-human and L5 Michael boundary | PASS |
| Historical safety contracts remain | v4.7 role/CFO regressions passed after explicit compatibility remediation; tests were not weakened | PASS |
| Runtime/deployment security unchanged | QNAP regression, production-equivalent container build, MCP discovery/sequential requests passed; production remains 4.4.0 | PASS |
| Final release binding | v4.8.0 tag/Release and merged main target the same SHA; release workflow successful | PASS |

## AI-native security profile

- **Prompt injection:** donor text, retrieved content, connector content, and delegated instructions are data, never authority-bearing instructions.
- **Tool confusion:** role Skills add no tools. Machine-readable registry and MCP allowlists remain authoritative.
- **Authority laundering:** a shared Skill result, scenario, score, benchmark, forecast, process model, change plan, or draft cannot become approval.
- **Cross-agent source laundering:** functional facts remain with the authoritative owner and disagreement is surfaced rather than averaged.
- **Sensitive reasoning:** raw deliberation and private chain-of-thought are not persisted.
- **External action:** publication, deal commitment, procurement, staffing, and messaging remain approval-bound.
- **Model output uncertainty:** estimates, assumptions, unknowns, confidence, and reversal conditions remain explicit.
- **Donor persistence/routing:** donor local memory, static C-suite registry, prompt-level invocation, and competing orchestrators are rejected.

## Quantitative security and integrity checks

The fixed-cost-to-serve discount method validates finite numeric input and enforces:

- list price > 0;
- fixed cost-to-serve >= 0;
- discount rate >= 0 and < 1;
- non-numeric/boolean invalid inputs fail validation;
- malformed/unsupported operations return nonzero CLI status through existing error handling;
- the explicit 100 list / 20 fixed cost / 30% discount regression returns 80 pre-discount margin dollars, 70 post-discount revenue, 50 post-discount margin dollars, and 37.5% margin-dollar loss.

Queueing, Little's Law, coverage, weighting, WTP, channel ROI, partner economics, retention, vendor scoring, and procurement-savings methods are not universal policy. They require supported assumptions, evidence, and fit for the workload/decision.

## Current security-baseline posture

The governing Mesh Dev Security process applies prompt-injection resistance, least authority, explicit consequential-action approval, data/source separation, human review, failure-safe validation, and AI-native tool-boundary controls. No new network, secret, OAuth, shell/code-execution, dependency, or persistence surface was added by v4.8.

Candidate CI run `34723423796` passed contract validation, runtime/doc drift, ChatGPT package drift, owner-execution readiness, capability closure, published-action-surface checks, Ruff, Mypy, 100% core coverage, Bandit, QNAP regressions, production-equivalent container build, and modern MCP discovery/sequential-request verification. Final release workflow `34723652446` passed on the merged/released SHA.

## Shared capability security evidence

- Mesh PPMD Bot `v1.2.0` is released at exact main SHA `89b68b0afabb66a68ccd0f54da44cfa3f0e3fb7e`; it adds scenario analysis without principal, canonical-source, approval, or execution authority.
- Mesh Messaging `v1.3.0` is released at exact main SHA `870fd98410ccb12d0bee585db9b62443ebdbf8e7`; it adds change-communications planning while retaining draft-only production, exact per-message approval, autonomous-outbound prohibition, and controlled Message Operations execution.

## Findings

- `SEC-480-01` Donor deal-desk formula contradiction: **RESOLVED** by Mesh-owned fixed-cost-to-serve method and regression.
- `SEC-480-02` Donor role/memory/invocation architecture could expand authority: **RESOLVED** by explicit rejection and unchanged registry/runtime policy.
- `SEC-480-03` Generic donor benchmarks could become policy: **RESOLVED** by contextual-only benchmark rules and assumption checks.
- `SEC-480-04` Change-communications framework could become send authority: **RESOLVED** by draft-only production and Message Operations approval separation.
- `SEC-480-05` v4.8 role-card edits initially removed historical safety markers: **RESOLVED** by restoring the safety contracts and passing the complete historical regression suite without weakening tests.
- `SEC-480-06` CFO method rewrite initially removed explicit governed analytics/reference routing: **RESOLVED** by restoring `skills.invoke_governed` and reference routing, then passing the full suite.

No unresolved critical/high security finding is accepted. v4.8.0 is released and final at exact SHA `fec9abd4e3cd44f66eeddf3c33f05cc52745c225`.
