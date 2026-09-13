# v4.8.4 Release Record Correction Security Review

Applicability: **TARGETED**  
Security result: **PASS WITH DOCUMENTED BASELINE ADVISORY**

## Scope

v4.8.4 changes documentation and GitHub Actions release authority only. It does not change runtime code, agents, Skills, MCP tools, authentication, OAuth, secrets, dependencies, network boundaries, databases, or QNAP production.

## Security properties

| Property | Required result |
|---|---|
| Historical publisher isolation | Every published SemVer workflow through v4.8.3 is manual-only and read-only |
| No historical release mutation | v4.8.3 tag and GitHub Release remain untouched |
| Least privilege | Only the v4.8.4 release job has `contents: write` |
| Release ordering | v4.8.4 publication depends on successful verification |
| Exact identity | v4.8.4 publishes against exact `GITHUB_SHA` |
| Main-push isolation | No historical SemVer workflow reacts automatically to the v4.8.4 merge commit |

## Trust boundary

The relevant boundary is GitHub Actions verification state to release-token authority. Historical workflows are verification-only and cannot publish. v4.8.4 defaults to `contents: read`; write permission exists only in the release job on a `main` push after the verify job succeeds.

## Baseline advisory

The pre-existing MCP npm baseline reports one moderate Hono advisory. v4.8.4 does not modify dependencies or runtime exposure. No new Critical or High finding is accepted by this PATCH.

## Residuals

- `BLOCKED_SOURCE_IDENTIFICATION` remains for the unresolved fourth donor source.
- GitHub connector branch-ref deletion remains unavailable and is housekeeping only.

## Disposition

**PASS WITH DOCUMENTED BASELINE ADVISORY**, subject to exact-head verification and post-merge proof that only canonical CI and v4.8.4 react to the integrated commit.
