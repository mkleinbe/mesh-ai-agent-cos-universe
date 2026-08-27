# Production Readiness

This is the current go-live gate for the Mesh AI Chief of Staff universe at QNAP deployment target **v4.1.16**. Historical release-specific evidence remains retained but does not override this current contract.

The canonical Phase 1 authority/runtime contract remains `4.0.0`, with exactly 10 registered agents and exactly 27 governed CoS MCP tools.

## 1. Canonical runtime and release identity

Production is green only when:

- `TaskLedger` is canonical runtime state;
- all 10 agents resolve against the same registry/TaskLedger universe;
- `MESH_COS_AGENT_ID` is process-bound;
- production `/mcp` ingress is through the OpenAI Secure MCP Tunnel only;
- hosted envelopes report `mcp_version=4.0.0`, `deployment_release=4.1.16`, and `agent_id=cos`;
- `/readyz` reports `slack_hitl_ready=true` for required Slack HITL;
- the governance audit chain validates;
- the kill switch is not active;
- QNAP preflight and post-deploy verification are green.

## 2. Pre-deploy backup integrity

Every upgrade with an existing `mesh-cos-mcp` container must execute the pre-deploy backup gate.

- Docker `.State.Running=true` is not by itself proof that an online `docker exec` backup is safe.
- Stable `status=running` with `.State.Restarting=false` uses the online SQLite backup path.
- Restarting/non-running existing runtimes use the quiesced helper path.
- A restarting runtime is stopped before canonical SQLite state is read.
- The helper uses the exact active Mesh image, `--network none`, runtime UID/GID, read-only root filesystem, dropped capabilities, and `no-new-privileges`.
- Protected Slack/tunnel credentials are not mounted into the helper.
- The canonical SQLite backup helper uses read-only source access, SQLite backup semantics, and `PRAGMA integrity_check`.
- Prior running intent is restored after both successful and failed quiesced backup attempts.
- Failed helper/export attempts leave no successful partial backup artifact.
- Only an absent `mesh-cos-mcp` container skips the existing-runtime pre-deploy backup.

## 3. Release-root staging and transactional promotion

- canonical application root: `/share/Docker/cos-mcp`;
- operator release root: `/share/Docker/cos-mcp/releases`;
- v4.1.16 archive contains one top-level `v4.1.16/` directory;
- scripts self-resolve their versioned release root and do not depend on caller CWD;
- release-directory identity must match staged `release-metadata.txt`;
- candidate build context, Compose, and `.env.runtime` remain under the versioned release directory;
- canonical TaskLedger, tunnel identity/key, Slack protected files, qnet identity, logs, and backups remain outside release payloads;
- candidate containers must become healthy before active-file promotion;
- active `.env`, Compose, and release metadata are snapshotted before promotion;
- partial promotion or post-promotion verification failure restores exact pre-promotion configuration and the prior active stack when available;
- incomplete rollback preserves its recovery snapshot;
- successful post-deploy verification is the promotion transaction commit point.

## 4. Slack HITL trust boundary

v4.1.16 retains the v4.1.15 split:

- connected Slack integration is collaboration-only;
- CoS `slack-adapter` uses `operation: handoff` and returns `CHATGPT_CONNECTOR_HANDOFF` with `COLLABORATION_ONLY` authority;
- ordinary Slack text, reactions, copied commands, display names, and connected-app writes are non-authoritative;
- the custom Slack app is only provider-authenticated `/mesh-approval` Socket Mode human ingress;
- governed Slack user `U01KG3CNYHK` maps to canonical principal `michael` only inside that trusted ingress;
- only `U...`/`W...` human principals are accepted; `D...` conversation IDs fail closed;
- the runtime needs the protected approver identity and `xapp-` Socket Mode token only; no `xoxb-` verifier token is required or mounted;
- canonical approval must be PENDING, owned by `michael`, and bound to an immutable 64-hex `payload_fingerprint`;
- wrong user/channel/command, missing fingerprint, or conflicting second interaction fails closed;
- same provider-envelope replay is idempotent;
- agent-facing MCP tools cannot record human approval.

Slack provider/network failure must not terminate the MCP HTTP process. `/healthz` remains available and `/readyz` fails closed while required Slack HITL is unavailable.

## 5. QNAP network and runtime boundary

- QNAP baseline remains Docker `27.1.2-qnap8` / Compose `2.29.1-qnap2`;
- `mesh-cos-private` is internal-only `172.30.60.0/29`;
- MCP uses private `172.30.60.2` plus qnet `192.168.7.60` as its only external-capable network;
- tunnel uses private `172.30.60.3` plus dedicated egress `172.30.61.2`;
- no unsupported gateway-priority feature is required;
- no direct MCP host port is published;
- application remains UID/GID 65532, read-only root, capabilities dropped, no-new-privileges, and no Docker socket;
- protected credential files remain outside source/release assets and mode `0400` at runtime.

## 6. Scheduled execution, authority, and lifecycle

- scheduled occurrences retain deterministic `task.intake.idempotency_key` values and canonical lifecycle progression;
- `approval.record_decision` and `reliability.human_override` remain human-only;
- L4 requires qualified-human approval; L5 remains Michael-exclusive;
- consequential actions require exact current payload-bound approval and fresh canonical readback;
- `task.complete` and `task.verify` remain separate; **COMPLETED != VERIFIED**.

## 7. Repository release gate

The exact v4.1.16 candidate must pass fresh:

- dependency integrity and npm security checks;
- TypeScript MCP/Socket Mode build/tests;
- contract, runtime-documentation, and ChatGPT package drift checks;
- Ruff, mypy, 100% `mesh_cos` coverage, Bandit, and compileall;
- QNAP POSIX shell regressions including `test-restarting-container-backup.sh` and transactional promotion;
- BDD QNAP-112 through QNAP-115 plus retained QNAP-104 through QNAP-111;
- exact v4.1.16 bundle/checksum and one-top-level-directory inspection;
- absence of state, generated env, and protected secrets from the release artifact;
- exact container OCI version/revision provenance;
- deterministic QNAP Compose topology;
- modern MCP discovery and sequential request regression;
- FULL_REVIEW security receipt for the exact candidate.

Security applicability for v4.1.16 is **FULL_REVIEW**. See `docs/security-review-v4.1.16.md`.

## 8. Hosted production acceptance

Repository and container evidence produce a verified release candidate, not production certification.

After QNAP deployment, execute `docs/chatgpt-published-app-production-acceptance-v4.1.16.md` and require:

- correct `4.0.0` / `4.1.16` dual release identity;
- successful pre-deploy backup evidence, including `state_export_method=quiesced_helper` when upgrading from a restarting source;
- exactly 10 agents and 27 CoS tools;
- valid audit chain;
- deterministic lifecycle/idempotency behavior;
- connected Slack collaboration remains non-authoritative;
- provider-authenticated `/mesh-approval` from the governed human succeeds while wrong-user interaction fails closed;
- fresh canonical approval readback;
- no unauthorized consequential external action.

## 9. Go-live rule

Production certification requires **zero open CRITICAL/HIGH defects** and no unresolved required acceptance blocker.

A live runtime still serving an older deployment release, failed TaskLedger backup integrity, unverified QNAP network path, invalid audit chain, unavailable required Slack human ingress, or any attempt to substitute ordinary Slack text for human authority is a blocker, not an advisory.