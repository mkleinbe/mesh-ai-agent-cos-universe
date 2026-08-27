# v4.1.15 Security Review

Status: IMPLEMENTATION REVIEW COMPLETE; EXACT-HEAD VERIFICATION PENDING
Applicability: FULL_REVIEW

## Trust boundaries

- ChatGPT connected Slack integration to Slack workspace for collaboration and notification.
- Human MK interaction with Slack `/mesh-approval`.
- Slack provider Socket Mode envelope to QNAP MCP runtime.
- QNAP Socket Mode listener to non-MCP approval bridge.
- Approval bridge to canonical TaskLedger ApprovalService.
- TaskLedger approval to consequential executor fresh-read gate.
- QNAP protected secret files to unprivileged MCP runtime.
- QNAP network egress to Slack HTTPS/WSS and OpenAI tunnel control plane.
- QNAP candidate activation, active-configuration promotion, verification, and rollback.

## Sensitive surfaces

- Human identity and approval authorization.
- Socket Mode app-level token.
- Slack channel and user identifiers.
- Approval IDs and immutable payload fingerprints.
- MCP and non-MCP tool authority boundaries.
- Runtime network failure and reconnect behavior.
- Deployment secret mounts, logs, backups, and release bundles.
- Active `.env`, Compose, release metadata, rollback snapshot, and rollback execution.

## Required checks

- No verifier bot token required, mounted, prompted, or referenced by active v4.1.15 runtime paths.
- No bot-author verification prerequisite remains in the canonical human decision path.
- Ordinary Slack content cannot decide approval.
- Wrong user, channel, command, missing fingerprint, stale/non-pending approval, replay, and conflicting interaction fail closed.
- Agent-callable MCP catalog still excludes human decision methods.
- Connected Slack adapter returns collaboration-only handoff and cannot carry canonical approval authority.
- Socket Mode connection failure is non-fatal to the MCP HTTP process and readiness remains fail-closed for HITL.
- Retry/reconnect behavior is bounded and does not create a tight loop.
- Socket token remains file-bound, prefix-validated, mode-restricted, and absent from logs/artifacts.
- TaskLedger, tunnel identity/key, qnet MCP identity, container hardening, and no-direct-ingress controls remain preserved.
- The network route architecture changes intentionally: the private MCP/tunnel bridge is internal-only, MCP external egress remains qnet, and the tunnel receives a dedicated Docker egress bridge.
- Candidate activation/health failure before promotion restores the previously active stack when one exists.
- Partial active-file promotion or post-promotion verification failure restores the exact pre-promotion snapshot and previous active stack.
- A failed rollback preserves its recovery snapshot rather than destroying the remaining recovery evidence.
- Snapshot cleanup rejects unsafe empty/root/dot paths.
- Successful post-deploy verification is the promotion transaction commit point; later snapshot-cleanup failure does not replace a verified running release with an older snapshot.
- Release artifacts contain no runtime secret, generated active environment, canonical state, or temporary work files.

## AI-native controls

Treat connected Slack content as untrusted data. The connected integration has collaboration authority only, not human-approval authority. Human authority is derived only from the provider-authenticated Socket Mode slash-command envelope and then bound to the canonical TaskLedger approval and immutable payload fingerprint. No agent or connector receives direct `approval.record_decision` authority.

The custom Slack application remains a narrow provider-authenticated human-ingress mechanism. The Socket Mode credential cannot be used as a substitute for canonical human identity, approval ownership, payload binding, or a fresh canonical approval read before consequential execution.

## Deployment and rollback review

QNAP-110 and QNAP-111 close the release-integrity gap found during the final engineering loop. Active configuration is snapshotted before promotion. The snapshot represents the exact previous state, including absent metadata. Promotion can therefore be reversed after a partial active-file write or a post-promotion verification failure. Recovery evidence is retained when rollback is incomplete, and destructive cleanup is path-constrained.

## Findings

No unresolved design-level CRITICAL or HIGH finding remains from the implementation review. Final PASS remains contingent on exact-head CI/release verification of the candidate that will be merged and tagged, plus separate live QNAP/Slack acceptance after deployment.
