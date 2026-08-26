# v4.1.12 QNAP Release-Root Bootstrap

`v4.1.12` supersedes v4.1.11 for QNAP artifact layout and operator pathing. v4.1.11 correctly made operator scripts self-resolving and separated staged candidate identity from active production, but its published ZIP still extracted payload files directly into the caller directory while the operator runbook expected `/share/Docker/cos-mcp/releases/v4.1.11` to already exist. That inconsistency caused the deployment commands themselves to fail before the corrected scripts could run.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and 27 governed CoS MCP tools. Human-only operations remain human-only. Message Operations remains one of the 10 agents; Mesh Devil's Advocate remains a governed shared Skill and is not an agent principal.

## Incident corrected

The observed operator failure was:

- `cd /share/Docker/cos-mcp/releases/v4.1.11` failed because the release directory had not yet been created;
- checksum and ZIP commands then failed because the assets were not in that nonexistent directory;
- chmod failed because extraction had not occurred.

The release artifact shape and the deployment instructions disagreed. v4.1.12 corrects the artifact and runbook together rather than requiring the operator to perform manual staging choreography.

## Core changes

- Stable operator working directory is `/share/Docker/cos-mcp/releases`.
- `mesh-cos-mcp-qnap-v4.1.12.zip` contains a single top-level `v4.1.12/` directory.
- Extracting the ZIP from the releases root creates `/share/Docker/cos-mcp/releases/v4.1.12` automatically.
- No manual `mkdir`, `cp`, `mv`, `chmod`, or `cd` into the version directory is required.
- Operator scripts continue to self-resolve their own directory and helper paths using POSIX/BusyBox-compatible `dirname`, `cd`, and `pwd -P` behavior.
- Deployment validates that its resolved `vX.Y.Z` directory is directly beneath the canonical releases root and agrees with staged semantic release metadata before candidate preparation.
- Candidate metadata, build context, Compose, and generated `.env.runtime` remain inside the versioned release directory.
- Candidate release identity defaults from staged metadata; genuine mismatches remain fail-closed.
- Active `.env`, Compose, and release metadata are promoted only after both application and tunnel containers are healthy.
- Canonical TaskLedger, tunnel runtime key, Slack protected files, qnet/static networking, image provenance, pre-deploy backup, and rollback controls are preserved.

Historical already-published archive layouts remain immutable and reproducible. The v4.1.12 builder retains the historical flat archive shape only when explicitly rebuilding already-published 4.1.0 through 4.1.11 artifacts; current and future releases use the versioned top-level directory contract.

## Retained runtime behavior

v4.1.12 retains immutable scheduled idempotency keys, canonical lifecycle progression, separate completion and verification, official OpenAI bot notice verification, protected Slack approver identity, provider verification, non-authoritative ordinary Slack text, authenticated Socket Mode `/mesh-approval`, human-only `approval.record_decision`, and fail-closed Slack HITL readiness.

## Security boundary

Security applicability is **TARGETED**. See `docs/qnap-security-review-v4.1.12.md`.

The bundle contains no tunnel runtime key, Slack verifier token, Socket Mode token, human Slack identifier, generated `.env`, staged `.env.runtime`, canonical TaskLedger, or state directory. Runtime secrets remain protected read-only files. The release-root metadata gate and OCI version/revision provenance checks remain mandatory.

## BDD and TDD evidence

Ready scenarios QNAP-083 through QNAP-091 in `specs/qnap-release-root-bootstrap-v4.1.12.feature` cover archive prefixing, canonical releases-root execution, directory/metadata identity, removal of manual staging choreography, auxiliary script pathing, artifact secret/state exclusion, canonical runtime separation, BusyBox compatibility, and unchanged authority.

Historical QNAP-074 through QNAP-082 and SCH-HITL-001 through SCH-HITL-007 remain retained as regression evidence.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.12.zip`
- `mesh-cos-mcp-qnap-v4.1.12.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.12`
- Semantic tag: `v4.1.12`
- Container image label default: `4.1.12-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS agent-facing catalog: 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Human Slack approval ingress: authenticated Slack Socket Mode `/mesh-approval`

Successful hosted readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.12
agent_id: cos
slack_hitl_ready: true
```

## Verification gate

The exact final candidate must pass dependency integrity, TypeScript/npm checks, contract/document/package drift checks, Ruff, mypy, 100 percent branch-aware Python coverage, Bandit, compileall, QNAP POSIX shell regressions, actual v4.1.12 archive-prefix inspection, deterministic bundle/checksum generation, Compose validation, OCI provenance, modern MCP discovery/sequential requests, protected Slack HITL controls, non-root/read-only runtime controls, direct-ingress denial, restart/persistence, and Docker-mediated SQLite backup integrity.

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the actual on-premises serving instance, official OpenAI Workspace Agent Slack delivery, or live Slack Socket Mode human interaction.

After deploying v4.1.12, execute `docs/chatgpt-published-app-production-acceptance-v4.1.12.md`. Do not certify production while any CRITICAL/HIGH defect or required live acceptance blocker remains open.

See:

- `docs/qnap-release-root-bootstrap-v4.1.12.md`
- `docs/qnap-security-review-v4.1.12.md`
- `docs/verification-v4.1.12-qnap-release-root-bootstrap.md`
- `docs/release-4.1.12-qnap-release-root-bootstrap.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.12.md`
- `specs/qnap-release-root-bootstrap-v4.1.12.feature`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `docs/slack-agent-protocol.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
