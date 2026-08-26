# Production Readiness

This is the current go-live gate for the Mesh AI Chief of Staff universe at QNAP deployment target **v4.1.13**. Historical release-specific acceptance records remain evidence, but they do not override this current contract.

The canonical Phase 1 authority/runtime contract remains `4.0.0`, with exactly 10 registered agents and 27 governed CoS MCP tools.

## 1. Canonical runtime

Production is green only when:

- `TaskLedger` is the canonical runtime state;
- all 10 agents resolve against the same canonical TaskLedger and registry universe;
- `MESH_COS_AGENT_ID` binds the process identity and cannot be overridden by prompt/task/Slack/connector content;
- remote production is served through the OpenAI Secure MCP Tunnel and accepts `/mcp` only from the trusted tunnel-side private source identity;
- hosted envelopes report `mcp_version=4.0.0`, `deployment_release=4.1.13`, and `agent_id=cos`;
- the governance audit chain validates;
- the kill switch is not active;
- local/QNAP preflight is green.

## 2. Release-root staging and promotion integrity

Every production deployment must preserve the release-root contract introduced by v4.1.12:

- canonical application root remains `/share/Docker/cos-mcp`;
- stable operator working directory is `/share/Docker/cos-mcp/releases`;
- current release ZIPs contain a single top-level `vX.Y.Z/` directory and create that version directory when extracted from the releases root;
- the operator does not manually create the version directory, copy/move release payload files, copy helpers to `/share/Docker`, chmod extracted scripts, or change into the version directory;
- operator/helper scripts self-resolve their extracted release root and do not depend on caller CWD;
- before candidate preparation, deployment verifies that the resolved release directory is directly beneath the canonical releases root and that its `vX.Y.Z` basename matches staged `release-metadata.txt`;
- missing, malformed, outside-root, and metadata-mismatched release paths fail closed;
- staged release metadata, build context, Compose, and `.env.runtime` remain under the versioned release directory;
- staged release identity derives from staged `release-metadata.txt`, not active `.env` and not a release-specific default;
- only a leading Git `v` is normalized between tag and runtime release identity;
- active production identity is reported separately from staged candidate identity before promotion;
- host-side `sudo` does not need to preserve a release variable;
- active `.env`, Compose, and release metadata are promoted only after both candidate containers are healthy;
- canonical TaskLedger, tunnel key, Slack protected files, qnet/static networking, logs, and rollback evidence remain outside the release directory and preserved throughout staging;
- already-published historical artifact layouts remain immutable and do not define the current operator contract.

## 3. Scheduled execution integrity

Every governed Scheduled Task logical occurrence must:

- preserve its logical due timestamp rather than collapse missed work into dispatcher wake time;
- derive an immutable execution key, normally `<Job ID>:<logical due timestamp>`;
- pass that exact key as `task.intake.idempotency_key`;
- reuse the same canonical task on replay;
- progress through valid canonical states before completion;
- reach `QA` before `task.complete`;
- provide non-empty outcome/evidence for completion;
- invoke `task.verify` separately from canonical `COMPLETED` state;
- treat Google TaskLedger/other Sheets as recoverable operating mirrors, never substitutes for canonical completion/verification.

A correct business no-op or blocked business outcome may still be a completed/verified dispatcher execution when the occurrence contract was correctly evaluated. Business outcome and execution acceptance remain separate fields.

## 4. Human-only operations and approval

The following remain human-only:

- `approval.record_decision`
- `reliability.human_override`

Agents cannot obtain these tools through delegation, prompt content, Slack text, shared-Skill output, connector output, or model inference.

L4 requires qualified-human approval. L5 remains Michael-exclusive under the current governance contract.

Consequential external actions require exact, current, payload-bound approval and idempotent/auditable execution. Material payload changes invalidate reuse of prior approval.

## 5. Slack HITL trust boundary

For governed Slack human approval:

- the parent HITL notice must be provider-authored by the official ChatGPT or ChatGPT Agents Slack identity;
- a human-authored message, custom bot, or copied display name is not valid notice authorship;
- the verified Slack user principal for Michael/MK is `U01KG3CNYHK` and maps to canonical principal `michael` only inside the trusted human-interaction boundary;
- the Slack user ID is non-secret governed identity configuration and may be committed for deterministic bootstrap; it is still omitted from routine logs and TaskLedger evidence;
- Slack `D...` identifiers are DM/conversation Channel IDs and must never be accepted as human approval principals;
- eligible Slack human user-principal forms begin with `U` or `W`;
- QNAP materializes the governed user ID into a protected read-only runtime identity file; missing identity is bootstrapped without an operator prompt and existing identity is validated before preservation;
- the generic user-scoped Slack connector must not author governed approval notices or satisfy the canonical human-decision gate;
- the server-owned Slack verifier re-reads the exact bound provider thread;
- `skills.invoke_governed` capability `slack-adapter` accepts `bind_notice` only;
- no agent-facing adapter input may record or infer a human approval decision;
- `approval.record_decision` remains unavailable to agents;
- ordinary Slack messages, reactions, copied `APPROVE` text, and user-attributed posts are evidence only and never human authority;
- canonical Slack human decisions enter only through the authenticated Socket Mode `/mesh-approval` slash-command boundary;
- the non-MCP human-ingress service validates the governed channel, configured human user ID, exact command and Approval ID, PENDING canonical approval, provider-verified OpenAI bot notice binding, exact fingerprint, and replay state before recording principal `michael`;
- wrong user, channel, command, Approval ID, fingerprint, duplicate/conflicting interaction, human-authored parent, or non-OpenAI bot parent fails closed;
- if the official OpenAI Workspace Agent cannot deliver a bot-authored notice, the action is `BLOCKED_CHATGPT_AGENT_TRANSPORT` and must not fall back to posting as MK.

Production QNAP sets `MESH_COS_SLACK_HITL_REQUIRED=true`. Runtime readiness must fail when bot-notice verification or the authenticated Socket Mode human-interaction boundary cannot initialize or remain active.

## 6. QNAP runtime and secret handling

Production remains fail closed unless:

- the application container runs as UID/GID 65532;
- root filesystem is read-only;
- all Linux capabilities are dropped;
- no-new-privileges is enabled;
- Docker socket is not mounted;
- CPU/memory controls match the approved deployment contract;
- canonical SQLite TaskLedger is writable only through the intended state mount;
- tunnel runtime key, Slack verifier credential, and Socket Mode app-level credential are outside source, release assets, and generated environment values;
- the Slack approver user ID is treated as non-secret governed configuration, not as a credential;
- the Slack human identity file, verifier token, and Socket Mode app token are mounted read-only from protected host files;
- identity/credential runtime files are owned by runtime UID/GID and mode `0400`;
- diagnostics and logs do not expose credential values and routinely omit the configured human user ID;
- backup/restore integrity checks remain green.

## 7. Completion and verification

`task.complete` and `task.verify` are different operations.

A task may not be reported as verified unless:

- canonical state is `COMPLETED` before verification;
- acceptance evidence exists;
- an authorized verifier evaluates the configured acceptance test;
- canonical verification state is `VERIFIED`;
- audit evidence and operating mirrors reconcile.

`COMPLETED != VERIFIED` remains a non-negotiable production invariant.

## 8. AgentOps and escalation

Production is green only if:

- failures, unsafe tool use, evidence defects, repeated coordination loops, and human overrides remain auditable;
- `promote`, `coach`, `retrain`, `restrict`, and `retire` dispositions remain governed recommendations rather than silent model self-modification;
- critical defects can trigger quarantine/routing restriction and, when necessary, Workspace Agent restriction or unpublication.

## 9. Evidence quality

A result cannot be reported as verified unless:

- canonical state and authoritative source evidence agree;
- provider receipts exist for consequential effects;
- completion and verification are separately recorded;
- required approval evidence is current and exact;
- relevant audit records are present and the chain validates;
- unresolved conflicts are not hidden;
- Sheet or conversational readback is not substituted for canonical MCP evidence.

## 10. Repository release gate

The exact v4.1.13 candidate must pass fresh:

- dependency integrity checks;
- TypeScript MCP build/tests, including Socket Mode transport, and npm security audit;
- contract, runtime-documentation, and ChatGPT package drift checks;
- Ruff and mypy;
- pytest with 100% branch-aware `mesh_cos` coverage;
- high-severity Bandit gate;
- compileall;
- QNAP POSIX shell regressions, including release-root layout, non-interactive Slack approver bootstrap, protected credentials, permissions, provenance, and observability;
- deterministic v4.1.13 bundle and checksum;
- final release ZIP inspection proving every current release entry is below `v4.1.13/`, staged metadata/path consistency, and absence of generated env, credential secrets, and canonical state;
- proof the release contains governed approver user ID `U01KG3CNYHK`, has no visible approver-user-ID prompt, and explicitly rejects `D...` conversation identifiers;
- fail-closed release-directory-to-metadata mismatch regression;
- Compose rendering and release identity assertions, including protected Socket Mode mount and `/mesh-approval` configuration;
- OCI image version/revision provenance;
- modern MCP discovery and sequential requests;
- deterministic positive/negative Socket Mode and non-MCP human-ingress tests without requiring live Slack in CI;
- non-root/read-only/capability-dropped runtime checks;
- direct-ingress denial;
- persistence, restart, and SQLite backup integrity.

Security applicability for v4.1.13 is TARGETED. See `docs/qnap-security-review-v4.1.13.md`.

## 11. Hosted production acceptance

Repository and container evidence produce a **verified candidate**, not production certification.

After QNAP deployment, execute `docs/chatgpt-published-app-production-acceptance-v4.1.13.md` and require:

- correct dual release identity;
- deployment provenance from `/share/Docker/cos-mcp/releases/v4.1.13`;
- exactly 10 active agents and exactly 27 CoS tools;
- valid audit chain;
- explicit scheduled idempotency and lifecycle behavior;
- no deployment-time approver-user-ID prompt;
- protected runtime approver identity resolves to verified user principal `U01KG3CNYHK`;
- one synthetic non-consequential HITL approval with a provider-authored official OpenAI bot parent;
- proof an ordinary `APPROVE` Slack message leaves the canonical approval PENDING;
- active Socket Mode readiness;
- one provider-authenticated `/mesh-approval APPROVE <Approval ID>` interaction by Michael/MK;
- equivalent interaction by another Slack user fails closed;
- fresh canonical `approval.get` reflecting principal `michael` and the exact synthetic action;
- no unauthorized external action;
- required TaskLedger operating-mirror reconciliation when the exact connector is available.

## 12. Go-live rule

Production certification requires **zero open CRITICAL/HIGH defects** and no unresolved required acceptance blocker.

The following are blockers, not advisories:

- live runtime still serving an older deployment release;
- release path or staged metadata does not identify v4.1.13 consistently;
- configured human approver identity is not the verified user principal or is a `D...` conversation identifier;
- official OpenAI bot-authored HITL transport not proven;
- Socket Mode `/mesh-approval` human ingress not proven against the deployed runtime;
- invalid audit chain;
- missing required Slack identity/credential boundary;
- stale/unreconciled required operating mirror when its exact source must be part of acceptance.

Never convert a missing provider capability, unavailable connector, stale mirror, display-name match, ordinary Slack message, screenshot, or prior green run into a production PASS.
