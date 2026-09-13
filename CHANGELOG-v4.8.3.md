# Changelog v4.8.3

## Fixed

- Retired all remaining published historical SemVer workflows that still retained executable `gh release create` logic or release-write permission.
- Converted v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.4.1, v4.4.2, v4.6.0, and v4.8.2 to read-only `workflow_dispatch` historical verification.
- Added a systemic regression requiring every already-published v4.x SemVer workflow through v4.8.2 to be manual-only, read-only, and non-publishing.
- Established v4.8.3 as the sole current SemVer publisher with exact `GITHUB_SHA` binding and `contents: write` isolated to the post-verification release job.

## Why this PATCH exists

During post-release verification of v4.8.2, historical v4.4.1 and v4.4.2 workflows reacted to the new `main` commit. Their idempotency checks correctly left existing tags and Releases unchanged, but the workflows still possessed publication capability. The follow-up audit found the same retained publisher logic in v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.6.0, and v4.8.2. v4.8.3 removes that unnecessary authority systemically.

## Unchanged

- All v4.8.2 Functional Method behavioral remediation and the ten updated ChatGPT Skill packages.
- Canonical Phase 1 authority/runtime contract `4.0.0`.
- Production QNAP deployment `4.4.0`.
- Exactly 10 Phase 1 agents and established parentage.
- TaskLedger and Revenue Intelligence authority.
- L4/L5 and `COMPLETED != VERIFIED` controls.
- Shared PPMD Bot v1.2.0 and Mesh Messaging v1.3.0.
- No MCP, OAuth, credential, connector, network, database, dependency, or QNAP runtime change.

## Known blocker

The fourth donor source remains `BLOCKED_SOURCE_IDENTIFICATION`. v4.8.3 does not claim four-source completeness.
