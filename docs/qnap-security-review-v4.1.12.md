# QNAP Security Review v4.1.12

## Classification

Security applicability: **TARGETED**.

v4.1.12 changes release archive layout, shell path resolution, deployment-directory validation, release CI, and operator runbooks. It does not change MCP authentication or authorization, agent authority, TaskLedger semantics, Slack approval authority, network topology, or business behavior.

## Security-sensitive surfaces

The review covers:

- shell and filesystem authority on the QNAP host;
- release artifact extraction and version identity;
- canonical state and secret path separation;
- Docker/Compose deployment execution;
- image provenance and release metadata;
- OpenAI Secure MCP Tunnel ingress;
- protected Slack HITL files;
- deployment logs, backups, and rollback evidence.

## Required security properties

1. The operator root is `/share/Docker/cos-mcp/releases` and a v4.1.12 archive extracts only beneath `v4.1.12/`.
2. Candidate scripts self-resolve from their own release directory and do not trust the caller working directory.
3. The resolved release-directory basename must match staged release metadata before candidate preparation.
4. A release directory outside the canonical release root fails closed unless a test-only `QNAP_RELEASES_ROOT` override deliberately establishes an isolated fixture root.
5. The archive contains no canonical TaskLedger, generated `.env.runtime`, tunnel runtime key, Slack verifier token, Slack Socket Mode token, or human Slack identifier.
6. Canonical state remains `/share/Docker/cos-mcp/state`; protected secrets remain `/share/Docker/cos-mcp/secrets`.
7. Existing release metadata mismatch and OCI image version/revision provenance checks remain mandatory.
8. The runtime remains non-root, read-only, capabilities-dropped, no-new-privileges, with no Docker socket and no public MCP port.
9. Production ingress remains the OpenAI Secure MCP Tunnel.
10. Exactly 10 registered agents, exactly 27 governed CoS tools, human-only operations, and `COMPLETED != VERIFIED` remain unchanged.

## Findings

### SEC-QNAP-027: ambiguous extraction root could cause operator path confusion

Severity: Medium before remediation, resolved in v4.1.12.

The v4.1.11 archive stored its payload at archive root while the operator procedure expected an already-existing `v4.1.11` directory. This created a mismatch between artifact shape and runbook pathing. v4.1.12 packages all current-release entries beneath one top-level `v4.1.12/` directory.

### SEC-QNAP-028: release path identity was not independently bound to staged metadata

Severity: Medium before remediation, resolved in v4.1.12.

Self-resolving scripts correctly avoided caller-CWD dependence, but the deployment orchestrator did not independently require its resolved directory name to match the staged semantic release. v4.1.12 validates the canonical release parent and `vX.Y.Z` basename against staged metadata before candidate preparation.

## Evidence required before release

- ready QNAP-083 through QNAP-091 behavior scenarios;
- RED regression demonstrating v4.1.11 archive/runbook mismatch;
- v4.1.12 archive inspection proving one top-level `v4.1.12/` prefix;
- shell regression for valid and mismatched release-root identity;
- POSIX `sh -n` checks and BusyBox-compatible path-resolution assertions;
- full Python suite with 100% branch-aware coverage;
- npm/TypeScript checks and dependency audit;
- Bandit;
- Compose validation and OCI provenance checks;
- non-root ownership, hardened runtime, direct-ingress denial, restart/persistence, and SQLite backup checks;
- exact-candidate diff inspection for secrets, state, and authority drift.

## Residual risk

QNAP filesystem utilization observed during the prior failed deployment was approximately 96%. The configured absolute free-space gate passed, so this was not causal to the pathing failure, but capacity and snapshot headroom remain an operational advisory.

No unresolved critical or high security finding is accepted by this review. Repository verification cannot prove the actual QNAP deployment or hosted ChatGPT/Slack path; those remain post-deploy acceptance requirements.
