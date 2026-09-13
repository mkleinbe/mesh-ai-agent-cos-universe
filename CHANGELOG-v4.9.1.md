# Changelog v4.9.1

Release date: September 13, 2026

## Added

- Registered `mesh-media-production`, `mesh-media-verification`, and `mesh-media-distribution` for CMO.
- Registered `mesh-media-production` for VP Content only.
- Added deterministic Media OS capability-registration evaluation proving governed `CHATGPT_SKILL_HANDOFF` execution.

## Fixed

- Reconciled the legacy enterprise-consulting regression with the approved Media OS registry expansion. The prior assertion incorrectly treated the new CMO/VP Content bindings as unauthorized drift and caused `main` CI to fail after PR #77 merged.
- Preserved the ten-agent organization, CMO L3 authority, VP Content L2 production authority, VP Content zero delegation authority, and human public-release boundary.
- Retired the already-published v4.9.0 workflow to read-only historical verification and moved sole exact-SHA SemVer publication authority to v4.9.1.

## Runtime and deployment

- Canonical Phase 1 authority/runtime contract remains `4.0.0`.
- QNAP production remains deployment release `4.4.0` until the verified current-source QNAP candidate is explicitly deployed and read back.
- No database migration, new agent principal, new delegation edge, or public-publishing authority is introduced.

## Security

- Review depth: TARGETED for registry/Skill authority, MCP handoff, release controls, and QNAP deployment provenance.
- Media OS capabilities remain Skill handoffs, not principals or authority sources.
- Existing protected credentials and TaskLedger authority are unchanged.
