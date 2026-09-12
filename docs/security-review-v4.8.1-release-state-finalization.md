# v4.8.1 Release State Finalization Security Review

Date: 2026-09-12  
Applicability: **TARGETED**  
Security result: **PASS for release candidate**  
Scope: documentation and GitHub release-control only  
Verified release-control candidate: `f1fa3601e373515950e61ead7c6b9cbdb37fdb28`  
Canonical CI: `34724369995`, **SUCCESS**  
Targeted release-state gate: `34724369989`, **SUCCESS**

## Security profile

This patch touches CI/CD release automation, so TARGETED review is required. It does not alter application runtime, agent identity, MCP tools, connectors, credentials, secrets, data handling, network boundaries, persistence, OAuth, TaskLedger, dependencies, or L0-L5 authority.

## Trust boundaries reviewed

1. GitHub `main` commit -> semantic release workflow.
2. GitHub Actions token -> tag/Release creation.
3. Historical release workflow -> later `main` commits.
4. Release documentation -> operator understanding of actual published state.
5. Verification/security receipt changes -> workflow path-filter coverage.
6. Evidence fixtures -> durable candidate evidence without self-referential SHA drift.

## Falsifiable security properties

- The v4.8.0 historical publisher must not auto-run on future `main` commits.
- v4.8.1 must publish only after its verification job succeeds on the exact `main` SHA.
- The release job must use `--target "$GITHUB_SHA"`.
- The workflow must use read-only contents permission except the release job, which receives only `contents: write`.
- Existing agent/runtime authority, MCP action surfaces, credentials, secrets, and QNAP deployment must remain unchanged.
- The documentation-only patch must not introduce or modify executable runtime dependencies.
- Changes to the v4.8.1 verification/security receipts must trigger the targeted release-state workflow.
- Regression fixtures may pin the independently verified release-control candidate and its run IDs, but must not require a self-referential final evidence commit SHA.

## Verification evidence

Exact-head canonical CI run `34724369995` passed the full repository verification surface on `f1fa3601e373515950e61ead7c6b9cbdb37fdb28`, including contract/drift/package/action checks, Ruff, Mypy, 100% core coverage, Bandit, QNAP regressions, production-equivalent container build, and MCP discovery/sequential-request verification.

Exact-head targeted run `34724369989` passed the v4.8.1 release-state contract, including exact-SHA publishing configuration, historical-publisher retirement, candidate verification receipt checks, and documentation-only runtime/security boundaries.

PR #72's changed-file surface contains only release workflow, release documentation, security/verification receipts, README/RELEASE/changelog, and a release-state regression. It contains no runtime source, role/agent registry, Skill package, MCP source, dependency manifest, deployment asset, database schema, secret, or credential change.

## Findings

- `SEC-481-01` Stale v4.8.0 verification/security receipts described an already-published release as awaiting final publication: **RESOLVED** by durable final receipt updates tied to main/tag/Release SHA `fec9abd4e3cd44f66eeddf3c33f05cc52745c225` and successful release run `34723652446`.
- `SEC-481-02` The already-published v4.8.0 workflow still owned future automatic `main` publication and could fail or create release ambiguity after PATCH commits: **RESOLVED** by converting v4.8.0 to manual historical verification and assigning automatic publication to v4.8.1.
- `SEC-481-03` README release-state edits initially removed a protected historical evidence guarantee: **RESOLVED** by restoring the exact guarantee and passing canonical CI without weakening the historical regression.
- `SEC-481-04` The v4.8.1 verification receipt was initially absent from the workflow path filters, allowing an evidence-only receipt change to bypass the targeted gate: **RESOLVED** by adding the receipt to push/PR filters, checking its candidate-PASS marker, and enforcing the path in `test_release_state_v481.py`.
- `SEC-481-05` The first evidence-only recheck found that the regression still required an obsolete intermediate candidate SHA after the receipt advanced to the independently verified `f1fa3601...` candidate: **RESOLVED** by pinning the regression to the verified release-control candidate and its successful run IDs. No runtime or security acceptance criterion was weakened.

No critical or high security finding remains open in the v4.8.1 candidate.

## Release-control result

The candidate satisfies the required security properties:

- v4.8.0 publication is historical/manual only;
- v4.8.1 owns automatic `main` publication;
- release creation is exact-SHA bound;
- release permissions remain least privilege at workflow/job scope;
- verification/security receipt changes are release-gated;
- evidence fixtures are tied to independently verified candidate evidence without creating an impossible self-referential SHA requirement;
- no runtime, dependency, secret, connector, identity, source-authority, or consequential-action authority change is included.

## Residual risk and non-blocking maintenance

The GitHub connector does not expose branch-ref deletion. Merged feature refs are therefore reconciled to their exact released `main` SHAs rather than deleted. This does not create code divergence or release ambiguity.

A separate Dependabot PR #62 proposes `actions/upload-artifact` v6 -> v7. Current canonical CI still succeeds on v6. That dependency update is unrelated to this documentation/release-state PATCH and is intentionally not absorbed into v4.8.1.

The existing MCP dependency graph also reports one moderate Hono advisory during `npm audit`. This condition predates v4.8.1 and is not introduced or modified by this docs/release-control PATCH. Existing canonical security checks remain green under the repository's current policy. Remediation belongs in a separately scoped dependency/security maintenance change.

## Final security gate

Security status is **PASS for release candidate**. After the verified `f1fa3601` release-control candidate, remaining changes are limited to evidence receipts and regression-fixture alignment. A final exact-head canonical and targeted recheck must pass after they are committed. After merge, final publication verification must prove `main`, tag `v4.8.1`, and the GitHub Release target the same merged commit.
