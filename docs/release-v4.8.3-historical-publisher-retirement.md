# v4.8.3 Historical Publisher Retirement

Release date: September 12, 2026

Repository release: `v4.8.3`  
Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged  
Production QNAP deployment: `4.4.0`, unchanged

## Purpose

v4.8.3 is a release-control-only PATCH discovered during independent verification of v4.8.2. It removes unnecessary publication authority from already-published historical workflows and makes the release-control rule systemic: a published historical release may be manually verified, but only the current release workflow may publish.

## Defect discovered after v4.8.2 publication

The v4.8.2 `main` push also triggered historical v4.4.1 and v4.4.2 workflows. Both exited safely because their Releases already existed, and neither historical tag nor Release target changed. However, both workflows still retained `contents: write` and `gh release create`. A repository-wide audit found equivalent stale publisher logic in v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.6.0, and v4.8.2.

That state was unnecessarily privileged and violated the durable rule that future releases own their own publisher.

## Remediation

The following published workflows are converted to `workflow_dispatch` only, `contents: read`, with no executable publisher:

- v4.1.15
- v4.2.3
- v4.3.0
- v4.3.1
- v4.4.1
- v4.4.2
- v4.6.0
- v4.8.2

The remaining historical SemVer workflows were already manual/read-only. `tests/evaluations/test_historical_release_workflows_v483.py` asserts the complete published workflow set through v4.8.2 is manual-only, read-only, and non-publishing.

## Integrity

Historical tags and GitHub Releases are not retargeted, deleted, recreated, or mutated. v4.8.3 has its own exact-SHA publisher. The release job alone receives `contents: write` after the full verify job succeeds.

## Capability boundary

No Skill package changes are made in v4.8.3. The ten installable ChatGPT Skills changed by the remediation remain exactly the v4.8.2 packages and the v4.8.2 release bundle remains the manual-update artifact.

No runtime, registry, MCP, QNAP, shared capability, source authority, or consequential-action authority changes are introduced.

## Known blocker

`BLOCKED_SOURCE_IDENTIFICATION`: the fourth donor source remains unavailable. v4.8.3 does not change or conceal that source-completeness blocker.

## Record correction

v4.8.4 corrects the prior source/release-record omission that failed to list v4.6.0 even though the v4.8.3 implementation did retire its historical publisher. The published v4.8.3 tag remains immutable; this current-source record states the complete implemented inventory.
