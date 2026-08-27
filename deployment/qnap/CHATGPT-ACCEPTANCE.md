# ChatGPT Secure MCP Tunnel Connection and Acceptance

Run this only after the **v4.1.15** deployment reports successful release-root validation, candidate health, transactional promotion, verification, and post-deploy backup.

The production ChatGPT surface is the published **Mesh CoS MCP** app connected to the QNAP-hosted runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 authority/runtime contract remains **4.0.0**. The QNAP deployment release is independently identified as **4.1.15**.

v4.1.15 uses the connected Slack integration for collaboration only and the custom Slack app only for provider-authenticated `/mesh-approval` Socket Mode human ingress. No Slack verifier-bot credential or bot-authored notice binding is part of the current approval trust model.

## 1. Local deployment identity

Capture:

```sh
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-mcp
sudo docker inspect -f '{{.Config.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' mesh-cos-tunnel
grep '^MESH_COS_DEPLOYMENT_RELEASE=' /share/Docker/cos-mcp/.env
sed -n 's/^version=//p' /share/Docker/cos-mcp/release-metadata.txt
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/healthz').then(r=>r.text()).then(console.log)"
sudo docker exec mesh-cos-mcp node -e "fetch('http://127.0.0.1:8080/readyz').then(r=>r.text()).then(console.log)"
```

PASS requires application image `mesh-cos-mcp:qnap-v4.1.15`, both containers healthy, and:

```text
mcp_version: 4.0.0
deployment_release: 4.1.15
agent_id: cos
transport: SECURE_MCP_TUNNEL
slack_hitl_ready: true
```

Do not print protected Slack or tunnel files.

## 2. Release-root and promotion evidence

Confirm:

- operator release root is `/share/Docker/cos-mcp/releases`;
- retained release directory is `/share/Docker/cos-mcp/releases/v4.1.15`;
- staged and active `release-metadata.txt` report `version=4.1.15` and the released commit;
- no canonical TaskLedger or protected credential exists beneath the versioned release directory;
- active `.env`, Compose, and release metadata all identify v4.1.15;
- no unresolved `.release-rollback.*` recovery snapshot remains after a successful deployment.

Do not delete the versioned release directory during acceptance.

## 3. QNAP network evidence

PASS requires:

- MCP retains qnet `192.168.7.60`;
- tunnel remains private MCP source `172.30.60.3`;
- shared `mesh-cos-private` bridge is internal-only;
- tunnel has dedicated external egress bridge address `172.30.61.2`;
- tunnel does not consume a second qnet address;
- no direct MCP host port is published.

## 4. Slack protected configuration

The deployment must complete without prompting for a Slack approver user ID. The governed user principal is `U01KG3CNYHK` and is materialized into the protected runtime approver identity file.

PASS requires:

- no approver-user-ID prompt during normal deployment;
- a `D...` conversation identifier is never accepted as a user principal;
- only `U...` or `W...` user-principal forms are eligible;
- the protected Socket Mode app-level token is present and valid as `xapp-...`;
- no `xoxb-` verifier token is required, mounted, validated, prompted for, or used by v4.1.15.

## 5. Tool catalog

The CoS-bound published app must expose exactly **27 agent-facing tools**. Human-principal-only `approval.record_decision` and `reliability.human_override` must not appear. The canonical roster remains exactly 10 agents; Mesh Devil's Advocate remains a governed shared Skill rather than an agent principal.

## 6. Request-contract and scheduled idempotency acceptance

Create one synthetic L0 task with documented `task.intake` fields and an explicit `idempotency_key`. Repeat with the same key. PASS requires the same canonical task ID.

Call `task.intake` while omitting `accountable_agent`. PASS requires bounded `validation_failed` details and no raw exception, stack trace, credential, filesystem detail, or private reasoning.

For an existing synthetic task, `task.get` and `task.decompose` using `parent_task_id` must resolve the same canonical identifier. An undocumented alias must fail request validation.

## 7. Governed Skill and connected Slack handoff acceptance

Call `skills.invoke_governed` for an authorized CoS Skill using a synthetic, non-consequential payload. PASS requires bounded `CHATGPT_SKILL_HANDOFF` authorization behavior.

Call CoS `slack-adapter` with:

```text
operation: handoff
channel_id: C0BRL4GCL3A
payload: synthetic collaboration payload
```

PASS requires:

```text
execution_mode: CHATGPT_CONNECTOR_HANDOFF
authority: COLLABORATION_ONLY
```

The handoff must not change approval state. Attempts to pass approval authority fields or operations such as `approved`, `approval_status`, `record_decision`, or `ingest_decision` must fail closed. `approval.record_decision` remains unavailable to the CoS.

## 8. AgentOps acceptance

`agentops.recommend` with the documented minimum contract must succeed. Invalid field names or malformed values must return the same safe structured validation contract used by other tools.

## 9. Lifecycle acceptance

Use a separate synthetic task and advance it through:

```text
INTAKE -> TRIAGED -> PLANNED -> ASSIGNED -> IN_PROGRESS -> QA
```

Call `task.complete` with non-empty outcome and evidence. PASS requires `status=COMPLETED` and no verification yet. Only a separate authorized `task.verify` with acceptance evidence may move it to `VERIFIED`.

## 10. Audit integrity

Call `governance.verify_audit_chain` before and after synthetic acceptance writes. PASS requires `valid: true` both times.

## 11. Slack authenticated human-interaction gate

The runtime must have the protected approver identity, Socket Mode app credential, exact `/mesh-approval` command configuration, and active Socket Mode connection reflected by `slack_hitl_ready=true`.

Create a synthetic PENDING L4 approval owned by canonical principal `michael` whose action contains an immutable 64-hex `payload_fingerprint`.

PASS requires:

- ordinary Slack `APPROVE` text does not alter the approval;
- connected Slack writes do not alter the approval;
- authenticated `/mesh-approval APPROVE <Approval ID>` from verified human user `U01KG3CNYHK` in the governed channel records the canonical decision;
- a different Slack user, different channel, wrong command, missing fingerprint, or distinct conflicting second interaction fails closed;
- replay of the same provider envelope is idempotent;
- durable decision evidence does not persist the protected Slack human user ID;
- a fresh canonical approval read reflects the accepted decision before any consequential executor could act.

The authenticated Socket Mode human ingress is deliberately **not** an MCP tool.

## 12. Provider-degradation gate

A real or controlled Slack provider/network outage must not terminate the MCP HTTP process. PASS requires `/healthz` to remain available, `/readyz` to report not ready for required Slack HITL, consequential approval to remain blocked, and bounded reconnect behavior to continue.

## 13. Multi-agent boundary

Repository/container certification establishes immutable `MESH_COS_AGENT_ID` binding and exact allowlists for all 10 agents. A CoS session reading another registry record is not equivalent to a separately authenticated downstream-agent hosted session.

## 14. Consequential-action exclusion

Do not perform prospect sends, public publishing, client commitments, pricing/discount approvals, final staffing commitments, reliability human overrides, or other consequential real-world actions during acceptance. Slack acceptance uses a synthetic no-op approval only.

## 15. Pass rule

Base v4.1.15 hosted acceptance passes only when the actual Mesh CoS MCP app demonstrates correct dual release identity, release-root provenance, deterministic QNAP network identity, `slack_hitl_ready=true`, exact schema behavior, safe validation, canonical TaskLedger lookup, scheduled idempotency, lifecycle separation, governed Skill/Slack handoff enforcement, AgentOps contract, authorization boundaries, and valid audit chain.

Full production certification additionally requires `chatgpt-published-app-production-acceptance-v4.1.15.md`, including connected Slack collaboration-only behavior, authenticated `/mesh-approval` from the verified approver, canonical approval readback, replay/negative tests, no unauthorized external action, and required TaskLedger mirror reconciliation. Zero open CRITICAL/HIGH defects and no required acceptance blocker are mandatory.
