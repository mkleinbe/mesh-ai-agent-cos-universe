# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.2.1 Native Slack HITL Decision Compatibility`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, event-triggered execution, Slack HITL, request contract, transactional deployment recovery, backup integrity, and release evidence without widening the Phase 1 agent authority model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface. The QNAP deployment target is **4.2.1** while the canonical MCP runtime/product version remains **4.0.0**.

Governed Slack HITL uses the dedicated **ChatGPT Enterprise AI Agent** Slack bot for outbound approval notices and server-side provider reconciliation. New MK thread replies wake a single ChatGPT-native Slack event-triggered Work task. The trigger itself is not approval authority. Mesh CoS MCP re-reads the exact Slack provider message and canonical TaskLedger state before a human decision can be recorded.

v4.2.1 fixes the production acceptance defect where Slack provider text for a bold decision reply was observed as `*APPROVE*`. The server now removes exactly one whole-message Slack `*...*` wrapper and then applies the same exact APPROVE / DENY / CHANGE grammar. Nested, partial, unknown, wrong-user, edited, unbound, stale-fingerprint, and conflicting replay cases remain fail closed.

QNAP does not own Slack event ingress, does not start a Slack Socket Mode listener, and does not require an `xapp-` Socket Mode credential. OpenAI Secure MCP Tunnel remains the only remote MCP ingress.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core, governance runtime, Slack bot, and native-trigger reconciliation.
- `mcp/`: remote MCP transport. Historical Socket Mode compatibility source remains retained but is not started by the production runtime.
- `deployment/qnap/`: QNAP Container Station deployment, verification, backup, rollback, and acceptance assets.
- `chatgpt/`: published ChatGPT app contracts and package evidence.
- `specs/`: ready BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, and production-readiness tests.
- `docs/`: architecture, release, verification, security, dispatcher, and acceptance evidence, including Mermaid architecture/sequence diagrams.

## Current release

v4.2.1 is a patch to the v4.2.0 ChatGPT-native Slack HITL architecture. It does not change the dispatcher trigger, MCP tool catalog, agent registry, canonical state model, Slack scopes, or authority boundary. The existing **Mesh Slack HITL Dispatcher** remains a locator-only event bridge and should only have its release label changed from `v4.2.0` to `v4.2.1` after deployment.

See:

- `RELEASE.md`
- `docs/release-4.2.1-slack-rendered-decision.md`
- `docs/security-review-v4.2.1.md`
- `docs/chatgpt-native-slack-dispatcher-v4.2.1.md`
- `docs/chatgpt-published-app-production-acceptance-v4.2.1.md`
- `docs/verification-v4.2.1-slack-rendered-decision.md`
- `specs/native-slack-event-hitl-v4.2.1.feature`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

Historical versioned documents remain retained as release-train evidence.
