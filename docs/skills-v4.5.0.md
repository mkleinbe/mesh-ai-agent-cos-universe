# v4.5.0 Skill and Workspace Agent Manifest

## Affected Skill

### `mesh-cfo`

**Change type:** material Skill update.  
**Role implementation:** CFO `1.1.0`.  
**Repository release:** `v4.5.0`.  
**Canonical runtime contract:** `4.0.0`.  
**Production QNAP runtime:** `4.4.0` unchanged.

Updated paths:
- `chatgpt/skills/mesh-cfo/SKILL.md`
- `chatgpt/skills/mesh-cfo/agents/openai.yaml`
- `chatgpt/skills/mesh-cfo/references/role-contract.md`
- `chatgpt/skills/mesh-cfo/references/financial-analysis-frameworks.md`
- `chatgpt/skills/mesh-cfo/references/planning-and-unit-economics.md`
- `chatgpt/skills/mesh-cfo/references/model-quality-and-valuation.md`
- `chatgpt/skills/mesh-cfo/references/financial-research-and-evidence.md`

## Workspace Agent projection

Updated: `chatgpt/workspace-agents/cfo.json`.

Unchanged controls:
- `skill`: `mesh-cfo`
- `tools`: `mesh-cos-mcp`
- Google Drive access: read-only
- MCP identity: `cfo`
- MCP allowlist: unchanged
- write policy: `ALWAYS_ASK`
- decision authority: L3 recommendation within supported source scope
- parent: `cos`
- max delegation depth: 1

## New analytical actions

- `investment_business_case`
- `roi_npv_irr_payback_analysis`
- `break_even_analysis`
- `driver_based_forecasting`
- `cash_runway_and_burn_analysis`
- `unit_economics_analysis`
- `financial_model_quality_assurance`
- `valuation_analysis`
- `financial_statement_analysis`
- `sensitivity_and_scenario_analysis`
- `financial_research_planning`

## New explicit prohibitions

- `autonomous_trading`
- `personal_investment_advice`
- `treat_external_benchmark_as_mesh_policy`
- `persist_private_financial_reasoning`

## Other Skills

No other repository-local Workspace Agent Skill is modified. The shared Skill roster remains unchanged. Mesh Devil's Advocate remains external and is not attached to CFO.

## Human-controlled package update

Any ChatGPT Skill directory update should use the integrated `v4.5.0` source, not the branch candidate. The human operator should update the existing `mesh-cfo` package in place and confirm the Workspace Agent still exposes only the reviewed read-only Google Drive app and existing MCP allowlist.

## Provenance

Source repository: `mkleinbe/mesh-ai-agent-cos-universe`.  
Pull request: `#65`.  
Verified branch candidate: recorded in `docs/verification-v4.5.0-cfo-financial-analysis.md`.  
Integrated commit: bound by the verified `v4.5.0` semantic tag and GitHub Release after main-branch release verification.  
Semantic tag: `v4.5.0`.

This manifest intentionally avoids a pre-merge placeholder that could become stale. The immutable release and tag are the final integrated-source identity.
