# QNAP Security Review v4.1.11

## Applicability

**TARGETED**. v4.1.11 changes privileged QNAP deployment scripts, release/staging paths, runtime configuration promotion, image provenance inputs, secret-file handling context, and MCP deployment/runtime controls. It does not change the canonical MCP authority model.

## Security properties

The corrected candidate must prove:

1. Canonical TaskLedger state is preserved and is never replaced merely because a release is staged.
2. Tunnel runtime key, Slack approver identity, Slack verifier token, and Slack Socket Mode app token remain outside release assets and generated runtime environment values.
3. Operator/helper scripts execute from the versioned release root without expanding filesystem authority to arbitrary paths.
4. Candidate image version and revision remain bound to staged release metadata and exact Git commit.
5. A genuine requested-release versus staged-release mismatch fails closed.
6. Candidate runtime descriptors do not replace active descriptors before candidate health succeeds.
7. Existing Secure MCP Tunnel ingress, qnet/static networking, non-root runtime UID/GID, read-only rootfs, capability drops, and no-new-privileges remain unchanged.
8. Exactly 10 agents and 27 CoS MCP tools remain governed; no L4/L5 authority is widened.
9. Human-only approval operations remain human-only. Slack `/mesh-approval` remains the trusted human approval ingress defined by v4.1.10.
10. Diagnostic logging does not collect secret contents, generated environment contents, or tunnel logs containing credentials.

## Trust-boundary review

### Release artifact to privileged QNAP shell

Release content is untrusted until checksum, staged metadata, semantic release identity, and image provenance checks pass. Self-resolution uses the executing script directory and canonicalized `pwd -P`; it does not accept arbitrary helper search paths by default.

### Staged candidate to canonical runtime

Staged metadata, Compose, and `.env.runtime` remain under the versioned release directory. Canonical state and secrets remain under `/share/Docker/cos-mcp`. Only non-secret runtime descriptors are promoted, and only after both application and tunnel containers report healthy.

### Secrets

The release bundle contains no generated `.env`, canonical TaskLedger, tunnel key, personal Slack ID, verifier token, or Socket Mode app token. Protected files remain mode `0400` under runtime UID/GID after the existing constrained Docker-mediated permission helper runs.

### Network and MCP authority

No network topology, MCP tool catalog, agent roster, trusted tunnel source, or authorization policy is changed by this remediation. Direct non-tunnel MCP denial remains part of verification.

## Review result

No new authority or data-access capability is introduced by the intended fix. The release-identity mismatch assertion and OCI provenance checks are preserved. Candidate promotion is more conservative than v4.1.10 because active descriptors are not overwritten during preparation.

Required verification evidence: POSIX shell syntax/regressions, staged-layout RED/GREEN coverage, full repository suite and coverage gate, Bandit, Compose render, exact bundle inspection and SHA-256, OCI version/revision labels, hardened runtime checks, restart/persistence, direct-ingress denial, Docker-mediated SQLite backup, diff review for secret/debris leakage, and exact-candidate CI.

Codex Security evidence is not claimed by this review. Any such scan, if separately executed, must be bound to the exact candidate SHA. Actual QNAP and hosted ChatGPT/Slack acceptance remains outside repository-only security proof.

## Residual risk

The QNAP application filesystem was observed at 96 percent utilization during the v4.1.10 failure. The existing absolute free-space gate passed, so this was not the incident root cause. It remains an operational headroom advisory and should be monitored independently of this release correction.
