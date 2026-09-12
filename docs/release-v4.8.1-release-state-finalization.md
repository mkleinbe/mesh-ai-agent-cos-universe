# v4.8.1 Release State Finalization

Release date: September 12, 2026

`v4.8.1` is a documentation and release-control PATCH that finalizes the durable post-publication state of the v4.8.0 Functional Method Expansion release.

Repository release: `v4.8.1`  
Canonical Phase 1 authority/runtime contract: `4.0.0`, unchanged  
Production QNAP deployment: `4.4.0`, unchanged

## Why this patch exists

The v4.8.0 implementation, tests, security review, merge, semantic tag, and GitHub Release completed successfully, but `docs/verification-v4.8.0-functional-method-expansion.md` and the v4.8.0 security receipt still contained pre-publication wording saying final main/tag/Release alignment remained pending.

That wording became stale after publication. The actual v4.8.0 release is bound to final main SHA `fec9abd4e3cd44f66eeddf3c33f05cc52745c225`, and release workflow run `34723652446` completed successfully.

## Patch scope

v4.8.1:

- finalizes the v4.8.0 verification receipt with actual merged-main, tag, GitHub Release, and workflow evidence;
- finalizes the v4.8.0 security receipt from candidate wording to durable released-state wording;
- updates README and RELEASE current-release identity to `v4.8.1`;
- retires the v4.8.0 semantic publisher from automatic `main` execution while preserving manual historical verification;
- adds release-state regression coverage and a dedicated v4.8.1 semantic release workflow.

## Explicit non-changes

This patch makes **no agent behavior change** and no change to:

- the 10-agent Phase 1 roster or parentage;
- TaskLedger canonical state;
- L0-L5 authority or approval rights;
- agent Skills, role methods, MCP allowlists, connectors, or external-action rights;
- the v4.8.0 fixed-cost deal-economics implementation;
- Mesh PPMD Bot v1.2.0 or Mesh Messaging v1.3.0;
- runtime schemas, dependencies, credentials, secrets, OAuth, or network boundaries;
- production QNAP deployment `4.4.0`.

No QNAP deployment is part of v4.8.1.

## Security applicability

Security applicability is `TARGETED` because this patch changes CI/CD release-control configuration. Review is limited to exact-SHA release binding, least GitHub token permissions, prevention of historical-release retargeting, and preservation of the existing authority/runtime boundary. No runtime or AI-agent trust boundary changes.

## Rollback

If the patch introduces documentation or release-control drift, revert the v4.8.1 commit and issue a corrective PATCH. Do not roll back or restart the healthy QNAP 4.4.0 runtime for a repository-release metadata defect.
