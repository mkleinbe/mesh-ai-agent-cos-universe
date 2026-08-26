# v4.1.13 Slack Approver Bootstrap

`v4.1.13` supersedes v4.1.12 for QNAP deployment. v4.1.12 successfully corrected release-root pathing, but its Slack HITL configuration still asked the operator to enter the human approver Slack user ID. Slack displayed `D01K4CL2F8F` as a **Channel ID** in the profile pane; that value identifies a direct-message/conversation channel and is not a Slack user principal, so the v4.1.12 script correctly rejected it.

The verified Slack user principal for Michael/MK is `U01KG3CNYHK`. v4.1.13 ships that non-secret identifier as the governed approver default and removes interactive approver-user-ID entry entirely.

The canonical Phase 1 authority/runtime contract remains **`4.0.0`** with exactly 10 registered agents and 27 governed CoS MCP tools. Human-only operations remain human-only. Message Operations remains one of the 10 agents; Mesh Devil's Advocate remains a governed shared Skill and is not an agent principal.

## Core changes

- Human approver principal Michael/MK is bound to verified Slack user ID `U01KG3CNYHK`.
- Deployment no longer prompts for the approver Slack user ID.
- A missing protected approver identity file is populated automatically from the governed default.
- An existing approver identity file is validated before preservation.
- Forced Slack HITL reconfiguration restages the governed user ID without prompting for it.
- `D...` conversation/DM channel identifiers fail closed with an explicit diagnostic explaining that they are not user IDs.
- Only Slack `U...` or `W...` user-principal forms are accepted.
- Slack verifier `xoxb-...` and Socket Mode `xapp-...` credentials remain protected runtime secrets and are not embedded in the release artifact.
- The v4.1.12 release-root contract remains intact: `/share/Docker/cos-mcp/releases` is the only operator working directory, and extraction creates the versioned release folder automatically.

## Security boundary

Security applicability is **TARGETED**. See `docs/qnap-security-review-v4.1.13.md`.

The Slack user ID is treated as non-secret governed configuration. Actual Slack credentials, the OpenAI tunnel runtime key, generated runtime environment, canonical TaskLedger, and state directory remain excluded from the release artifact. Runtime secret files remain protected and read-only.

## BDD and TDD evidence

Ready scenarios QNAP-092 through QNAP-099 in `specs/qnap-slack-approver-bootstrap-v4.1.13.feature` cover non-interactive approver bootstrap, conversation-ID rejection, accepted user-principal formats, preservation and forced reconfiguration, continued secret isolation, unchanged release-root/authority boundaries, and completion/verification separation.

Historical QNAP-083 through QNAP-091 and SCH-HITL-001 through SCH-HITL-007 remain retained as regression evidence.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.13.zip`
- `mesh-cos-mcp-qnap-v4.1.13.zip.sha256`

## Version identity

- Repository/QNAP deployment release: `4.1.13`
- Semantic tag: `v4.1.13`
- Container image label default: `4.1.13-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Workforce: exactly 10 agents
- CoS agent-facing catalog: 27 governed tools
- Production transport: OpenAI Secure MCP Tunnel
- Human Slack approval ingress: authenticated Slack Socket Mode `/mesh-approval`

Successful hosted readiness after deployment must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.13
agent_id: cos
slack_hitl_ready: true
```

## Verification gate

The exact final candidate must pass dependency integrity, TypeScript/npm checks, contract/document/package drift checks, Ruff, mypy, 100 percent branch-aware Python coverage, Bandit, compileall, QNAP POSIX shell regressions, real v4.1.13 archive-prefix inspection, Slack approver-bootstrap artifact inspection, checksum generation, Compose validation, OCI provenance, modern MCP discovery/sequential requests, protected Slack HITL controls, non-root/read-only runtime controls, direct-ingress denial, restart/persistence, and Docker-mediated SQLite backup integrity.

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the actual on-premises serving instance, official OpenAI Workspace Agent Slack delivery, or live Slack Socket Mode human interaction.

After deploying v4.1.13, execute `docs/chatgpt-published-app-production-acceptance-v4.1.13.md`. Do not certify production while any CRITICAL/HIGH defect or required live acceptance blocker remains open.

See:

- `docs/qnap-slack-approver-bootstrap-v4.1.13.md`
- `docs/qnap-security-review-v4.1.13.md`
- `docs/verification-v4.1.13-slack-approver-bootstrap.md`
- `docs/release-4.1.13-slack-approver-bootstrap.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.13.md`
- `specs/qnap-slack-approver-bootstrap-v4.1.13.feature`
- `specs/qnap-release-root-bootstrap-v4.1.12.feature`
- `specs/scheduled-automation-slack-hitl-v4.1.10.feature`
- `docs/slack-agent-protocol.md`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
