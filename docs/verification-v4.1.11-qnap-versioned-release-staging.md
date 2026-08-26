# Independent Verification Plan v4.1.11

Subject: QNAP versioned release staging remediation for `mesh-ai-agent-cos-universe`.

## Bound behavior

Ready scenarios QNAP-074 through QNAP-082 in `specs/qnap-versioned-release-staging-v4.1.11.feature` govern this patch. v4.1.10 scheduled automation and Slack HITL scenarios remain applicable and unchanged.

## Evidence matrix

| Claim | Required evidence |
| --- | --- |
| Versioned bundle is self-contained | Release ZIP inspection plus `test-versioned-release-layout.sh` |
| Helpers resolve from release root | Shell regression and source inspection |
| Active production and staged candidate identities remain distinct | Python evaluation plus preflight source/behavior checks |
| `vX.Y.Z` normalization is bounded | Shell and Python regression tests |
| Real mismatch still fails closed | Regression assertion against prepare safety gate |
| Sudo need not preserve release env | Source/evaluation proof that staged metadata is default identity source |
| Candidate descriptors are staged | Source/evaluation proof for `.env.runtime`, staged Compose, staged metadata |
| Promotion occurs only after health | Deploy ordering regression and source inspection |
| State/secrets/network are preserved | Diff review, Compose checks, backup tests, runtime checks |
| MCP/agent authority is unchanged | existing contract/doc/package drift checks and agent/tool regression suite |
| Release artifact is internally consistent | bundle metadata, SHA-256, Compose, OCI version/revision and exact commit checks |

## Required fresh checks on exact candidate

- Python dependency integrity and package check
- TypeScript/npm checks and audit already governed by CI
- contract, runtime-doc, and ChatGPT-package drift checks
- Ruff and mypy
- full pytest with 100 percent branch-aware coverage gate
- Bandit and compileall
- POSIX `sh -n` across QNAP scripts/tests
- QNAP Compose, observability, permissions, provenance, Slack HITL, and versioned-layout regressions
- deterministic v4.1.11 bundle and checksum
- final ZIP inspection, including absence of `.env`, secrets, and canonical state
- Compose candidate validation for 4.1.11
- OCI image labels `4.1.11-qnap` and exact candidate Git revision
- modern MCP discovery/sequential requests
- non-root ownership, read-only runtime, no Docker socket, resource limits
- direct-ingress denial
- restart/persistence
- Docker-mediated SQLite backup
- exact diff inspection for unintended files, secrets, authority widening, and documentation drift

## Security receipt

Security applicability is TARGETED. Consume `docs/qnap-security-review-v4.1.11.md` and independently verify its properties against the exact candidate.

## Acceptance boundary

A green repository candidate is not production acceptance. Actual QNAP deployment must report `mcp_version=4.0.0`, `deployment_release=4.1.11`, `agent_id=cos`, and `slack_hitl_ready=true`, followed by the v4.1.11 hosted acceptance procedure. Until that occurs, release status may be INTEGRATED but not production accepted.
