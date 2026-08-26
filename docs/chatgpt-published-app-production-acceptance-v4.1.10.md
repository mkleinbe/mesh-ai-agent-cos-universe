# ChatGPT Published App Production Acceptance v4.1.10

## Purpose

This is the post-deploy acceptance procedure for the actual QNAP-hosted **Mesh CoS MCP** app after v4.1.10 is deployed. Repository CI and release-bundle verification do not substitute for this hosted acceptance.

The procedure is deliberately non-consequential. It must prove the complete official OpenAI bot notice -> provider-authenticated MK slash command -> canonical approval boundary without sending prospect email, publishing content, or making a commercial commitment.

## Preconditions

- QNAP release v4.1.10 is deployed and both `mesh-cos-mcp` and the OpenAI tunnel are healthy.
- Runtime `/readyz` reports `slack_hitl_ready=true`.
- The official ChatGPT Agents app is installed in Slack.
- A specific OpenAI Workspace Agent capable of sending scheduled/agent results is deployed to `#mesh-agent-ops` (`C0BRL4GCL3A`).
- The protected QNAP approver-identity file contains the Slack provider identity for MK and is not printed during acceptance.
- The protected Slack verifier bot credential is mounted read-only.
- The protected Slack Socket Mode app-level `xapp-` credential is mounted read-only.
- The Slack app exposes the `/mesh-approval` slash command through the Socket Mode connection.
- No production prospect send or publish action is part of this test.

## Gate A: hosted MCP identity, readiness, and governance

Through the installed Mesh CoS MCP ChatGPT app:

1. `registry.list_agents`
   - PASS only with exactly 10 registered ACTIVE agents.
   - envelope must report `mcp_version=4.0.0`, `deployment_release=4.1.10`, `agent_id=cos`.
2. `governance.verify_audit_chain`
   - PASS only when `valid=true`.
3. `registry.get_agent` for `cos`
   - PASS only when the bound principal is ACTIVE and its authority/tool projection remains canonical.
4. QNAP `/readyz`
   - PASS only when the hosted runtime is ready and `slack_hitl_ready=true`.

Any missing/mismatched deployment identity or inactive Slack HITL listener is a release blocker.

## Gate B: exact-once scheduled execution identity

Use a synthetic, non-consequential execution key such as:

```text
ACCEPTANCE-SCHEDULED-IDEMPOTENCY:<UTC timestamp>
```

Call `task.intake` twice with identical fields and the exact same `idempotency_key`.

PASS only if both calls return the same canonical `task_id` and no duplicate task is created.

Advance that task through:

```text
INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA
```

Then call `task.complete` with a non-empty acceptance outcome and evidence reference, followed by a separate `task.verify`.

PASS only if completion produces `COMPLETED` and the separate verification produces `VERIFIED`.

## Gate C: create a synthetic human approval request

Create a separate synthetic task with no external effect. Advance it to `IN_PROGRESS`, then call `approval.request` with:

- approval owner: `michael`
- authority level: L4
- action: `Authorize synthetic v4.1.10 Slack HITL acceptance no-op; payload_fingerprint=<random test fingerprint>`

Record the returned Approval ID and exact test fingerprint. Do not create a Gmail draft or external payload.

`approval.get` must show canonical `PENDING` before the Slack decision.

## Gate D: official OpenAI bot-authored Slack notice

Using the deployed OpenAI Workspace Agent, deliver a new governed HITL notice into `#mesh-agent-ops` containing:

```text
HITL APPROVAL REQUIRED
@MK
Approval ID: <exact canonical Approval ID>
Payload fingerprint: <exact test fingerprint>
Approval owner: MK / Michael
Action: authorize synthetic v4.1.10 acceptance no-op only
```

Provider readback must prove the parent author user ID is the official ChatGPT or ChatGPT Agents identity. A notice authored by MK, another human, or a custom bot is an immediate FAIL.

If the Workspace Agent cannot produce a bot-authored notice, record `BLOCKED_CHATGPT_AGENT_TRANSPORT`. Do not fall back to the generic user-scoped Slack write connector.

## Gate E: bind provider notice evidence through governed MCP

Invoke:

```text
skills.invoke_governed
capability: slack-adapter
payload:
  operation: bind_notice
  approval_id: <exact Approval ID>
  thread_ts: <provider thread timestamp>
  payload_fingerprint: <exact test fingerprint>
```

PASS only if the returned binding proves:

- exact Approval ID;
- exact thread;
- official OpenAI bot notice author;
- configured human approver binding;
- canonical principal `michael`;
- exact payload fingerprint.

Do not expose the configured human Slack ID in the acceptance report.

The CoS adapter must reject any `ingest_decision`, `approved`, actor, principal, or arbitrary Slack payload input.

## Gate F: prove ordinary Slack text is non-authoritative

Post an ordinary, non-consequential Slack thread message containing the exact text:

```text
APPROVE <Approval ID>
```

Do **not** use `/mesh-approval` for this negative control.

Then call `approval.get`. PASS only if the canonical approval remains `PENDING`. Do not attempt an agent-side `ingest_decision` operation because v4.1.10 intentionally exposes no such human-decision path.

This gate proves that an ordinary user-attributed Slack message is evidence only and cannot become canonical human authority.

## Gate G: provider-authenticated human decision through Socket Mode

MK invokes the Slack slash command manually:

```text
/mesh-approval APPROVE <Approval ID>
```

The QNAP runtime must receive a Socket Mode `slash_commands` envelope, validate the governed channel, protected MK identity, exact command and Approval ID, existing provider-verified OpenAI bot notice binding, exact payload fingerprint, and replay state, then record the decision through the non-MCP human-ingress service.

The CoS does **not** invoke this ingress and does not receive a human-decision tool.

Immediately call `approval.get` through Mesh CoS MCP. PASS only if canonical approval state is `APPROVED` for the exact synthetic action and the audit evidence corresponds to the trusted human-ingress decision. No external action is taken.

Negative controls must also be demonstrated in repository/CI evidence: wrong user, wrong channel, wrong command, ordinary message envelope, missing bot binding, non-OpenAI bot parent, unknown Approval ID, fingerprint mismatch, and duplicate/conflicting provider interaction all fail closed.

## Gate H: final governance and mirror reconciliation

1. Run `governance.verify_audit_chain` again and require `valid=true`.
2. Confirm the synthetic scheduled task and synthetic approval task have the expected canonical states.
3. Confirm no Gmail/prospect/publish action occurred.
4. Reconcile the Google TaskLedger operating mirror with the canonical v4.1.10 state and update ProductionPreflight/Operating Guide rows when the exact source connector is available. A stale or unavailable required mirror blocks full production certification but must not be replaced by a shadow workbook.

## Certification rule

Certify v4.1.10 production only when all applicable gates are green and there are **zero open CRITICAL or HIGH defects**.

Repository-green but not-yet-deployed state is `VERIFIED_CANDIDATE`, not production certification.

Official bot transport unavailable, Socket Mode human ingress unavailable, live QNAP release not deployed, or required TaskLedger mirror unreconciled are visible blockers. None may be converted into PASS by prose, screenshots, display names, ordinary Slack messages, or inferred intent.
