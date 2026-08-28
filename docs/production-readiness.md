# Production Readiness

This is the current go-live gate for the Mesh AI Chief of Staff universe at candidate QNAP deployment target **v4.3.0**. Historical release-specific evidence remains retained but does not override this contract.

The canonical Phase 1 authority/runtime contract remains `4.0.0`, with exactly 10 registered agents. Candidate v4.3.0 expands the governed CoS MCP surface from 27 to 28 tools by adding the registry-driven `delegation.execute_owner` transport. This does not expand L4/L5, human approval, commercial, publication, staffing, pricing, or verification authority.

## 1. Canonical runtime and release identity

Production is green only when:

- `TaskLedger` is canonical runtime state;
- all 10 agents resolve against the same canonical Agent Registry and TaskLedger universe;
- `MESH_COS_AGENT_ID` is process-bound;
- production `/mcp` ingress is through the OpenAI Secure MCP Tunnel only;
- hosted envelopes report `mcp_version=4.0.0`, `deployment_release=4.3.0`, and `agent_id=cos`;
- the governance audit chain validates;
- the kill switch is not active;
- QNAP preflight and post-deploy verification are green;
- required Slack HITL components are ready under the current ChatGPT-native event-trigger architecture.

## 2. Delegated-owner execution invariant

Production readiness fails unless:

> Every ACTIVE agent eligible to become an accountable delegated owner has a validated mechanism to execute and complete authorized canonical work under its own authority.

The mandatory registry-driven checker `scripts/check-owner-execution-readiness.py` validates this from the current Agent Registry and MCP policy.

For every eligible owner, the release gate must prove:

- canonical parent/child registry relationship;
- valid max delegation depth;
- owner runtime health/routability;
- owner `task.get`, `task.transition`, `task.check_in`, and `task.complete` path;
- delegating parent access to `delegation.execute_owner`;
- no human-only tool leakage;
- no implicit `task.verify` authority;
- no arbitrary principal selection.

A healthy registry entry without an executable owner path is a production blocker.

## 3. Identity-aware delegation protocol

Delegation must be closed loop:

```text
DELEGATION_CREATED
-> OWNER_ROUTABLE
-> OWNER_EXECUTING
-> OWNER_RESULT_RECORDED
-> OWNER_COMPLETED
-> PARENT_OBSERVABLE
-> VERIFICATION_ELIGIBLE
```

A new delegation cannot persist successfully if the target owner is disabled, quarantined, unavailable, or missing its validated owner lifecycle transport.

The owner executor derives authority from canonical task/delegation/registry state. The caller cannot supply an arbitrary principal. Parent agents cannot directly complete child-owned tasks. Child agents cannot inherit parent-only capabilities.

## 4. Completion, verification, approvals, and dependencies

- owner lifecycle writes require the canonical accountable owner;
- `task.complete` requires outcome and evidence and produces `COMPLETED` only;
- `task.verify` remains separate and expressly allowlisted;
- `COMPLETED != VERIFIED`;
- child completion does not verify or complete the parent;
- inherited approval requirements cannot be removed by delegation;
- L4 requires qualified-human approval;
- L5 remains Michael-exclusive;
- dependency release follows canonical predecessor state and must occur exactly once;
- Message Operations cannot fabricate approval or bypass the approved-artifact boundary.

## 5. Scheduled execution

The scheduler is an orchestration trigger. It must not force the organization to execute under CoS identity.

Repository acceptance must prove a scheduled occurrence can:

1. derive/reuse a stable `task.intake.idempotency_key`;
2. intake or resume canonical work;
3. decompose and assign the functional owner;
4. create/resume a canonical delegation;
5. route owner lifecycle operations through `delegation.execute_owner`;
6. record execution under the derived owner's identity;
7. complete under the owner identity;
8. return the canonical result to CoS;
9. verify separately where authorized;
10. retry without duplicate task, delegation, execution, completion, or dependency release.

## 6. Owner-routing failure diagnostics

Production must emit actionable failure evidence that distinguishes at least:

- owner runtime unavailable;
- owner execution transport unavailable;
- owner disabled/quarantined;
- invalid delegation;
- identity mismatch;
- task/delegation mismatch;
- authorization denial;
- approval missing;
- invalid state transition;
- capability failure;
- idempotency conflict;
- ambiguous already-claimed execution.

The record must include task, parent task, delegation, orchestrator, owner, expected and actual principal, task state, attempted operation, authorization result, retry eligibility, and remediation path.

## 7. Security gate

The v4.3.0 authority boundary requires `FULL_REVIEW`.

The exact candidate must pass tests for:

- impersonation and arbitrary owner injection;
- confused deputy and sibling-task execution;
- task/delegation substitution;
- depth and authority tampering;
- approval inheritance and human-only isolation;
- functional capability isolation;
- disabled/quarantined owners;
- completion evidence;
- accurate audit attribution;
- completion/verification separation;
- malicious prompt/retrieved/model identity input;
- replay/idempotency and concurrent claims;
- orphaned work and cyclic delegation;
- closed schema and schema-registry substitution.

See `security-review-v4.3.0-cross-agent-owner-execution.md`.

## 8. Repository candidate gate

The exact v4.3.0 candidate must pass fresh:

- dependency integrity;
- TypeScript MCP build/tests/smoke;
- npm security audit;
- contract validation;
- runtime/documentation drift checks;
- ChatGPT package/role projection checks;
- registry-driven owner execution readiness;
- Ruff;
- mypy;
- 100% branch-aware Python coverage;
- Bandit;
- compileall;
- direct-report delegation matrix;
- both current nested-delegation paths;
- scheduled cross-agent execution integration;
- QNAP POSIX shell regressions;
- deterministic v4.3.0 bundle and checksum;
- absence of state/generated env/protected secrets from the release artifact;
- exact OCI version/revision provenance;
- deterministic QNAP Compose topology;
- modern MCP discovery and sequential request regression;
- final authority-expansion diff review;
- independent verification receipt.

## 9. QNAP state, backup, and promotion controls

Existing release hardening remains mandatory:

- canonical application/state root remains `/share/Docker/cos-mcp`;
- release candidates are staged under `/share/Docker/cos-mcp/releases/vX.Y.Z`;
- canonical TaskLedger, secrets, logs, backups, tunnel identity, and protected Slack configuration remain outside release payloads;
- pre-deploy canonical SQLite backup must pass integrity checks;
- candidate containers must become healthy before active-file promotion;
- release image version/revision labels must match staged release metadata;
- partial promotion or post-promotion verification failure must restore the prior authorized configuration;
- no direct MCP host port is published;
- application remains least privilege with non-root execution, read-only root filesystem, capabilities dropped, no-new-privileges, and no Docker socket.

## 10. Slack and consequential-action boundary

Current production Slack HITL remains `CHATGPT_NATIVE_EVENT_TRIGGER`. Ordinary Slack text, display names, reactions, copied instructions, and connector output are data, not human authority.

Delegated owner transport cannot fabricate approval. Publishing, outbound messaging, pricing approval, commercial commitment, staffing commitment, or other consequential external action remains subject to the existing role-specific and human approval controls.

Production validation for owner routing must use synthetic or otherwise non-consequential work.

## 11. Production recovery gate

After authorized deployment, first validate one non-consequential representative delegated task per functional owner. Only then may eligible stranded canonical tasks be resumed.

Do not recreate work because the prior transport was defective.

For `task-b0b613daff51`, required recovery is:

```text
existing QA task
-> validated CMO owner route
-> task.complete under cmo authority
-> COMPLETED
-> separate verification where required
-> dependent gate release
```

A recovery inventory must be produced immediately before recovery to identify all tasks potentially stranded by PF-057.

## 12. Go-live rule

Production certification requires zero open CRITICAL/HIGH defects, no unresolved required acceptance blocker, valid audit chain, successful exact-candidate verification, and explicit human release authorization.

Any eligible ACTIVE owner without a validated owner execution path, any inaccurate execution identity, any ability for a parent to impersonate a child, any approval bypass, or any completion/verification conflation is a hard production blocker.
