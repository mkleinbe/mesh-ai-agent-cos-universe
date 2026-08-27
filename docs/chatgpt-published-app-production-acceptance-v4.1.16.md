# ChatGPT Published App Production Acceptance v4.1.16

Run only after the QNAP v4.1.16 deployment script reports successful pre-deploy backup, candidate health, promotion, verification, and post-deploy backup.

## Local release identity

PASS requires:

- application image `mesh-cos-mcp:qnap-v4.1.16`;
- active deployment release `4.1.16`;
- both `mesh-cos-mcp` and `mesh-cos-tunnel` healthy;
- `mcp_version=4.0.0`;
- `agent_id=cos`;
- `transport=SECURE_MCP_TUNNEL`;
- `slack_hitl_ready=true`.

## Restarting-runtime backup remediation

For an upgrade from a restarting prior runtime, deployment evidence must show:

- source container state was recognized as restarting rather than stable running;
- `docker exec` was not used for that source backup;
- the old runtime was quiesced before SQLite state backup;
- `state_export_method=quiesced_helper` is recorded in the resulting backup evidence;
- the helper used the active Mesh image with no network and no protected secret mounts;
- the pre-deploy backup passed SHA-256 verification;
- deployment continued into candidate preparation after the backup gate.

No TaskLedger file may be manually copied, replaced, or deleted to make acceptance pass.

## Published MCP acceptance

Through the installed **Mesh CoS MCP** app:

1. Confirm exactly 27 agent-facing CoS tools and exactly 10 registered agents.
2. Confirm human-only `approval.record_decision` and `reliability.human_override` are absent from the agent-facing catalog.
3. Confirm governed responses report `mcp_version=4.0.0`, `deployment_release=4.1.16`, and `agent_id=cos`.
4. Confirm `governance.verify_audit_chain` returns valid.
5. Confirm lifecycle separation `COMPLETED != VERIFIED` using synthetic non-consequential state.

## Slack HITL acceptance

The connected Slack integration remains collaboration-only. Ordinary Slack messages, reactions, or connector-authored content must not change canonical approval state.

PASS requires one synthetic provider-authenticated `/mesh-approval APPROVE <Approval ID>` Socket Mode interaction from the governed human approver and a fresh canonical approval readback. The same action from a non-governed Slack user must fail closed.

## Consequential-action exclusion

Do not perform a real prospect send, public publication, client commitment, pricing approval, staffing commitment, or other consequential external action during acceptance.

## Pass rule

Production acceptance requires zero open CRITICAL/HIGH defects and no required acceptance blocker across the QNAP deployment, Secure MCP Tunnel, published Mesh CoS MCP app, canonical TaskLedger, and provider-authenticated Slack human decision path.
