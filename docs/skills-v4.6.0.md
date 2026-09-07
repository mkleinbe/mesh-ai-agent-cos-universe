# v4.6.0 Skill and Workspace Agent Manifest

## Updated repository-local Skill

`mesh-cfo` advances to implementation `1.2.0`. It adds deterministic core finance calculation execution, management FP&A, research execution, governed analytical composition, operating cadence, and finance-artifact production while preserving CFO L3 authority and human approval gates.

## External shared Skill entitlement

`mesh-data-analytics` is registered as an `EXTERNAL_SHARED_SKILL` consumed only by CFO with `ANALYTICAL_EXECUTION_ONLY` authority. It is not copied into `chatgpt/skills/`, is not an eleventh Workspace Agent, and cannot modify canonical facts or execute consequential external actions.

The pre-existing external `mesh-devils-advocate` capability remains available only to Chief of Staff and CRO with advisory-only authority.

## Package contents

The `mesh-cfo` Skill package contains:
- `SKILL.md`;
- `agents/openai.yaml`;
- `scripts/financial_math.py`;
- `references/role-contract.md`;
- `references/production-readiness.md`;
- financial decision, planning/unit-economics, model/valuation, research/evidence, and operating-cadence/artifact references.

## Version identity

- CFO implementation: `1.2.0`
- Repository capability release: `v4.6.0`
- Canonical runtime contract / legacy Workspace `repository_release`: `4.0.0`
- Production QNAP deployment: `4.4.0`
