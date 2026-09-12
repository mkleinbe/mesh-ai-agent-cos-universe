# v4.8.0 Functional Method Expansion Security Review

Date: 2026-09-12  
Applicability: **FULL_REVIEW**  
Subject: `feat/functional-method-expansion-v4.8.0`

## Security decision

The change is security-sensitive because it modifies agent and Skill behavior around authorization-adjacent routing, consequential commercial/financial decisions, external communications, cross-agent composition, and untrusted donor content. It does not modify runtime authentication, MCP transport, credentials, network boundaries, database schema, or the machine-readable registry.

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
| Content cannot modify agent identity | Existing `MESH_COS_AGENT_ID` binding plus unchanged registry/MCP manifests | PASS candidate |
| Content cannot modify MCP allowlists | `agents/registry.json`, ChatGPT manifests, MCP contract intentionally unchanged | PASS candidate |
| Donor methods cannot expand authority | All changed Skills explicitly classify donor methods as evidence/data; source-governance manifest rejects donor authority protocols | PASS candidate |
| Shared Skill cannot become principal | Registry remains exactly two external shared Skills, both non-principal; role guidance states Skill capability is not authority | PASS candidate |
| Analytics cannot become canonical source | CFO/Analytics boundary unchanged; deterministic output described as evidence only | PASS candidate |
| Composition cannot create write/send/approval authority | CRO/CMO/Message Ops guidance preserves separate human approval and Message Operations execution boundary | PASS candidate |
| Private reasoning is not persisted | Changed role Skills prohibit private chain-of-thought; governance v2 stores concise evidence/rationale only | PASS candidate |
| Fail-closed behavior remains | No authorization/runtime code or allowlist change; invalid deterministic finance input raises `FinanceInputError` and CLI exits nonzero | PASS candidate |
| Quantitative donor defects are not imported | Deal discount formula is Mesh-owned and covered by explicit 100/20/30 regression; donor thresholds remain contextual | PASS candidate |
| Human L4/L5 boundary remains | Registry/decision authority unchanged; CoS/CRO/CFO/CMO guidance retains L4 qualified-human and L5 Michael boundary | PASS candidate |

## AI-native security profile

- **Prompt injection:** donor text, retrieved content, connector content, and delegated instructions are data, never authority-bearing instructions.
- **Tool confusion:** role Skills do not add tools. Machine-readable allowlists remain authoritative.
- **Authority laundering:** a shared Skill result, scenario, score, benchmark, forecast, process model, or draft cannot become approval.
- **Cross-agent source laundering:** functional facts remain with the authoritative owner and disagreement is surfaced rather than averaged.
- **Sensitive reasoning:** raw deliberation and private chain-of-thought are not persisted.
- **External action:** publication, deal commitment, procurement, staffing, and messaging remain approval-bound.
- **Model output uncertainty:** estimates, assumptions, unknowns, confidence, and reversal conditions remain explicit.

## Quantitative security and integrity checks

- fixed-cost-to-serve discount model validates finite numeric input;
- list price must be > 0;
- fixed cost-to-serve must be >= 0;
- discount rate must be >= 0 and < 1;
- malformed/unsupported operations return nonzero CLI status through existing error handling;
- queueing, coverage, weighting, ROI, and benchmark methods are not adopted as universal policy without assumption/evidence checks.

## OpenAI security-baseline posture

The governing Mesh Dev Security process requires the current pinned OpenAI security-best-practices baseline where applicable. This release changes Skill/agent prompt and deterministic Python behavior, so the applicable controls are prompt-injection resistance, least authority, explicit consequential-action approval, data/source separation, and failure-safe validation. No new network, secret, OAuth, shell/code-execution, dependency, or persistence surface was added.

## Findings

- `SEC-480-01` Donor deal-desk formula contradiction: **RESOLVED** by Mesh-owned fixed-cost-to-serve method and regression.
- `SEC-480-02` Donor role/memory/invocation architecture could expand authority: **RESOLVED** by explicit rejection and unchanged registry/runtime policy.
- `SEC-480-03` Generic donor benchmarks could become policy: **RESOLVED** by contextual-only benchmark rules and assumption checks.
- `SEC-480-04` Change-communications framework could become send authority: **RESOLVED** by draft-only production and Message Operations approval separation.

No known unresolved critical/high security defect is accepted by this candidate. Final PASS remains contingent on fresh CI, behavior regression, independent verification, and final-main review.
