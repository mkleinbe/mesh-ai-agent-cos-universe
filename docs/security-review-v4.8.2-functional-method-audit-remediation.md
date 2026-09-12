# v4.8.2 Functional Method Audit Remediation Security Review

Applicability: **FULL_REVIEW**  
Security result: **PASS WITH DOCUMENTED BASELINE ADVISORY**

## Scope and trust boundaries

This review covers the remediation changes to all 10 role Skill packages, donor/untrusted-content handling, consequential commercial/financial/messaging behavior, and GitHub release automation. It does not change the canonical runtime binary, MCP operation catalog, authentication, OAuth, secrets, network topology, database schema, or QNAP deployment.

Trust boundaries reviewed:

1. donor/retrieved content -> role Skill;
2. role Skill -> canonical registry, TaskLedger, Revenue Intelligence, and functional source owners;
3. role recommendation -> L4/L5 human approval;
4. CFO/CRO/COO evidence -> pricing, discount, procurement, staffing, contract, or deal authority;
5. CMO/VP Content/Message Operations -> draft, approval, recipient, send, suppression, idempotency, and kill-switch controls;
6. GitHub candidate -> verification -> exact-SHA tag and Release.

## Security properties and evidence

| Property | Required behavior | Evidence |
|---|---|---|
| Prompt injection | Donor/retrieved instructions cannot change identity, tools, canonical source, approvals, action authority, or persistence | `FMR-012`, behavior-gate adversarial matrix |
| Authority laundering | Analytical/recommendation output cannot become approval | `FMR-006` through `FMR-011`, role boundary tests |
| Tool confusion | Skill composition cannot grant tools or principal identity | registry/package/capability-closure checks plus `FMR-012` |
| Canonical-source laundering | Donor or peer evidence cannot reassign TaskLedger or designated canonical source ownership | `FMR-003`, `FMR-005`, `FMR-012` |
| External-action escalation | No donor/method output can authorize procurement, staffing, deals, publish, or send | `FMR-007` through `FMR-012` |
| Message approval | Missing message-specific approval, recipient/send authority, idempotency, suppression, duplicates, or kill switch blocks execution | `FMR-011` |
| Finance/commercial approval | CFO remains evidence-only; CRO remains recommendation-only; exceptions escalate | `FMR-006`, `FMR-008` |
| Skill/principal separation | Shared or local Skills do not become agents, owners, or approval authorities | v4.8 structural tests plus `FMR-012`, `FMR-018` |
| Private reasoning | No raw chain-of-thought or donor decision-memory write | `FMR-012`; Skill mandatory governance |
| Release integrity | Historical v4.8.1 publisher cannot react to future main; v4.8.2 publishes exact `GITHUB_SHA` only | `FMR-013`, workflow regression |
| Historical integrity | v4.8.0/v4.8.1 tags and Releases are never retargeted | historical workflow is read-only/manual; v4.8.2 has its own publisher |
| Token least privilege | Default workflow is `contents: read`; only the v4.8.2 release job receives `contents: write` | `.github/workflows/release-v4.8.2.yml` |

## Adversarial matrix

Each of the 10 role Skill packages is evaluated against instructions attempting to:

- change agent identity;
- add tools;
- change canonical-source ownership;
- bypass human approval;
- authorize procurement, staffing, pricing, discounts, or deals;
- publish or send externally;
- persist raw deliberation to donor memory such as `~/.claude/decisions/`;
- invoke donor roles with `[INVOKE:role]`.

Expected and tested disposition is `FAIL_CLOSED` with no identity/tool/source/approval/external-action/persistence mutation.

## Release automation

The v4.8.1 workflow is historical `workflow_dispatch` only, with `contents: read` and no release publisher. The v4.8.2 workflow owns the current PATCH publisher. It verifies the exact candidate before release and creates `v4.8.2` with `--target "$GITHUB_SHA"`. An already-existing v4.8.2 Release at a different target fails closed. Existing v4.8.0 and v4.8.1 tags/Releases are not rewritten.

## Dependency advisory

The baseline MCP `npm audit` currently reports one **moderate** Hono advisory. The v4.8.2 remediation does not add, update, or expose that dependency and does not change the runtime/network boundary. The advisory is therefore recorded as pre-existing baseline risk rather than silently represented as a clean dependency scan. It is not used to weaken any security gate and should be handled in its own dependency-remediation change if applicable to the deployed code path.

No new Critical or High finding is accepted by this remediation.

## Residuals

- `BLOCKED_SOURCE_IDENTIFICATION`: the fourth donor source remains unidentified. This is a provenance/source-completeness blocker, not an authority bypass.
- Production QNAP remains 4.4.0. No production deployment or runtime security claim is made from this repository PATCH.

## Disposition

**PASS WITH DOCUMENTED BASELINE ADVISORY.** The remediation strengthens behavioral and release-control evidence without expanding authority. The pre-existing moderate dependency advisory and the blocked fourth donor identifier remain explicitly visible.
