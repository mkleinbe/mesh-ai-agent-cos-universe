# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.3.0 Cross-Agent Owner Execution`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, event-triggered execution, Slack HITL, delegated owner execution, request contracts, transactional deployment recovery, backup integrity, and release evidence without widening the Phase 1 decision-rights model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface. The QNAP deployment target is **4.3.0** while the canonical MCP authority/runtime contract remains **4.0.0**.

v4.3.0 repairs PF-057 systemically. Delegated canonical work is executed through the server-owned `delegation.execute_owner` path. The caller does not supply an owner or principal. Mesh CoS MCP derives the accountable owner from canonical TaskLedger and delegation state, validates the Agent Registry and owner allowlist, executes under the owner-scoped policy context, and preserves owner-only completion. Parent agents cannot complete child work by impersonation. `COMPLETED != VERIFIED` remains enforced.

The CoS governed agent catalog contains **28 tools**, including `delegation.execute_owner`. Human-only `approval.record_decision` and `reliability.human_override` remain excluded from agent execution.

Governed Slack HITL continues to use the dedicated **ChatGPT Enterprise AI Agent** Slack bot for outbound approval notices and server-side provider reconciliation. New MK thread replies wake a single ChatGPT-native Slack event-triggered Work task. The trigger is not approval authority. Mesh CoS MCP rereads the exact Slack provider message and canonical TaskLedger state before a human decision can be recorded.

The provider-verified Slack App ID remains `A0B49RNE4K0`. The v4.2.3 Slack/qnet controls remain part of v4.3.0 unchanged: authenticated GET/query provider reads, bounded retry only for pre-provider qnet/network exceptions, and fail-closed provider authorization or response errors.

QNAP does not own Slack event ingress, does not start a Slack Socket Mode listener, and does not require an `xapp-` Socket Mode credential. OpenAI Secure MCP Tunnel remains the only remote MCP ingress.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core, governance runtime, delegated owner execution, Slack bot, and native-trigger reconciliation.
- `mcp/`: remote MCP transport. Historical Socket Mode compatibility source remains retained but is not started by the production runtime.
- `deployment/qnap/`: QNAP Container Station deployment, verification, backup, rollback, and acceptance assets.
- `chatgpt/`: published ChatGPT app contracts and package evidence.
- `specs/`: ready BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, scheduled-workflow, and production-readiness tests.
- `docs/`: architecture, material-turn, release, verification, security, dispatcher, Skill-package, and acceptance evidence, including Mermaid architecture/sequence diagrams.

## Material-turn documentation

Material changes must follow `docs/material-turn-documentation-standard.md`. Each material turn must leave enough repository evidence to reconstruct the business/technical trigger, architecture and trust-boundary change, executable behavior, security applicability, verification, updated Skills or agent packages, semantic version, release artifacts, deployment/recovery, rollback, and exact commit/tag/release identity.

The complete v4.3.0 turn record is `docs/material-turn-v4.3.0.md`; its updated ChatGPT Skill manifest is `docs/skills-v4.3.0.md`.

## Current release

v4.3.0 is a feature-level deployment release because it adds a governed MCP operation and closed-loop delegation/execution protocol. It does not change the 10-agent roster, L4/L5 human authority, canonical TaskLedger model, or functional decision-rights boundaries.

The existing **Mesh Slack HITL Dispatcher** remains one locator-only event bridge and stays version-family labeled `Mesh CoS MCP v4.x`. The Slack app manifest remains v4.2.3 because v4.3.0 does not require a Slack app scope or event-subscription change.

See:

- `RELEASE.md`
- `CHANGELOG-v4.3.0.md`
- `docs/material-turn-documentation-standard.md`
- `docs/material-turn-v4.3.0.md`
- `docs/skills-v4.3.0.md`
- `docs/pf-057-cross-agent-owner-execution.md`
- `docs/release-4.3.0-cross-agent-owner-execution.md`
- `docs/security-review-v4.3.0-cross-agent-owner-execution.md`
- `docs/verification-v4.3.0-cross-agent-owner-execution.md`
- `docs/chatgpt-published-app-production-acceptance-v4.3.0.md`
- `specs/cross-agent-owner-execution.feature`
- `docs/chatgpt-native-slack-dispatcher-v4.2.3.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

Historical versioned documents remain retained as release-train evidence.
