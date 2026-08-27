# v4.1.15 Implementation Plan

## Baseline

Branch: `refactor/slack-plugin-hitl-v4.1.15`
Base: `main` after v4.1.14.
Ready behavior: `specs/qnap-slack-plugin-hitl-v4.1.15.feature` QNAP-104 through QNAP-111.
Security: FULL_REVIEW per `docs/security-review-v4.1.15.md`.

## Dependency order

1. Establish RED evidence for the obsolete verifier dependency and bot-notice binding.
2. Establish RED approval-service evidence for provider-authenticated human ingress independent of notice-thread verification.
3. Establish RED runtime-resilience evidence for Slack connection failure during startup.
4. Refactor canonical approval service to validate pending approval, principal, immutable fingerprint, exact provider-authenticated slash-command envelope, and replay without notice-binding dependency.
5. Refactor Socket Mode listener so provider/network failure degrades HITL readiness and schedules bounded reconnect instead of terminating MCP startup.
6. Refactor QNAP deployment/configuration/Compose/preflight to require only approver identity plus Socket Mode app token and remove verifier credential runtime requirements.
7. Make QNAP Docker Engine 27 egress deterministic with an internal MCP/tunnel bridge, qnet MCP egress, and a dedicated tunnel egress bridge.
8. Add automatic recovery of the previously active stack when candidate activation or health fails before promotion.
9. Add snapshot-backed transactional promotion so partial promotion or post-promotion verification failure restores the exact pre-promotion configuration and previous stack.
10. Preserve a recovery snapshot if rollback itself fails; constrain snapshot cleanup paths; define successful post-deploy verification as the promotion commit point.
11. Remove obsolete active verifier/bot-author code while retaining historical release evidence where required for rollback history.
12. Update protocol, deployment, security, release docs, BDD, and bundle packaging for v4.1.15.
13. Run targeted Python/TypeScript/QNAP shell tests, lint/type/security checks, full CI, exact bundle verification, container build, MCP discovery/runtime regression, and secret/debris scan.
14. Independently verify requirement/scenario/security traceability and actual diff, resolve every defect, then merge/release only after exact-candidate verification passes.

## Scenario mapping

- QNAP-104: Slack collaboration has no approval authority and QNAP has no verifier dependency. Evidence: adapter, protocol, deployment, and approval tests.
- QNAP-105: authenticated MK slash command records the exact canonical approval. Evidence: Python approval service and Node Socket listener integration.
- QNAP-106: ordinary message, wrong user/channel/command, replay, and conflict fail closed. Evidence: adversarial unit/integration tests.
- QNAP-107: Slack provider/network outage does not terminate MCP service. Evidence: listener startup/reconnect tests and health/readiness behavior.
- QNAP-108: upgrade requires and mounts only Socket Mode token plus approver identity and never logs credentials. Evidence: shell/evaluation/bundle tests and artifact inspection.
- QNAP-109: Docker Engine 27 topology has deterministic MCP and tunnel egress without unsupported gateway-priority features. Evidence: Compose/evaluation/CI topology checks.
- QNAP-110: failed candidate activation/health restores the prior active stack before promotion. Evidence: deploy-path tests and shell contracts.
- QNAP-111: partial promotion and post-promotion verification failure restore the pre-promotion configuration and prior active stack. Evidence: transactional-promotion helper, shell regression, deploy-path assertions, and exact release gates.

## Recovery

No TaskLedger schema migration is required. v4.1.14 can be restored using existing backup/rollback controls. The legacy verifier secret file may remain on the host after upgrade but is unused and unmounted by v4.1.15 so older releases remain recoverable.

Before active-file promotion, v4.1.15 snapshots `.env`, `compose.yaml`, and `release-metadata.txt`, including absence markers. Any partial promotion or post-promotion verification failure attempts to restore that exact snapshot and the previously active stack. If rollback itself is incomplete, the recovery snapshot is preserved for operator recovery rather than deleted. Successful post-deploy verification is the transaction commit point.
