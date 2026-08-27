# Security Review: v4.1.18 QNAP Slack Bot Secret Permissions

## Applicability

**TARGETED** review. The change touches OAuth credential file ownership, QNAP deployment/runtime permissions, and the Slack HITL trust boundary.

## Security property

A valid protected Slack bot OAuth credential must be readable by the non-root Mesh runtime and not readable through broader file modes, logs, release artifacts, or environment values.

Required state:

- credential type remains `xoxb-`;
- runtime identity remains UID/GID `65532:65532`;
- file mode remains `0400`;
- token value is not logged;
- token is not copied into the release bundle or `.env` files;
- missing, unreadable, empty, or wrong-type credentials continue to fail closed;
- the permission helper receives only the existing constrained CHOWN/FOWNER/DAC_OVERRIDE capabilities, no network, and no new authority.

## Finding

### SEC-4.1.18-001: Slack bot token omitted from QNAP secret ownership normalization

- Severity: High deployment defect, not a credential disclosure
- Surface: QNAP protected secret lifecycle
- Evidence: v4.1.17 provisioning created the bot token as root with mode `0400`; `mesh_apply_secret_permissions` normalized the tunnel key, approver ID, deprecated verifier token, and Socket Mode token but omitted `slack-bot-token`.
- Consequence: the non-root candidate runtime could not read the mounted bot credential and failed canonical preflight. Transactional rollback preserved the prior production stack.
- Remediation: include `slack-bot-token` in the same constrained ownership/mode loop.
- Retest: QNAP-129/QNAP-130 plus the QNAP runtime-permission regression and live candidate runtime preflight.
- Status: remediated in candidate, pending exact-head CI and live QNAP verification.

## Review result

No authority widening, token-value exposure, or new network surface is introduced by the fix. The intended least-privilege state is restored by changing ownership to the existing runtime UID/GID while retaining mode `0400`.

**Repository security disposition: PASS subject to exact-head CI/security gates and live QNAP deployment verification.**
