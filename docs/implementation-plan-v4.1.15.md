# v4.1.15 Implementation Plan

## Baseline

Branch: `refactor/slack-plugin-hitl-v4.1.15`
Base: current `main` after v4.1.14.
Ready behavior: `specs/qnap-slack-plugin-hitl-v4.1.15.feature` QNAP-104 through QNAP-108.
Security: FULL_REVIEW per `docs/security-review-v4.1.15.md`.

## Dependency order

1. RED acceptance and unit evidence for QNAP-104/108 proving active deployment still requires verifier token and mount.
2. RED approval-service evidence for QNAP-105/106 proving the current canonical decision path depends on provider-verified notice binding.
3. RED runtime-resilience evidence for QNAP-107 proving an initial Slack connection failure rejects startup/crashes the process.
4. Refactor canonical approval service to validate pending approval, principal, immutable fingerprint, exact provider-authenticated slash-command envelope, and replay without notice-binding dependency.
5. Refactor Socket Mode listener so initial/provider connection failure degrades HITL readiness and schedules bounded reconnect instead of terminating MCP startup.
6. Refactor QNAP deployment/configuration/Compose/preflight to require only approver identity plus Socket Mode app token. Remove verifier credential provisioning/mounts/runtime requirements.
7. Remove obsolete active verifier/bot-author code while retaining historical release documentation/spec evidence as historical where appropriate.
8. Update current protocol, deployment, security, README/release docs and bundle packaging for v4.1.15.
9. Run targeted Python/TypeScript/QNAP shell tests, lint/type/security checks, full CI, exact bundle verification, container build, MCP discovery/runtime regression, and secret/debris scan.
10. Independently verify requirement/scenario/security traceability, inspect actual diff, resolve every defect, then open PR and run clean CI. Merge/release only after exact-candidate verification passes.

## Scenario mapping

- QNAP-104: Slack collaboration has no approval authority and QNAP has no verifier dependency. Evidence: deployment, protocol, approval tests.
- QNAP-105: authenticated MK slash command records exact canonical approval. Evidence: Python approval service + Node Socket listener integration.
- QNAP-106: ordinary message/wrong user/channel/replay/conflict fail closed. Evidence: unit/integration adversarial tests.
- QNAP-107: Slack outage does not terminate MCP service. Evidence: listener startup/reconnect tests plus QNAP runtime readiness behavior.
- QNAP-108: upgrade requires/mounts only Socket Mode token and approver identity, never logs credentials. Evidence: shell/evaluation/bundle tests and artifact inspection.

## Recovery

No migration of the TaskLedger schema is required. v4.1.14 production can be restored using existing deployment backup/rollback controls. The legacy verifier secret file may remain on the host after upgrade but is unused and unmounted; deletion is not part of automated deployment so rollback remains possible.
