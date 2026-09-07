# Changelog v4.5.1

## CFO Financial Analysis Release Closeout

### Fixed
- Finalized the v4.5.0 CFO Financial Analysis verification receipt after successful semantic tag and GitHub Release publication.
- Synchronized top-level repository release pointers with the completed release state.
- Added a patch-release regression gate so release documentation cannot remain in a pre-release state after publication.

### Verified
- CFO implementation remains `1.1.0` with no behavioral or authority change from v4.5.0.
- Canonical Phase 1 runtime contract remains `4.0.0`.
- Production QNAP Mesh CoS MCP remains `4.4.0`.
- Registered agent roster remains exactly 10.
- CFO MCP allowlist, Google Drive read-only scope, L3 decision authority, human approval gates, and completion-versus-verification boundary remain unchanged.
- No dependency, credential, connector, schema, runtime, QNAP, or external-action change.

### Release history
- `v4.5.0` remains the feature release that introduced CFO Financial Analysis capability.
- `v4.5.1` is a documentation and release-control closeout patch only.
