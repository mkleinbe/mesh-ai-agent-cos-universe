# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.1.14 QNAP Protected-Secret Provisioning Remediation`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, scheduled execution, Slack HITL, request contract, and release evidence without widening the Phase 1 agent authority model.

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

Successful governed tool envelopes for v4.1.14 must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.14
agent_id: cos
```

Production `/healthz` and `/readyz` additionally report `transport: SECURE_MCP_TUNNEL`. When Slack HITL is required, readiness also reports `slack_hitl_ready=true` only while the authenticated Socket Mode boundary is active.

`mcp_version` identifies the canonical Phase 1 authority/runtime contract. `deployment_release` identifies the QNAP deployment release serving the request. Remote production startup fails closed if `MESH_COS_DEPLOYMENT_RELEASE` is absent.

## v4.1.14 deployment remediation

v4.1.14 supersedes v4.1.13 for QNAP protected-secret provisioning while retaining the governed Slack approver bootstrap and all earlier runtime controls.

1. Normal upgrades validate and preserve existing Slack verifier and Socket Mode credentials without prompting.
2. The normal Slack configuration path no longer depends on `stty` or any hidden interactive secret-entry routine.
3. Missing or invalid Slack credentials fail closed and direct the operator to `mesh-cos-slack-hitl-provision.sh`.
4. First-time or deliberate Slack credential provisioning is isolated in that explicit operator command.
5. A shared QNAP/BusyBox secret-input helper prefers shell-native silent read, falls back to an explicitly resolved `stty` binary only during provisioning, and refuses to capture a secret when terminal echo cannot be disabled safely.
6. The same deployment-path pressure test found and removed the equivalent hidden-input dependency for a missing OpenAI tunnel runtime key. Tunnel key provisioning is now isolated in `mesh-cos-tunnel-key-provision.sh`.
7. Provisioned secrets are never placed on a command line, embedded in release artifacts, or intentionally emitted to deployment logs, and their runtime ownership/mode is normalized to `65532:65532` / `0400`.
8. The verified Slack human principal remains `U01KG3CNYHK`; `D...` conversation IDs remain invalid human principals.
9. Canonical TaskLedger, Secure MCP Tunnel ingress, exactly 10 agents, 27 governed CoS tools, human-only operations, and `COMPLETED != VERIFIED` remain unchanged.
10. Repository or release verification does not constitute production acceptance. QNAP, hosted MCP, published ChatGPT app, and live Slack HITL acceptance remain required after deployment.

## v4.1.13 capability retained

v4.1.13 established the governed Slack human-approver bootstrap: Michael/MK is bound to Slack user principal `U01KG3CNYHK`; the operator is not prompted for that non-secret identity; `D...` conversation IDs fail closed; existing valid identity files are preserved; and Slack verifier and Socket Mode credentials remain protected runtime secrets.

## v4.1.12 release-root contract retained

The QNAP artifact/pathing remediation introduced by v4.1.12 remains mandatory: release ZIPs contain a single top-level `vX.Y.Z/` directory, operator scripts self-resolve their helper paths, release-directory identity is bound to staged metadata, candidate files stay in the versioned release directory until health succeeds, and active production files are promoted only after both application and tunnel containers are healthy.

## v4.1.10 capability retained

The scheduled execution and Slack HITL hardening introduced by v4.1.10 remains current: immutable scheduled idempotency keys, canonical lifecycle progression, official OpenAI bot notice binding, protected Slack human identity, provider verification, authenticated non-MCP Socket Mode `/mesh-approval`, non-authoritative ordinary Slack text, and fail-closed readiness. Agents still cannot record human approval decisions.

## Authority boundary

Every MCP process is immutably bound through `MESH_COS_AGENT_ID`. Prompt text, retrieved content, task content, delegated instructions, connector content, Slack text, and shared-Skill output cannot change identity or widen the tool catalog.

The CoS production projection remains exactly **27 governed tools**. L4 requires qualified-human approval and L5 remains Michael-exclusive.

## Completion and verification

`task.complete` requires outcome and evidence and produces `COMPLETED` only. `task.verify` remains a separate CoS verification operation requiring acceptance evidence. **COMPLETED != VERIFIED.**

## Production acceptance

Repository, CI, container, and release-package verification do not prove the newly deployed on-premises serving instance, the official OpenAI Workspace Agent Slack delivery configuration, or the live Socket Mode human-interaction path.

After deploying v4.1.14, execute `docs/chatgpt-published-app-production-acceptance-v4.1.14.md`. Production certification requires the actual bot-authored HITL notice, proof ordinary APPROVE text remains non-authoritative, a provider-authenticated `/mesh-approval` interaction from the verified human approver, fresh canonical approval readback, valid audit chain, zero unauthorized external actions, and required TaskLedger operating-mirror reconciliation.

Current operator and release references:

- `SECURITY.md`
- `RELEASE.md`
- `docs/production-readiness.md`
- `docs/slack-agent-protocol.md`
- `docs/qnap-security-review-v4.1.14.md`
- `docs/release-4.1.14-qnap-slack-secret-provisioning.md`
- `docs/verification-v4.1.14-qnap-slack-secret-provisioning.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.14.md`
- `specs/qnap-slack-secret-provisioning-v4.1.14.feature`
- `docs/qnap-slack-approver-bootstrap-v4.1.13.md`
- `specs/qnap-slack-approver-bootstrap-v4.1.13.feature`
- `specs/qnap-release-root-bootstrap-v4.1.12.feature`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `deployment/qnap/README-QNAP.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
- `deployment/qnap/install-checklist.md`
- `deployment/qnap/upgrade-checklist.md`

Historical versioned documents remain retained as release-train evidence.
