# QNAP Security Review v4.1.13

## Classification

TARGETED

v4.1.13 changes only the bootstrap and validation path for the governed human Slack approver identity plus release/version documentation and tests. It does not widen MCP authority, change TaskLedger semantics, alter tunnel trust, add agent principals, or embed Slack credentials.

## Findings

### SEC-QNAP-029: Slack conversation ID could be mistaken for a human user principal

**Observed:** Slack exposed `D01K4CL2F8F` as a Channel ID in the user profile pane. v4.1.12 prompted the operator for a Slack user ID and correctly rejected the `D...` value, but the workflow created avoidable identifier ambiguity and deployment friction.

**Remediation:** v4.1.13 binds the verified human user principal `U01KG3CNYHK` as the governed deployment default and removes interactive approver-user-ID entry. `D...` values fail with an explicit conversation/DM-channel diagnostic. Existing persisted approver files are validated before preservation.

**Status:** REMEDIATED.

### SEC-QNAP-030: Non-interactive identity bootstrap must not convert personal identity into a credential secret

**Risk:** Treating the Slack user ID as a credential could encourage unsafe secret handling or accidental inclusion of real Slack tokens in source or release artifacts.

**Remediation:** The user ID is treated as non-secret configuration while runtime compatibility continues to use a protected read-only identity file. Verifier `xoxb-...` and Socket Mode `xapp-...` credentials remain excluded from source, release artifacts, diagnostics, and logs.

**Status:** REMEDIATED.

## Retained controls

- Slack verifier and Socket Mode tokens remain protected runtime files.
- Secret values are never logged.
- Runtime remains non-root and read-only with dropped capabilities and `no-new-privileges`.
- Direct MCP ingress remains denied; OpenAI Secure MCP Tunnel remains the production ingress.
- Release-directory identity remains bound to semantic release metadata.
- Canonical SQLite TaskLedger and protected runtime state remain outside release artifacts.
- Backups exclude secrets.
- Human-only approval operations remain human-only.

## Residual boundary

Repository and container verification cannot prove live Slack identity, official OpenAI Workspace Agent notice authorship, or end-to-end Socket Mode interaction. Live post-deploy acceptance remains required before production certification.
