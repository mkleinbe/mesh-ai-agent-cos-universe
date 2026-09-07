# Release v4.5.0: CFO Financial Analysis Capability

## Summary

`v4.5.0` is a MINOR repository capability release that expands the governed analytical depth of the Mesh CFO from implementation version `1.0.0` to `1.1.0`.

The release adds reusable methods for investment business cases, driver-based forecasting, unit economics, supported cash/runway and working-capital analysis, model quality assurance, bounded valuation and statement analysis, sensitivity/scenarios, and evidence-backed financial research.

## What does not change

- canonical Phase 1 runtime contract remains `4.0.0`;
- production QNAP Mesh CoS MCP runtime remains `4.4.0`;
- exactly 10 agents remain registered;
- CFO parent remains `cos`;
- CFO accountable domain remains `engagement finance and FP&A`;
- CFO decision authority remains L3 recommendation within supported source scope;
- CFO max delegation depth remains 1;
- CFO MCP allowlist is unchanged;
- Google Drive remains read-only and restricted to approved engagement-finance artifacts;
- no database/schema migration;
- no new dependency, credential, API, connector, container, or QNAP operator action;
- no pricing, trading, spending, hiring, contract, or external-write approval is granted.

## Compatibility considerations

Existing engagement-finance prompts remain compatible. The expanded Skill adds methods without changing existing tool schemas or MCP behavior. Any workflow that treated CFO implementation version as exactly `1.0.0` must accept the new semantic implementation version `1.1.0`; repository package/runtime version remains `4.0.0` by design.

## Security

Security profile: TARGETED. See `docs/security-review-v4.5.0-cfo-financial-analysis.md`.

The most material new risk is authority laundering through donor instructions, financial benchmarks, or model-generated recommendations. The release explicitly classifies donor and external material as reference evidence only, prohibits benchmark-as-policy behavior, prohibits persisted private financial reasoning, and keeps the existing MCP and connector surfaces fixed.

## Verification

Required release gates:

```bash
python scripts/validate-contracts.py
python scripts/check-runtime-doc-drift.py
python scripts/check-chatgpt-packages.py
python scripts/check-owner-execution-readiness.py
python scripts/check-capability-closure.py
python scripts/check-published-action-surface.py
ruff check src
ruff check tests scripts --select E9,F63,F7,F82
mypy src --check-untyped-defs
pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100
bandit -q -r src -lll
python -m compileall -q src
pytest -q tests/evaluations/test_cfo_financial_analysis_v450.py
```

GitHub CI also retains the existing Node/MCP, QNAP shell, packaging, security, and transport regression gates.

## Release lifecycle

1. Merge the verified `v4.5.0` pull request to `main` only after CI is green and review threads are resolved.
2. The `v4.5.0 CFO Financial Analysis Capability` release workflow reruns full release verification against the merged main SHA.
3. Only after verification succeeds, the workflow creates semantic tag `v4.5.0` and the GitHub Release from that exact SHA.
4. Confirm main, tag, release target, release notes, CFO registry `1.1.0`, and Workspace Agent manifest identify the same intended state.

## Rollback

This release changes repository configuration and Skill guidance only. If a post-release regression is found, restore the prior CFO registry, role card, Workspace Agent manifest, Skill, and reference set from the preceding main commit. Do not restart or roll back the healthy QNAP runtime for a Skill-only defect.

## Known limitations

The CFO still lacks enterprise GL, treasury, bank-balance, tax, audit, trading, brokerage, and unrestricted market-data authority. External or current finance data must be separately authorized and source-qualified before use. Analytical confidence remains dependent on source quality, freshness, definitions, and assumptions.
