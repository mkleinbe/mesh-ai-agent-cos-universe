# v4.8.3 Historical Publisher Retirement Verification

Verification status: **PASS WHEN EXACT-CANDIDATE GATES ARE GREEN**  
Publication proof model: **EXTERNAL MAIN == TAG == GITHUB RELEASE TARGET**

## Durable model

This source receipt defines the v4.8.3 verification requirements without embedding a self-referential final commit SHA. GitHub Actions supplies exact candidate identity through `GITHUB_SHA`, and final publication is proven externally after merge.

## Exact-candidate gates

The final PR head must pass:

- canonical repository CI;
- the dedicated v4.8.3 workflow;
- full pytest at the 100% `mesh_cos` coverage gate;
- the systemic historical publisher regression;
- v4.8.2 behavioral remediation regressions;
- v4.8.0 structural regressions;
- v4.8.1 historical release-state regressions;
- contract, runtime/documentation, package, capability-closure, owner-readiness, and published-action-surface checks;
- Ruff, mypy, Bandit, and compileall;
- QNAP POSIX regressions;
- production-equivalent 4.4.0 container build;
- modern MCP discovery and sequential requests.

## Systemic release-control acceptance

Every published SemVer workflow through v4.8.2 must have active YAML satisfying all of the following:

1. `workflow_dispatch` is available for historical verification.
2. No active `main` push trigger exists.
3. No active pull-request trigger exists.
4. No executable `gh release create` remains.
5. Permissions are `contents: read`.
6. No active `contents: write` remains.

The v4.8.3 workflow must be the sole SemVer publisher and bind publication to exact `GITHUB_SHA`.

## Post-merge proof

Completion requires:

- post-merge canonical CI green;
- v4.8.3 verify and release jobs green;
- no historical SemVer release workflow automatically triggered by the v4.8.3 `main` commit;
- current `main`, tag `v4.8.3`, and GitHub Release `v4.8.3` target all equal the same integrated SHA.

## Capability and runtime boundary

No ChatGPT Skill package content changes in v4.8.3. The v4.8.2 ten-Skill bundle remains the manual Skill update artifact. Canonical runtime remains 4.0.0 and production QNAP remains 4.4.0.

## Known blocked requirement

`BLOCKED_SOURCE_IDENTIFICATION` remains for the unresolved fourth donor source. This release-control PATCH neither resolves nor conceals that blocker.
