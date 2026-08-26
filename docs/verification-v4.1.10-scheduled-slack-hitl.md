# v4.1.10 Scheduled Automation and Slack HITL Verification Matrix

## Subject

Repository: `mkleinbe/mesh-ai-agent-cos-universe`  
Candidate branch: `fix/v4.1.10-scheduled-slack-hitl`  
Deployment release target: `4.1.10`  
Canonical Phase 1 runtime contract: `4.0.0`  
Security applicability: `TARGETED`

This record separates repository candidate verification from hosted production certification. A repository-green candidate is not evidence that QNAP, Slack Socket Mode, or the OpenAI Workspace Agent Slack surface has been upgraded/configured.

## Defect disposition

| ID | Severity | Defect | Candidate disposition | Hosted evidence required |
|---|---|---|---|---|
| SEC-QNAP-030 | HIGH | Scheduled intake did not pass explicit MCP idempotency key | REMEDIATED | Synthetic repeated intake on deployed v4.1.10 |
| SEC-QNAP-031 | HIGH | Scheduled execution omitted required canonical lifecycle | REMEDIATED | Hosted lifecycle through QA, completion, separate verify |
| SEC-QNAP-032 | HIGH | User-scoped Slack write could author HITL notice as the human user | REMEDIATED BY FAIL-CLOSED CONTROL | Provider evidence of official ChatGPT/ChatGPT Agents bot-authored notice |
| SEC-QNAP-033 | CRITICAL | No trusted Slack human decision -> canonical approval ingress | REMEDIATED | Live Socket Mode `/mesh-approval` and fresh canonical approval readback |
| SEC-QNAP-034 | MEDIUM | Early remediation fixture used production human Slack ID | REMEDIATED IN FINAL TREE | Final-tree/source hygiene evidence |
| SEC-QNAP-035 | HIGH | QNAP permission helper did not cover all Slack protected files | REMEDIATED | Deployed protected file/runtime readiness verification |
| SEC-QNAP-036 | HIGH | SECURITY.md described stale topology/agent count | REMEDIATED | Documentation drift checks on final candidate |
| SEC-QNAP-037 | HIGH | Single QNAP deploy path did not invoke Slack protected configuration | REMEDIATED | Clean v4.1.10 deploy from the single operator path |
| SEC-QNAP-038 | HIGH | Slack provider response could be consumed without service-level `ok:true` assertion under injected transport | REMEDIATED | Negative provider failure regression; live invalid verifier remains fail closed |
| SEC-QNAP-039 | CRITICAL | Ordinary Slack user attribution could be mistaken for proof of human approval | REMEDIATED BY ATTACK-PATH REMOVAL | Ordinary APPROVE message remains PENDING; Socket Mode slash command produces canonical decision |

## Requirement to evidence mapping

### SCH-HITL-001 exact-once scheduled identity

Candidate requirements:
- immutable execution key is passed as `task.intake.idempotency_key`;
- repeated intake returns the same canonical task;
- missed logical timestamps are not collapsed.

Evidence:
- current scheduled dispatcher prompts;
- MCP idempotency regression coverage;
- hosted synthetic acceptance Gate B.

### SCH-HITL-002 canonical lifecycle

Candidate requirements:
- `INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA`;
- `task.complete` requires outcome/evidence;
- `task.verify` is separate and later;
- Sheet PASS is mirror state only.

Evidence:
- lifecycle regression coverage;
- active scheduled task contracts;
- hosted synthetic acceptance Gate B.

### SCH-HITL-003 official OpenAI bot-authored parent

Candidate requirements:
- parent provider user is official ChatGPT or ChatGPT Agents identity;
- exact Approval ID, fingerprint, configured human mention, and approval-owner text;
- human-authored/custom-bot parent is rejected.

Evidence:
- `SlackApprovalHITLService.bind_notice`;
- negative parent-author/provider tests;
- hosted synthetic acceptance Gate D/E.

### SCH-HITL-004 provider-authenticated human decision

Candidate requirements:
- ordinary Slack message text cannot become canonical human authority;
- CoS `slack-adapter` exposes `bind_notice` only;
- `approval.record_decision` remains unavailable to agents;
- runtime opens authenticated Slack Socket Mode with a protected app-level credential;
- only a `slash_commands` envelope for `/mesh-approval` enters the non-MCP human-ingress service;
- the service validates governed channel, protected approver identity, exact command/Approval ID, PENDING canonical approval, official OpenAI bot notice binding, fingerprint, and replay state before recording principal `michael`.

Evidence:
- `SlackSocketModeApprovalListener` Node tests;
- `SlackSocketApprovalService` and bridge tests;
- agent-side denial tests;
- hosted synthetic acceptance Gate F/G.

### SCH-HITL-005 invalid evidence fails closed

Covered negative classes:
- ordinary `events_api`/thread message attributed to the configured human;
- wrong user;
- wrong channel;
- wrong slash command;
- wrong Approval ID;
- wrong fingerprint;
- missing bot binding;
- human-authored parent;
- non-OpenAI bot parent;
- provider `ok:false`;
- direct/agent-side human-decision attempts;
- duplicate/conflicting provider interactions;
- missing/empty/wrong-type protected approver/verifier/Socket Mode files.

Expected result is no canonical approval and no consequential external action.

### SCH-HITL-006 generic Slack connector cannot impersonate OpenAI bot or satisfy human approval

The user-scoped Slack connector is not an accepted governed notice-author surface and ordinary messages from that connector cannot satisfy the human-interaction gate. Active automation contracts prohibit fallback to posting the notice as the connected human user. Unavailable official Workspace Agent delivery is `BLOCKED_CHATGPT_AGENT_TRANSPORT`.

### SCH-HITL-007 production preflight

Production requires:
- exact governed Slack channel;
- protected configured human identity mapping to `michael`;
- exact official OpenAI bot author set;
- mounted non-empty `xoxb-` verifier credential;
- mounted non-empty `xapp-` Socket Mode credential;
- `/mesh-approval` command;
- valid canonical runtime/audit chain;
- `MESH_COS_SLACK_HITL_REQUIRED=true` on QNAP.

The application runtime fails readiness when the required bot-notice verification or active Socket Mode human-ingress boundary is unavailable.

## Repository engineering gates

The final release candidate must have fresh success evidence for:

1. Python dependency integrity.
2. TypeScript MCP build/tests, including Socket Mode transport, and npm audit.
3. Contract, runtime-documentation, and ChatGPT package drift checks.
4. Ruff and mypy.
5. 100% branch-aware `mesh_cos` coverage.
6. Bandit high-severity gate.
7. Python compileall.
8. QNAP shell regressions, including Slack protected configuration and all governed secret permissions.
9. Deterministic v4.1.10 bundle and SHA-256 verification.
10. Compose rendering with required protected mounts and Slack HITL-required runtime configuration.
11. OCI `4.1.10-qnap` version/revision provenance.
12. Modern MCP discovery and sequential requests.
13. Non-root/read-only/capability-dropped runtime and direct-ingress denial.
14. Slack-required production readiness controls and Socket Mode configuration tests.
15. Restart/persistence and SQLite backup integrity.

No green run from an earlier commit may satisfy the final-candidate gate.

## Security review limitation

The Codex Security diff-scan engine is not executable from the current ChatGPT host. No completed Codex Security scan is claimed. The strongest available targeted evidence is required instead: exact diff inspection, repository security policy, source-to-sink attack-path tracing, closed authorization schemas, negative trust-boundary tests, Bandit, full regression/coverage, container/QNAP integration, and independent hosted acceptance.

## Hosted production blockers before certification

The following are not converted into source-level defects if the candidate correctly fails closed, but each blocks production certification until resolved:

1. The live QNAP MCP must report `deployment_release=4.1.10` rather than an older release.
2. A specific official OpenAI Workspace Agent must be configured to deliver the governed bot-authored HITL notice into `#mesh-agent-ops`.
3. Provider readback must prove that notice author is the official ChatGPT/ChatGPT Agents bot identity.
4. QNAP `/readyz` must report `slack_hitl_ready=true` with the authenticated Socket Mode connection active.
5. An ordinary `APPROVE <Approval ID>` Slack message must leave the synthetic approval `PENDING`.
6. MK must invoke `/mesh-approval APPROVE <Approval ID>` and the non-MCP human-ingress service must update canonical principal `michael`.
7. `approval.get` must reflect the synthetic canonical decision before any action.
8. Google TaskLedger operating-mirror state and ProductionPreflight must be reconciled when the exact source connector is available. A shadow workbook is prohibited.

## Certification rule

Only certify production when:

- the exact final repository/release candidate is independently green;
- the actual QNAP deployment is v4.1.10;
- all hosted acceptance gates pass;
- the canonical audit chain remains valid;
- no unauthorized external action occurred;
- there are zero open CRITICAL/HIGH defects;
- there is no unresolved required production-acceptance blocker.
