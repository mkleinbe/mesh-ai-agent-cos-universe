# v4.8.0 Functional Method Expansion Verification

## Verification objective

Independently prove the actual v4.8.0 candidate against FME-001 through FME-024, FULL_REVIEW security requirements, quantitative-method integrity, legacy regressions, documentation synchronization, and release identity.

## Bound subject

- repository: `mkleinbe/mesh-ai-agent-cos-universe`
- candidate branch: `feat/functional-method-expansion-v4.8.0`
- baseline: `26ad1edcf1952d0203a25378987f42af6560d637`
- BDD: `specs/functional-method-expansion-v4.8.0.feature`
- security receipt: `docs/security-review-v4.8.0-functional-method-expansion.md`
- requirements: `docs/requirements-trace-v4.8.0.md`

## Required independent checks

1. `python scripts/validate-contracts.py`
2. `python scripts/check-runtime-doc-drift.py`
3. `python scripts/check-chatgpt-packages.py`
4. `python scripts/check-owner-execution-readiness.py`
5. `python scripts/check-capability-closure.py`
6. `python scripts/check-published-action-surface.py`
7. `ruff check src`
8. `ruff check tests scripts --select E9,F63,F7,F82`
9. `mypy src --check-untyped-defs`
10. `pytest --cov=mesh_cos --cov-report=term-missing --cov-report=xml --cov-fail-under=100`
11. `bandit -q -r src -lll`
12. `python -m compileall -q src chatgpt/skills/mesh-cfo/scripts/financial_math.py tests/evaluations/test_functional_method_expansion_v480.py`
13. `pytest -q tests/evaluations/test_phase1_role_model_consistency.py`
14. `pytest -q tests/evaluations/test_cfo_financial_analysis_v450.py`
15. `pytest -q tests/evaluations/test_cfo_release_closeout_v451.py`
16. `pytest -q tests/evaluations/test_cfo_release_state_v452.py`
17. `pytest -q tests/evaluations/test_cfo_execution_v460.py`
18. `pytest -q tests/evaluations/test_enterprise_consulting_skill_consumption_v470.py`
19. `pytest -q tests/evaluations/test_functional_method_expansion_v480.py`
20. MCP TypeScript `npm ci` and `npm run check`.

## Independent acceptance matrix

| Scope | Evidence required | Pre-release state |
|---|---|---|
| FME-001..003 governance | registry/package/runtime regression | PENDING fresh CI |
| FME-004..009 CoS | v4.8 evaluation + source inspection | PENDING fresh CI |
| FME-010..011 AgentOps | v4.8 evaluation + source inspection | PENDING fresh CI |
| FME-012 Answer Desk | v4.8 evaluation + source inspection | PENDING fresh CI |
| FME-013..017 CRO | v4.8 evaluation + quantitative regression | PENDING fresh CI |
| FME-018 CFO | deterministic regression + finance legacy tests | PENDING fresh CI |
| FME-019..020 COO/Steward | v4.8 evaluation + source inspection | PENDING fresh CI |
| FME-021..023 CMO/Content/Message Ops | v4.8 evaluation + shared Messaging release evidence | PENDING shared release |
| FME-024 security | FULL_REVIEW + drift/allowlist checks | PENDING fresh CI |
| PPMD shared method | PPMD v1.2.0 CI/tag/release | PENDING shared release |
| Documentation/release identity | docs checks + tag/main alignment | PENDING publication |

## Release claim boundary

This document is intentionally not marked PASS until fresh candidate checks, merged-main checks, semantic tag, GitHub Release, and final target-SHA alignment are observed. The final verification receipt must replace the pending states with actual run IDs and commit SHAs.
