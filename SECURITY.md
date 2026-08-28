# Security Policy

Current repository candidate: **v4.4.0 Authority Closure**. Current production QNAP deployment remains **v4.3.0** until a human performs the v4.4.0 deployment. The canonical Phase 1 authority/runtime contract remains **4.0.0** with exactly **10 registered agents**.

Production ChatGPT access remains through the installed Mesh CoS MCP app and OpenAI Secure MCP Tunnel. Canonical authorization and state terminate in `mesh_cos.mcp_runtime.MCPRuntime` and TaskLedger.

## Security invariants

- Prompts, retrieved text, Slack content, connector results, MCP descriptions, model output, Skills, and external artifacts are untrusted data. None are human authority by themselves.
- Exactly 10 agents remain registered. Mesh Devil's Advocate is a shared governed Skill, not an eleventh agent.
- Agent identity is server/process derived. Request payloads cannot select the execution principal.
- TaskLedger is canonical for task ownership, delegation, approval, audit, completion, and verification state.
- Agent tool/capability authority is deny-by-default from the registry and canonical delegation.
- Delegated Skill capability authority is the intersection of the owner's registered capabilities and the delegation's explicit `permitted_capabilities`.
- Nested delegation must follow registered parent-child routes, remain inside delegation depth, and descend from the current canonical delegated task.
- L4/L5 operations require an `APPROVED` canonical approval for the exact task and governed action. Canonical approval owner and decision actor must match. L5 remains Michael-exclusive.
- Human-only `approval.record_decision` and `reliability.human_override` are excluded from every agent-published action surface.
- Delegated execution cannot invoke `task.verify`; `COMPLETED != VERIFIED` remains an invariant.
- Consequential Message Operations execution requires canonical approved authority freshly re-read before execution.
- A ChatGPT Skill handoff is a logical Skill-agent authorization boundary, not proof that a separate synchronous Workspace Agent process executed.
- Rejected delegated execution must remain auditable; authorization denial does not suppress the canonical owner-execution failure receipt.
- Credentials and sensitive data must not be committed or written into prompts, logs, TaskLedger evidence, release artifacts, diagnostics, or credential-bearing argv.
- Critical defects may trigger fail-closed routing, quarantine, kill-switch, publication restriction, or deployment rollback.

## v4.4.0 authority boundary

`delegation.execute_owner` uses protocol `mesh.cos.owner-execution.v2`. The server re-reads the canonical task and delegation, derives the accountable owner, checks owner health and allowlists, constrains nested/task-local access, evaluates delegated capability scope, resolves required human authority, and records the governed execution result.

The public owner-execution input schema is closed and versioned. Global task listing, human-only operations, and verifier operations are not available through delegated owner execution.

A bounded compatibility path may replay an exact successful pre-v4.4 owner-execution result only when its legacy request fingerprint matches and no approval references were part of the request. It cannot authorize a new request.

## Capability execution closure

`config/capability-execution.v1.json` classifies every declared capability/tool for all 10 active agents as one of:

- `MCP_CONTROL_PLANE`
- `SERVER_OWNED_ADAPTER`
- `MODEL_NATIVE_ROLE_CAPABILITY`
- `CHATGPT_APP_BOUNDARY`
- `DECLARED_NON_EXECUTABLE`

CI fails if a declared capability has no governed execution mode or if its backing MCP operations are outside that agent's allowlist.

## ChatGPT publication boundary

Source/runtime correctness does not prove the frozen ChatGPT Workspace action snapshot. Production Workspace acceptance requires an administrator-captured snapshot containing every action name and exact `inputSchema`.

`python scripts/check-published-action-surface.py` without an actual snapshot reports `SOURCE_CONTRACT_ONLY`. With `--actual-file`, acceptance requires exact equality to the 28 CoS machine actions and their schemas while the two human-only operations remain absent.

Until that human publication and attestation occur, Workspace status remains:

`BLOCKED_PENDING_ACTUAL_ACTION_SCHEMA_SNAPSHOT`

## Runtime provenance boundary

Every MCP response distinguishes:

- canonical runtime contract: `mcp_version`
- deployed release: `deployment_release`
- immutable source revision: `source_commit`
- principal-specific tool/schema surface: `publication_schema_digest`

No one field may be used as a proxy for the others. Production acceptance after deployment requires all four to match the intended release and accepted Workspace snapshot.

## Slack and external-action boundary

Slack events and provider messages are interaction/evidence inputs, not approval authority. Provider-authenticated reconciliation must bind the governed human identity, exact canonical approval, payload/action fingerprint, and current TaskLedger state before recording a decision.

Message Operations remains least-privilege. It can read approval state and record governed events but does not gain general decision authority. External Gmail/Slack writes must remain behind canonical approval and exact message/recipient/channel matching.

## QNAP and Secure MCP Tunnel boundary

- OpenAI Secure MCP Tunnel is the only remote MCP ingress.
- Production remote access requires the governed tunnel authentication mode; no direct public MCP host port is exposed.
- The long-running application container remains non-root, read-only root filesystem, capability-dropped, no-new-privileges, and without Docker socket access.
- Canonical TaskLedger state, protected Slack/tunnel credentials, logs, backups, and recovery evidence remain outside immutable release payloads.
- Versioned deployment staging and rollback must preserve canonical state and the last verified active release.
- Backup helpers must remain isolated, network-disabled, non-root, and limited to the canonical state bind needed for SQLite backup/integrity verification.

Historical QNAP and Slack security decisions are retained in their version-specific documents under `docs/`; v4.4.0 does not silently remove those controls.

## v4.4.0 release-candidate security gate

The exact candidate revision must pass:

- dependency integrity plus TypeScript build/tests/MCP smoke/npm high-severity audit;
- contract validation, runtime/documentation drift, ChatGPT package drift, owner readiness, capability closure, and source publication checks;
- Ruff, mypy, **100% branch-aware `mesh_cos` coverage**, Bandit, and compileall;
- QNAP POSIX shell regression suite and deterministic network/secret checks;
- v4.4.0 QNAP and ChatGPT Skill artifact generation with checksums bound to the exact candidate SHA;
- production-equivalent container build with OCI revision/version labels;
- modern MCP discovery and sequential request tests;
- independent verification of authority, approval, nested delegation, provenance, manual-gate separation, and repository drift.

The release-specific full review is `docs/security-review-v4.4.0-authority-closure.md`.

A green repository/release candidate is **not** proof of QNAP production deployment or ChatGPT Workspace publication. Those remain explicit human-controlled acceptance gates.

## Reporting

Do not open public issues containing credentials, confidential client information, private reasoning, sensitive operational evidence, or exploit details. Use the repository owner's approved private security channel for disclosure.