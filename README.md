# Mesh AI Chief of Staff Agent Universe

Production operating core for Mesh Digital LLC's governed AI Chief of Staff workforce.

**Current repository/QNAP deployment target: `v4.1.18 QNAP Slack Bot Secret Permission Hotfix`.**

The canonical Phase 1 agent authority/runtime contract remains **`4.0.0`**. The `4.1.x` deployment train packages and hardens the QNAP container, remote MCP transport, OpenAI Secure MCP Tunnel integration, operating controls, scheduled execution, Slack HITL, request contract, transactional deployment recovery, backup integrity, and release evidence without widening the Phase 1 agent authority model.

## Canonical Phase 1 architecture

Phase 1 contains exactly **10 registered agents**: Chief of Staff, AgentOps Controller, Answer & Decision Desk, CRO, CFO, COO, Consultant Network Steward, CMO, VP Content, and Message Operations.

**Mesh Devil's Advocate is not an eleventh agent.** It remains an external governed shared Skill, advisory only, available to authorized agents. It cannot own tasks, decide approvals, overwrite canonical facts, or execute external actions.

`TaskLedger` remains canonical state. ChatGPT, Slack, connectors, Workspace app state, governance Sheets, and shared-Skill packets remain interaction, evidence, or mirror surfaces.

## Production ChatGPT topology

The published **Mesh CoS MCP** ChatGPT app is the production ChatGPT surface. The QNAP deployment target is **4.1.18** while the canonical MCP runtime/product version remains **4.0.0**.

Governed Slack HITL uses the dedicated **ChatGPT Enterprise AI Agent** Slack bot for outbound approval cards and provider-authenticated Socket Mode for human thread replies and Block Kit interactions. The connected ChatGPT Slack integration is not canonical approval authority.

## Repository layout

- `src/mesh_cos/`: canonical Python operating core and governance runtime.
- `mcp/`: remote MCP transport and Socket Mode bridge.
- `deployment/qnap/`: QNAP Container Station deployment, verification, backup, rollback, and acceptance assets.
- `chatgpt/`: published ChatGPT app contracts and package evidence.
- `specs/`: ready BDD behavior specifications.
- `tests/`: unit, integration, evaluation, security, and production-readiness tests.
- `docs/`: architecture, release, verification, security, and acceptance evidence.

## Current release

v4.1.18 is a targeted deployment hotfix over v4.1.17. It repairs QNAP protected-file ownership for the dedicated Slack bot OAuth credential so the non-root runtime can read the already-provisioned `xoxb-` token while the file remains mode `0400`. No Slack, approval, agent, TaskLedger, or MCP authority is widened.

v4.1.17 remains the behavior-bearing Slack HITL release: dedicated-bot Block Kit approval cards, case-insensitive authenticated thread replies, and human actions **Approve**, **Deny**, and **Change** without typing an approval ID. v4.1.18 preserves that contract plus the v4.1.16 restarting-runtime backup and rollback controls.

See:

- `docs/release-4.1.18-qnap-slack-bot-secret-permissions.md`
- `docs/security-review-v4.1.18.md`
- `docs/verification-v4.1.18-qnap-slack-bot-secret-permissions.md`
- `docs/release-4.1.17-slack-bot-block-kit-hitl.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.18.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`

Historical versioned documents remain retained as release-train evidence.
