# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.1.15 QNAP Slack Plugin HITL Simplification`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, scheduled execution, Slack HITL, request contract, transactional deployment recovery, and release evidence without widening the Phase 1 agent authority model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface:

```text
ChatGPT / Mesh CoS MCP app
  -> OpenAI Secure MCP Tunnel
  -> mesh-cos-tunnel 172.30.60.3
  -> mesh-cos-mcp 172.30.60.2 + 192.168.7.60
  -> canonical mesh_cos.mcp_runtime.MCPRuntime
  -> TaskLedger SQLite
```

Local engineering and deterministic certification retain stdio:

```text
local MCP client
  -> node mcp/dist/index.js
  -> mesh_cos.mcp_stdio_bridge
  -> canonical MCPRuntime
  -> TaskLedger SQLite
```

The canonical QNAP application root remains `/share/Docker/cos-mcp` and uses the verified external QNAP `lan7` qnet. The stable operator release root is `/share/Docker/cos-mcp/releases`. Starting with v4.1.12, the release ZIP itself creates its `vX.Y.Z/` subdirectory when extracted from that root. Operator/helper scripts resolve from their own versioned directory and must not be copied to `/share/Docker`. The MCP protocol port is not published to the host or public internet. Production `/mcp` requests are accepted only from the Secure MCP Tunnel sidecar private source address.

## Dual release identity

Successful governed tool envelopes for v4.1.15 must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.15
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`. When Slack HITL is required, readiness reports `slack_hitl_ready=true` only while the authenticated Socket Mode boundary is active.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## v4.1.15 Slack HITL and deployment hardening

v4.1.15 supersedes v4.1.14 for QNAP deployment and removes the unnecessary Slack verifier-bot layer.

1. The connected Slack integration is collaboration-only. CoS `slack-adapter` returns `CHATGPT_CONNECTOR_HANDOFF` with `COLLABORATION_ONLY` authority and cannot record, infer, or carry canonical human approval.
2. The custom Slack app remains only as the provider-authenticated `/mesh-approval` Socket Mode ingress. The runtime requires the protected `xapp-` app-level token and governed approver identity, not an `xoxb-` verifier bot token.
3. Ordinary Slack messages, reactions, copied command text, connector-authored content, and display names remain non-authoritative.
4. Provider-authenticated approval ingress verifies exact channel, user, command, PENDING state, owner, replay state, and immutable 64-hex `payload_fingerprint` before changing canonical approval state.
5. Slack provider/network failure does not terminate the MCP HTTP process. `/healthz` remains available, `/readyz` fails closed, and Socket Mode reconnect uses bounded backoff.
6. QNAP Docker Engine 27 network ambiguity is removed: the MCP keeps qnet `192.168.7.60` as its only external-capable network, the shared MCP/tunnel bridge is internal, and the tunnel receives a dedicated egress bridge for OpenAI control-plane traffic.
7. Candidate failure before promotion restores the previously active stack without advancing release metadata.
8. Active `.env`, Compose, and release metadata are snapshotted before promotion. Partial promotion or post-promotion verification failure restores the exact pre-promotion state and previous active stack.
9. Failed rollback preserves its recovery snapshot for operator recovery and evidence. Successful post-deploy verification is the promotion transaction commit point.
10. Canonical TaskLedger, Secure MCP Tunnel ingress, exactly 10 agents, 27 governed CoS tools, human-only operations, and `COMPLETED != VERIFIED` remain unchanged.

Ready BDD scenarios QNAP-104 through QNAP-111 are defined in `specs/qnap-slack-plugin-hitl-v4.1.15.feature`.

## Retained release contracts

v4.1.14 established explicit protected-secret provisioning for QNAP/BusyBox environments and removed hidden secret entry from ordinary deployment. Those safe provisioning controls remain available where still applicable, including the OpenAI tunnel key provisioner.

v4.1.13 established the governed Slack human-approver bootstrap: Michael/MK is bound to Slack user principal `U01KG3CNYHK`; the operator is not prompted for that non-secret identity; `D...` conversation IDs fail closed; and existing valid identity files are preserved.

v4.1.12 established the release-root contract: release ZIPs contain a single top-level `vX.Y.Z/` directory, operator scripts self-resolve their helper paths, release-directory identity is bound to staged metadata, candidate files stay in the versioned release directory until health succeeds, and active production files are promoted only after candidate health.

v4.1.10 established scheduled execution and Slack HITL foundations: immutable scheduled idempotency keys, canonical lifecycle progression, protected Slack human identity, authenticated non-MCP `/mesh-approval`, non-authoritative ordinary Slack text, and fail-closed readiness. v4.1.15 simplifies the collaboration side of this model while preserving the human-only decision boundary.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, Slack text, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. L4 requires qualified-human approval and L5 remains Michael-exclusive. `approval.record_decision` and `reliability.human_override` remain human-principal-only and outside the agent-facing MCP catalog.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verification operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

Repository, CI, container, and release-package verification do not prove the newly deployed on-premises serving instance, the live Secure MCP Tunnel route, or the provider-authenticated Slack human-interaction path.

After deploying v4.1.15, execute `docs/chatgpt-published-app-production-acceptance-v4.1.15.md`. Production certification requires the actual QNAP runtime, hosted MCP acceptance, proof ordinary Slack text remains non-authoritative, a provider-authenticated `/mesh-approval` interaction from the governed human approver, fresh canonical approval readback, valid audit chain, zero unauthorized external actions, and required TaskLedger operating-mirror reconciliation.

Current operator and release references:

- `SECURITY.md`
- `RELEASE.md`
- `docs/production-readiness.md`
- `docs/slack-agent-protocol.md`
- `docs/engineering-contract-v4.1.15.md`
- `docs/implementation-plan-v4.1.15.md`
- `docs/security-review-v4.1.15.md`
- `docs/release-4.1.15-slack-plugin-hitl.md`
- `docs/verification-v4.1.15-slack-plugin-hitl.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.15.md`
- `specs/qnap-slack-plugin-hitl-v4.1.15.feature`
- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `deployment/qnap/install-checklist.md`
- `deployment/qnap/upgrade-checklist.md`

Historical versioned documents remain retained as release-train evidence.
