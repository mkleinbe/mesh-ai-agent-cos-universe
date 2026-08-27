# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.2.0 Native Slack Event-Triggered HITL`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, event-triggered execution, Slack HITL, request contract, transactional deployment recovery, backup integrity, and release evidence without widening the Phase 1 agent authority model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface. The QNAP deployment target is **4.2.0** while the canonical MCP runtime/product version remains **4.0.0**.

Governed Slack HITL uses the dedicated **ChatGPT Enterprise AI Agent** Slack bot for outbound approval notices and server-side provider reconciliation. New MK thread replies wake a single ChatGPT-native Slack event-triggered dispatcher task. The trigger itself is not approval authority. Mesh CoS MCP re-reads the exact Slack provider message and canonical TaskLedger state before a human decision can be recorded.

QNAP no longer owns Slack event ingress, does not start a Slack Socket Mode listener, and does not require an `xapp-` Socket Mode credential. OpenAI Secure MCP Tunnel remains the only remote MCP ingress.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core, governance runtime, Slack bot, and native-trigger reconciliation.
- `mcp/`: remote MCP transport. Historical Socket Mode compatibility source remains retained but is not started by the v4.2.0 production runtime.
- `deployment/qnap/`: QNAP Container Station deployment, verification, backup, rollback, and acceptance assets.
- `chatgpt/`: published ChatGPT app contracts and package evidence.
- `specs/`: ready BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, and production-readiness tests.
- `docs/`: architecture, release, verification, security, dispatcher, and acceptance evidence.

## Current release

v4.2.0 is a behavior-bearing Slack HITL architecture release. It replaces the v4.1.17/v4.1.18 Socket Mode ingress with ChatGPT-native Slack new-message triggers while preserving the same protected human principal, canonical thread/fingerprint binding, fail-closed decision grammar, TaskLedger authority, and human-only MCP operations.

Approval notices are reply-driven with **APPROVE**, **DENY**, and **CHANGE**. Block Kit decision buttons are removed because button interactions are not new-message trigger events. The dispatcher may pass only Slack thread and message timestamps. Slack message text, asserted sender identity, approval state, and decision fields are rejected at the MCP adapter boundary and re-derived server-side.

See:

- `RELEASE.md`
- `docs/release-4.2.0-native-slack-event-hitl.md`
- `docs/security-review-v4.2.0.md`
- `docs/chatgpt-native-slack-dispatcher-v4.2.0.md`
- `docs/chatgpt-published-app-production-acceptance-v4.2.0.md`
- `docs/verification-v4.2.0-native-slack-event-hitl.md`
- `specs/native-slack-event-hitl-v4.2.0.feature`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

Historical versioned documents remain retained as release-train evidence.