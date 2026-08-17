# Phase 1 Operations Runbook

This runbook governs startup, validation, incident response, agent restriction, and controlled restoration for the Phase 1 CoS operating core.

## 1. Preflight

Before enabling production routing:

1. Copy `.env.example` to `.env` and populate only approved runtime configuration.
2. Confirm no credentials, tokens, personal Slack IDs, or protected source exports are committed to the repository.
3. Keep the automation kill switch in its safe state until integration credentials, source permissions, Slack channels, and approval owners are validated.
4. Confirm the private agent-operations Slack channel is `#mesh-agent-ops` with Channel ID `C0BRL4GCL3A`, supplied through `MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID`. Configure the separate team-facing Answer Desk channel ID when available.
5. Configure the Slack bot token and signing secret using the approved secret-management mechanism.
6. Configure authoritative source connectors and requester/source permissions.
7. Confirm approval owners for L4 actions and confirm that L5 remains Michael-exclusive unless explicitly changed.
8. Leave monetary thresholds unset unless Michael has explicitly approved them. Unset thresholds fail closed to approval.

## 2. Verification before routing changes

Run:

```bash
python scripts/validate-contracts.py
pytest
python -m compileall -q src
```

Do not claim a check passed unless it actually ran and passed in the relevant environment. Remote GitHub Actions status and local verification are separate evidence.

## 3. Safe startup posture

Recommended Phase 1 production rollout:

1. Start new or materially changed agents in `SHADOW` where practical.
2. Confirm registry permissions and prohibited actions.
3. Confirm source authority for each functional agent.
4. Confirm Message Operations blocks consequential external sends without required approval.
5. Confirm duplicate Slack/event handling is idempotent.
6. Confirm the kill switch can stop automated actions.
7. Promote routing only after evidence supports the change.

## 4. Normal task operations

Every task must have one accountable owner, expected outcome, success criteria, evidence requirements, authority level, approval gates, dependencies, next check, and acceptance test.

Delegated work is never fire-and-forget. It remains visible until it is `VERIFIED`, `CANCELLED`, or explicitly superseded.

`COMPLETED` is an agent assertion. `VERIFIED` requires the acceptance test to pass.

## 5. Stalled or blocked work

When a task stalls:

1. identify the named blocker or missing dependency
2. update the task state to `BLOCKED` or `AWAITING_INPUT` as appropriate
3. record the evidence gap or dependency
4. assign/request the next action from the correct owner
5. set or update `next_check_at`
6. reassign through CoS if the accountable owner is no longer appropriate
7. escalate only when authority, impact, confidence, or consequence requires it

AgentOps should flag repeated missed deadlines, abandoned work, tool failures, and coordination loops.

## 6. Approval handling

For L4/L5 or other approval-gated actions:

1. prepare the work without executing the consequential action
2. record the approval request and decision owner
3. move the task to `AWAITING_APPROVAL` or `READY_FOR_DECISION` as appropriate
4. preserve the evidence and recommendation supporting the request
5. execute only after the required approval is recorded
6. log the resulting action and approval reference

False claims of approval are critical defects.

## 7. Cross-functional conflict

When functional agents disagree:

1. preserve uncontested facts separately from disputed facts/recommendations
2. determine which source or agent owns each canonical fact
3. create a conflict record for material disagreements
4. use Devil's Advocate review when consequence warrants it
5. have CoS frame the enterprise tradeoff using evidence, authority, consequence, confidence, and reversibility
6. escalate a concise Decision Brief to Michael only if required

Do not use majority voting and do not forward raw agent debates to Michael.

## 8. Critical defect response

Critical examples include unauthorized external action, fabricated material evidence, confidentiality breach, prohibited-source exposure, bypassed approval, irreversible unauthorized action, or false human-approval claims.

Immediate response:

1. activate the automation kill switch when continued execution could create further consequence
2. prevent new routing to the affected agent
3. set the agent to `QUARANTINED` where warranted
4. preserve task, audit, approval, source, and error evidence
5. identify affected tasks and any external consequences
6. verify whether data, client, security, privacy, or commercial escalation is required
7. perform root-cause analysis across policy, prompt/context, source provenance, tool behavior, authority enforcement, and implementation
8. remediate and test before any restoration
9. require Michael approval for material restoration of authority if the incident resulted in a material authority restriction/change

Never delete evidence needed for incident reconstruction.

## 9. WATCH, RESTRICTED, and QUARANTINED recovery

### WATCH
Use for performance degradation or elevated rework. Reduce routing if appropriate, increase review, identify defect patterns, and define remediation evidence.

### RESTRICTED
Use when authority or workload must be reduced. Update permitted actions/routing explicitly and record the reason.

### QUARANTINED
No new production work. Restoration requires root-cause remediation, successful verification, and appropriate approval for any material authority change.

AgentOps recommends changes. CoS may make bounded workload adjustments. Material authority expansion requires Michael.

## 10. Slack incident handling

If Slack emits duplicates or malformed events:

- use idempotency keys/event identity to suppress duplicate work
- do not reconstruct canonical task state solely from Slack history
- preserve one-task-per-thread mapping
- avoid posting protected raw source content when a reference is sufficient
- flag repeated agent exchanges with no state/evidence progress as a coordination loop

If Slack is unavailable, canonical task/event state remains in the ledger. Slack outage does not transfer system-of-record authority to chat history.

## 11. Source outage or stale evidence

If an authoritative source is unavailable, stale, or outside agent permissions:

- mark evidence status accordingly
- do not invent or infer missing canonical facts
- use `Open / Unknown`, `BLOCKED_BY_EVIDENCE`, `AWAITING_INPUT`, or equivalent explicit state
- do not treat stale consultant availability as confirmed
- escalate only if the decision consequence requires action before evidence can be restored

## 12. Controlled shutdown

For planned shutdown:

1. stop new automated routing
2. preserve active task states and audit events
3. identify tasks awaiting approval or external action
4. record incomplete work and next actions
5. revoke/rotate ephemeral credentials where required
6. verify no task is silently represented as completed because execution stopped

## 13. Post-change review

After significant configuration, agent, source, or authority changes:

- rerun contract and behavioral tests
- review AgentOps performance trends
- review escalation quality and rework
- verify source permissions and approval gates
- update ADRs/documentation when architecture or policy changed
- do not expand autonomy solely because an implementation is technically capable of it
