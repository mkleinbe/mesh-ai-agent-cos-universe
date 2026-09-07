# Material Turn v4.5.1: CFO Financial Analysis Release Closeout

## Executive summary

v4.5.1 is a documentation and release-control patch that synchronizes repository records with the successfully published v4.5.0 CFO Financial Analysis release. It changes no CFO behavior or production runtime.

## Trigger

Final release reconciliation proved that v4.5.0 main CI, dedicated release verification, semantic tag, and GitHub Release all succeeded on SHA `075eb8de04d6035a16ff2b6a24d2106ef8783b95`. The in-repository v4.5.0 verification receipt still contained pre-publication wording and therefore no longer matched the actual release state.

## Scope

In scope:
- finalize the v4.5.0 verification receipt;
- synchronize README, RELEASE, and SECURITY current-release pointers;
- add v4.5.1 changelog, release contract, release authorization, regression test, and release workflow;
- verify and publish a patch release from final main.

Out of scope:
- CFO behavioral changes;
- agent-registry changes;
- Skill-method changes;
- MCP/runtime changes;
- connector or credential changes;
- QNAP deployment;
- source-authority or human-approval changes.

## Root cause

The v4.5.0 verification receipt was generated before semantic publication so it could travel with the verified candidate. After the release-control fix merged and the release workflow succeeded, the receipt became historically incomplete because it still described semantic release as gated.

## Before / after

Before: v4.5.0 was actually released, but one repository verification document still described the final publication gate as pending.

After: repository documentation explicitly records v4.5.0 as released, points current repository state to v4.5.1 closeout, and preserves v4.5.0 as the feature release.

## Architecture and authority impact

None. The v4.5.0 architecture diagrams remain authoritative for CFO Financial Analysis. v4.5.1 changes only documentation, tests, and release automation.

## Security impact

No new trust boundary, secret, package, network, connector, tool, identity, persistence, or external action. Security classification: documentation-only patch with full regression verification retained.

## Compatibility

Backward compatible. CFO remains implementation `1.1.0`; canonical Phase 1 runtime remains `4.0.0`; production QNAP remains `4.4.0`.

## Verification

The patch is gated by the full repository CI plus `tests/evaluations/test_cfo_release_closeout_v451.py`. The regression requires top-level release pointers and the v4.5.0 verification receipt to reflect completed release state while preserving CFO/runtime boundaries.

## Release authorization

`docs/release-authorization-v4.5.1.md` records the standing project authorization for this bounded patch lifecycle.

## Rollback

Revert the v4.5.1 documentation and release-control changes, rerun full CI, and issue a corrective patch release. Do not modify QNAP or the CFO runtime because neither changes here.

## Decision log

1. Preserve `v4.5.0` as the feature release.
2. Use `v4.5.1` as a documentation/release-control PATCH under Semantic Versioning.
3. Do not alter CFO implementation version `1.1.0`.
4. Do not alter canonical runtime `4.0.0` or QNAP production `4.4.0`.
5. Require main, semantic tag, GitHub Release, and current documentation to converge on the same final v4.5.1 commit before closeout.
