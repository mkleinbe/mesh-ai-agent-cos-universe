# Changelog v4.8.4

## Fixed

- Corrected the v4.8.3 current-source changelog, release record, and gap audit to explicitly include v4.6.0 in the historical publisher inventory actually retired by the v4.8.3 implementation.
- Preserved the already-published v4.8.3 tag and GitHub Release without retargeting or mutation.
- Retired the now-published v4.8.3 workflow to read-only `workflow_dispatch` historical verification.
- Advanced the systemic publisher invariant so every published SemVer workflow through v4.8.3 is manual-only, read-only, and non-publishing.
- Established v4.8.4 as the sole active SemVer publisher with exact `GITHUB_SHA` binding and release-write permission isolated to the post-verification job.

## Unchanged

- Canonical Phase 1 authority/runtime contract `4.0.0`.
- Production QNAP deployment `4.4.0`.
- Exactly 10 Phase 1 agents and established parentage.
- All v4.8.2 ChatGPT Skill packages and behavior-level remediation.
- TaskLedger, Revenue Intelligence, L4/L5, and `COMPLETED != VERIFIED` authority boundaries.
- No runtime, MCP, OAuth, credential, connector, network, database, dependency, or QNAP change.

## Known blocker

The unresolved fourth donor remains `BLOCKED_SOURCE_IDENTIFICATION`. v4.8.4 does not claim four-source completeness.
