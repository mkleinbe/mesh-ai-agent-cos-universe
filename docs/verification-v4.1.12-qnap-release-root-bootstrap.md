# Verification v4.1.12 QNAP Release-Root Bootstrap

## Subject

Candidate release `v4.1.12` for `mkleinbe/mesh-ai-agent-cos-universe`.

## Behavior-to-evidence matrix

| Scenario | Requirement | Evidence |
|---|---|---|
| QNAP-083 | ZIP creates one versioned directory under the releases root | archive listing must contain only `v4.1.12/` entries and required deploy/metadata paths |
| QNAP-084 | deploy runs while operator remains at `/share/Docker/cos-mcp/releases` | script self-resolution tests plus runbook contract |
| QNAP-085 | directory identity agrees with staged metadata | shell regression for valid root and fail-closed mismatch |
| QNAP-086 | no manual mkdir/copy/move/chmod/chdir choreography | runbook static regression |
| QNAP-087 | backup/preflight/verify/Slack scripts work when invoked through versioned paths from release root | self-resolution regression for all operator scripts |
| QNAP-088 | archive excludes state and protected secrets | deterministic bundle inspection |
| QNAP-089 | canonical state/secrets/logs remain outside release folder | source/config regression and runtime checks |
| QNAP-090 | BusyBox-compatible path resolution | POSIX `sh -n` plus prohibition on `realpath`/`readlink -f` dependencies |
| QNAP-091 | release correction does not widen authority | contract/package drift checks, exact 10-agent and 27-tool assertions, human-only negative controls |

## Required engineering evidence

The exact candidate SHA must pass:

- Python dependency integrity;
- npm/TypeScript build, tests, smoke, and high-severity dependency audit;
- contract, runtime-documentation, and ChatGPT package drift checks;
- Ruff and mypy;
- full pytest suite at 100 percent branch-aware coverage;
- Bandit and Python compileall;
- QNAP shell syntax and release-root regressions;
- current v4.1.12 bundle construction and archive-prefix inspection;
- checksum verification;
- Compose candidate validation;
- production image construction with OCI version/revision provenance;
- modern MCP discovery and sequential requests;
- non-root QNAP ownership handoff;
- hardened runtime, direct-ingress denial, restart/persistence, and Docker-mediated SQLite backup.

## Security evidence

Security applicability is TARGETED. `docs/qnap-security-review-v4.1.12.md` defines the trust boundaries and properties to verify. No release PASS is valid if a release-root mismatch can proceed, if secrets/state are present in the artifact, if OCI provenance is weakened, or if authority/runtime invariants drift.

## Post-deploy evidence

Actual QNAP deployment remains outside repository verification. After deployment require:

```text
mcp_version: 4.0.0
deployment_release: 4.1.12
agent_id: cos
slack_hitl_ready: true
```

Then execute the hosted ChatGPT and Slack acceptance procedure. Repository-green is not production certification.
