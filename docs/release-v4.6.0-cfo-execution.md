# v4.6.0 CFO Zero-Defect Execution Remediation

## Release intent

Close the P0-P2 defects and material gaps identified after the v4.5.x CFO capability expansion while preserving Mesh financial authority boundaries.

## Shipped

- CFO implementation `1.2.0` with engagement finance plus approved management FP&A analytical scope.
- Deterministic finance calculator for NPV, IRR, simple/discounted payback, break-even, runway, contribution margin, and LTV:CAC.
- CFO-only external `mesh-data-analytics` shared Skill for approved spreadsheet/model analysis, quantitative research, validation, visualization, and durable finance artifacts.
- Financial research execution, finance-artifact production, and explicit weekly/monthly/quarterly CFO cadence.
- Behavior-level BDD/evaluation scenarios rather than text-presence-only proof.
- Manual-only historical v4.5.x release workflows so later main releases cannot be failed by stale current-state assertions.
- Explicit version identity separating repository release, CFO implementation, canonical runtime, and production deployment.

## Preserved

- exactly 10 registered agents;
- CFO L3 recommendation authority;
- canonical Mesh Proposals - Engagement P&L Tracker source;
- existing CFO MCP allowlist;
- Google Drive read-only app scope;
- human-only approval tools and L4/L5 approval gates;
- no enterprise GL, treasury, tax, audit, bank-balance, autonomous trading, personal investment advice, or private-reasoning persistence.

## Runtime/deployment

- Repository capability release: `v4.6.0`
- CFO implementation: `1.2.0`
- Canonical Phase 1 runtime contract: `4.0.0`
- Production QNAP deployment: `4.4.0`, unchanged
- New MCP tool: none
- New schema migration: none
- New credential: none
- QNAP deployment/restart: none

## Release gate

The release workflow must run full repository CI plus `tests/evaluations/test_cfo_execution_v460.py`, historical CFO compatibility tests, security checks, current-source artifact build, and package validation. Release publication must target the exact final `main` SHA.
