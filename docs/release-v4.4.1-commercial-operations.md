# Release v4.4.1: Commercial Operations Orchestration Correction

## Summary

v4.4.1 is a repository and operating-control patch. It corrects Commercial Operations work-package construction, bounded recovery, scheduler drift, business-first executive reporting, and CMO/VP Content integration.

The QNAP Mesh CoS MCP production runtime remains 4.4.0. No QNAP deployment is part of this release.

## Material changes

- Canonical task dependencies are restricted by operating contract to actual predecessor task IDs.
- Legacy narrative-dependency defects use one deterministic dependency-clean successor with audit history preserved.
- Commercial Operations reports business result separately from technical health.
- CMO and VP Content participate through canonical parentage when authority/content context is relevant, without gaining Revenue Intelligence authority.
- The central Commercial Operations automation is restored to active weekday 08:00, 10:00, 12:00, and 16:00 ET operation.
- The existing event-driven Commercial HITL send executor remains separate and unchanged.

## Compatibility

- Canonical authority/runtime contract remains 4.0.0.
- QNAP deployment release remains 4.4.0.
- CoS machine action surface remains unchanged.
- Exactly 10 registered agents remain unchanged.
- No database migration, schema migration, provider credential change, Slack boundary change, or QNAP operator action is required.

## Verification

The release is acceptable when:

- repository CI passes;
- regression tests prove narrative dependency misuse reproduces a fail-closed block while dependency-clean work advances;
- current MCP identity, registry, owner execution, completion/verification separation, and audit chain pass;
- recovered banking and response occurrences remain verified;
- CMO and nested VP Content operating-model tasks are verified;
- TaskLedger operating/preflight/test evidence is reconciled;
- the Commercial Operations automation is enabled with the declared schedule and prompt contract;
- no unauthorized external action occurred.

## Release and deployment

Merge to `main`, then create semantic tag `v4.4.1` and a GitHub Release from the final main commit. This release does not build or deploy a new QNAP image. QNAP remains operator-controlled and unchanged.

## Rollback

If the automation contract produces incorrect routing, disable the Commercial Operations Scheduled Task, preserve canonical MCP state and TaskLedger evidence, restore the previous automation prompt from the TaskLedger prompt archive, and investigate the caller contract. Do not roll back the healthy QNAP runtime for an orchestration-only defect.
