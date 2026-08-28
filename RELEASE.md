# v4.4.0 Authority Closure

`v4.4.0` is the current repository release candidate. It closes material approval, delegated-authority, nested-delegation, logical Skill-agent provenance, action/schema publication-attestation, runtime-provenance, and release-pipeline defects discovered during v4.3.x production acceptance.

The canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**. The currently deployed QNAP release remains **4.3.0** until a human performs the v4.4.0 deployment.

## Material architecture changes

- L4/L5 authority resolves canonical `APPROVED` TaskLedger approvals for the exact task/action rather than trusting request strings.
- L5 requires Michael as the canonical approval actor.
- `delegation.execute_owner` uses `mesh.cos.owner-execution.v2` and derives the child principal from canonical state.
- Delegated Skill capability authority is restricted to the intersection of owner registry capability and delegation `permitted_capabilities`.
- Nested execution remains task-local and follows registered parent-child routes.
- Human-only and verifier operations remain unreachable through owner execution.
- Denied delegated capabilities produce durable owner-execution failure receipts.
- Skill handoffs explicitly identify the `LOGICAL_SKILL_AGENT` authorization boundary and do not claim synchronous separate Workspace Agent execution.
- All declared agent tools/capabilities are closed through `config/capability-execution.v1.json`.
- ChatGPT production publication attestation requires exact action-name **and input-schema** equality.
- MCP response provenance separately exposes runtime contract, deployment release, immutable source commit, and publication-schema digest.

See `docs/architecture-v4.4.0-authority-execution.md` and `docs/security-review-v4.4.0-authority-closure.md`.

## Release-candidate verification

The exact branch/main revision is acceptable for integration only when GitHub CI proves:

- TypeScript build/tests/MCP smoke and npm security audit;
- Python contract/package/drift, owner-readiness, capability-closure, and source publication checks;
- Ruff, mypy, Bandit, compileall, and **100% branch-aware `mesh_cos` test coverage**;
- QNAP POSIX regression/security checks;
- v4.4.0 QNAP and ChatGPT Skill bundle generation with checksums bound to the exact SHA;
- production-equivalent container version/revision labels;
- modern MCP discovery and sequential calls;
- independent verification recorded in `docs/verification-v4.4.0-authority-closure.md`.

Normal CI is release-neutral and builds the current v4.4.0 candidate. Historical v4.3.0 release workflow execution is no longer triggered by arbitrary future pull requests.

## Candidate assets

CI prepares:

- `mesh-cos-mcp-qnap-v4.4.0.zip`
- `mesh-cos-mcp-qnap-v4.4.0.zip.sha256`
- `mesh-cos-chatgpt-skills-v4.4.0.zip`
- `mesh-cos-chatgpt-skills-v4.4.0.zip.sha256`
- `verification-receipt-current.txt`

The QNAP ZIP contains the v4.4.0 material-turn, architecture, security review, runbook, release notes, Skill notes, and ChatGPT publication-acceptance contract. The Skill ZIP contains the eight governed top-level Skill packages and exact source manifest.

## Version identity

- Repository candidate: `4.4.0`
- Intended semantic tag when manually released: `v4.4.0`
- Candidate container image label: `4.4.0-qnap`
- Canonical authority/runtime contract: `4.0.0`
- Workforce: exactly 10 registered agents
- CoS machine action surface: exactly 28 actions
- Full tool catalog: 30 operations including two human-only operations
- Production remote ingress: OpenAI Secure MCP Tunnel

## Human-controlled release and production gates

The user/operator may handle semantic tag/GitHub Release creation manually. Repository integration does not treat a missing manual release as a source verification failure.

The following remain human-controlled and must not be inferred from CI success:

1. semantic tag / GitHub Release when manually cut;
2. QNAP v4.4.0 production deployment;
3. ChatGPT Workspace custom-app refresh/recreation and publication;
4. capture of the actual ChatGPT action+input-schema snapshot;
5. post-deployment/post-publication live acceptance.

### QNAP production acceptance after human deployment

Require a safe live MCP response to report:

```text
mcp_version: 4.0.0
deployment_release: 4.4.0
source_commit: <merged/released main SHA>
publication_schema_digest: <accepted principal surface digest>
agent_id: cos
```

Then verify the 10-agent registry, valid audit chain, direct delegated-owner execution, both bounded nested routes, owner-only completion, verifier separation, and fail-closed Message Operations approval behavior.

### ChatGPT Workspace acceptance after human publication

Capture the actual action snapshot including exact `inputSchema` for every action and run:

```bash
python scripts/check-published-action-surface.py --actual-file <snapshot.json>
```

Require exact 28/28 CoS machine actions, no unexpected actions, exact schema equality, `delegation.execute_owner` present, and both human-only operations absent. Until then the required status remains:

`BLOCKED_PENDING_ACTUAL_ACTION_SCHEMA_SNAPSHOT`

## Rollback

If a human-deployed v4.4.0 candidate fails live provenance or acceptance, preserve TaskLedger/audit/approval state, stop consequential routing, use the existing versioned QNAP rollback/backup procedures to restore the last verified production release, and keep the last accepted ChatGPT app snapshot active. Do not delete failure receipts or rewrite canonical history.

## Historical releases

v4.3.1 added the independent frozen Workspace action-snapshot gate after PF-058. v4.3.0 introduced cross-agent owner execution for PF-057. Their detailed release, security, verification, and material-turn records remain retained under `docs/` and `CHANGELOG-v4.3.*.md` as immutable release-train evidence.