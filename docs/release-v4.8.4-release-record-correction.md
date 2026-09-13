# v4.8.4 Release Record Correction

Release date: September 12, 2026

Repository release: `v4.8.4`  
Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged  
Production QNAP deployment: `4.4.0`, unchanged

## Purpose

v4.8.4 is a documentation and release-control PATCH. Final verification of v4.8.3 confirmed that the implementation correctly retired historical publisher authority, including v4.6.0, but the v4.8.3 changelog, release record, and gap audit omitted v4.6.0 from their explicit inventory.

v4.8.4 corrects that record without rewriting the already-published v4.8.3 tag or GitHub Release.

## Corrected v4.8.3 inventory

The v4.8.3 implementation retired publisher/write authority from these previously published workflows:

- v4.1.15
- v4.2.3
- v4.3.0
- v4.3.1
- v4.4.1
- v4.4.2
- v4.6.0
- v4.8.2

The current-source v4.8.3 records now match that implemented scope. The historical v4.8.3 tag remains immutable at its original source state.

## Release-control closeout

Because v4.8.3 is now published, its workflow is converted to manual, read-only historical verification. The systemic regression now requires every published SemVer workflow through v4.8.3 to be manual-only, read-only, and non-publishing.

v4.8.4 is the sole active SemVer publisher. Its release job receives `contents: write` only after the verification job succeeds and publishes against exact `GITHUB_SHA`.

## Capability boundary

No application/runtime behavior changes in v4.8.4. There are no changes to:

- ChatGPT Skill packages;
- Python `mesh_cos` runtime or version;
- agent registry, parentage, or decision rights;
- MCP catalog, authentication, transport, or connector scope;
- TaskLedger or Revenue Intelligence authority;
- QNAP production 4.4.0;
- shared PPMD Bot or Messaging releases;
- consequential send, publish, procurement, staffing, pricing, discount, deal, contract, or approval authority.

## Known blocker

`BLOCKED_SOURCE_IDENTIFICATION` remains for the unresolved fourth donor source. This PATCH neither resolves nor conceals that source-completeness blocker.
