# Changelog v4.8.1

## Release State Finalization

### Fixed

- Finalized the v4.8.0 verification receipt with actual merged-main, semantic tag, GitHub Release, and successful release-workflow evidence.
- Finalized the v4.8.0 security receipt so it no longer describes the already-published release as a candidate awaiting publication.
- Retired the v4.8.0 publisher from automatic `main` execution to prevent an already-published tag from being compared against later PATCH commits.
- Added a v4.8.1 release-state regression and dedicated semantic release workflow.
- Updated repository release documentation to keep the current release identity synchronized.

### Preserved

- No agent behavior change.
- No registry, authority, Skill, method, MCP, connector, source-authority, or external-action change.
- Canonical Phase 1 authority/runtime contract remains `4.0.0`.
- Production QNAP remains `4.4.0`.
- Exactly 10 registered agents remain.
- No QNAP deployment is part of this patch.
- v4.8.0 remains the functional-method feature release and historical evidence boundary.
