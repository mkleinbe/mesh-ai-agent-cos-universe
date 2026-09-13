# v4.8.3 Historical Publisher Retirement Security Review

Applicability: **TARGETED**  
Security result: **PASS WITH DOCUMENTED BASELINE ADVISORY**

## Scope

This PATCH changes GitHub Actions release control only. It does not change runtime code, agent/Skill behavior, registry state, MCP tools, authentication, OAuth, secrets, dependencies, network boundaries, database state, or production QNAP deployment.

## Threats reviewed

| Threat | Control | Result |
|---|---|---|
| Historical release republish | Every published historical SemVer workflow through v4.8.2 is manual-only and contains no executable `gh release create` | PASS |
| Excess GitHub token privilege | Historical workflows use `contents: read`; no historical job retains `contents: write` | PASS |
| Historical tag or Release retarget | Existing tags/Releases remain immutable and are never rewritten by v4.8.3 | PASS |
| Current release confusion | Only v4.8.3 owns a SemVer publisher; release is exact `GITHUB_SHA` | PASS |
| Main-push fan-out | Systemic regression blocks historical SemVer workflows from active `main` triggers | PASS subject to post-merge run observation |
| Release-before-verification | v4.8.3 release job depends on the full verify job | PASS |

## Least privilege

The v4.8.3 workflow defaults to `contents: read`. `contents: write` exists only on the `release` job, which is restricted to a `push` on `main` and depends on successful verification.

Historical workflows are intentionally read-only even when manually dispatched. Comment-only strings recording former publisher/trigger behavior are non-executable and ignored by the systemic active-YAML regression.

## Baseline advisory

The pre-existing MCP dependency baseline continues to report one moderate Hono advisory during npm audit. v4.8.3 does not modify dependencies or runtime exposure. No new Critical or High finding is accepted.

## Residuals

- Fourth donor source remains `BLOCKED_SOURCE_IDENTIFICATION`, unrelated to release-control authority.
- GitHub connector branch-ref deletion remains unavailable. This is housekeeping, not release authority or runtime risk.

## Disposition

**PASS WITH DOCUMENTED BASELINE ADVISORY**, subject to exact-head CI and post-merge observation that no historical SemVer workflow reacts automatically to the v4.8.3 `main` commit.
