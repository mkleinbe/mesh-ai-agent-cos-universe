# v4.1.11 QNAP Versioned Release Staging Remediation

`v4.1.11` supersedes the published v4.1.10 QNAP deployment artifact because the v4.1.10 operator scripts did not honor the established versioned release-directory contract. The scheduled-automation and Slack HITL runtime behavior introduced by v4.1.10 is carried forward unchanged.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and 27 governed CoS MCP tools. Human-only operations remain human-only. This release does not widen L4/L5 authority. Message Operations remains one of the 10 agents; Mesh Devil's Advocate remains a governed shared Skill and is not an agent principal.

## Incident corrected

A real v4.1.10 deployment from `/share/Docker/cos-mcp/releases/v4.1.10` exposed two coupled release-layout defects:

1. operator/helper scripts defaulted `QNAP_SCRIPT_ROOT` to `/share/Docker`, so the self-contained extracted bundle could not find its observability helper;
2. preflight and prepare read release configuration and metadata from active `/share/Docker/cos-mcp`, causing staged v4.1.10 operations to observe active v4.1.8 and ultimately fail the release-identity gate.

The published v4.1.10 checksum was valid and its internal release metadata was not stale. The artifact was structurally defective for the required execution model. The active v4.1.8 runtime and canonical TaskLedger remained intact, and the pre-deployment online SQLite backup succeeded.

## Core changes

- Release artifacts are staged and executed from `/share/Docker/cos-mcp/releases/vX.Y.Z`.
- Operator scripts self-resolve their extracted release root using POSIX `sh` compatible path resolution.
- No helper scripts need to be copied into `/share/Docker`.
- Candidate metadata, build context, Compose, and generated `.env.runtime` remain inside the versioned staging directory.
- Candidate release identity defaults from staged `release-metadata.txt`, not active `.env` and not a hard-coded patch version.
- An explicit `vX.Y.Z` request normalizes only its leading `v`; true mismatches remain fail-closed.
- Standard `sudo sh ./mesh-cos-mcp-deploy.sh` does not depend on sudo preserving `MESH_COS_DEPLOYMENT_RELEASE`.
- Preflight reports the active production release and staged candidate release separately.
- Active `.env`, Compose, and release metadata are promoted only after both application and tunnel containers are healthy.
- Canonical TaskLedger, tunnel runtime key, Slack protected files, qnet/static networking, image provenance, pre-deploy backup, and rollback controls are preserved.

## v4.1.10 behavior retained

v4.1.11 retains immutable scheduled idempotency keys, canonical lifecycle progression, separate completion and verification, official OpenAI bot notice verification, protected Slack approver identity, provider verification, non-authoritative ordinary Slack text, authenticated Socket Mode `/mesh-approval`, human-only `approval.record_decision`, and fail-closed Slack HITL readiness.

## Security boundary

Security applicability is **TARGETED**. See `docs/qnap-security-review-v4.1.11.md`.

The bundle contains no tunnel runtime key, Slack verifier token, Socket Mode token, human Slack identifier, generated `.env`, staged `.env.runtime`, canonical TaskLedger, or state directory. Runtime secrets remain protected read-only files. The release mismatch gate and OCI version/revision provenance checks remain mandatory.

## BDD and TDD evidence

Ready scenarios QNAP-074 through QNAP-082 in `specs/qnap-versioned-release-staging-v4.1.11.feature` cover self-contained versioned execution, active/candidate identity separation, release normalization, fail-closed mismatch, sudo behavior, staged descriptors, post-health promotion, rollback/state preservation, BusyBox compatibility, and authority invariants.

The historical SCH-HITL-001 through SCH-HITL-007 scenarios remain retained and applicable to the carried-forward v4.1.10 capability.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.11.zip`
- `mesh-cos-mcp-qnap-v4.1.11.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.11`
- Semantic tag: `v4.1.11`
- Container image label default: `4.1.11-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS agent-facing catalog: 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Human Slack approval ingress: authenticated Slack Socket Mode `/mesh-approval`

Successful hosted readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.11
agent_id: cos
slack_hitl_ready: true
```

## Verification gate

The exact final candidate must pass dependency integrity, TypeScript/npm checks, contract/document/package drift checks, Ruff, mypy, 100 percent branch-aware Python coverage, Bandit, compileall, QNAP POSIX shell regressions including versioned-layout tests, deterministic bundle/checksum generation, final ZIP inspection, Compose validation, OCI provenance, modern MCP discovery/sequential requests, protected Slack HITL controls, non-root/read-only runtime controls, direct-ingress denial, restart/persistence, and Docker-mediated SQLite backup integrity.

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the actual on-premises serving instance, official OpenAI Workspace Agent Slack delivery, or live Slack Socket Mode human interaction.

After deploying v4.1.11, execute `docs/chatgpt-published-app-production-acceptance-v4.1.11.md`. Do not certify production while any CRITICAL/HIGH defect or required live acceptance blocker remains open.

See:

- `docs/qnap-versioned-release-staging-v4.1.11.md`
- `docs/qnap-security-review-v4.1.11.md`
- `docs/verification-v4.1.11-qnap-versioned-release-staging.md`
- `docs/release-4.1.11-qnap-versioned-release-staging.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.11.md`
- `specs/qnap-versioned-release-staging-v4.1.11.feature`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `docs/slack-agent-protocol.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
