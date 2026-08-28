# Runbook: v4.4.0 Authority and Execution

## Scope

Operational procedures for the v4.4.0 Mesh CoS MCP authority model, delegated owner execution, capability closure, publication attestation, and production provenance.

## Preflight

1. Confirm the repository candidate SHA.
2. Confirm CI is green for that exact SHA.
3. Confirm `python scripts/check-owner-execution-readiness.py` reports PASS.
4. Confirm `python scripts/check-capability-closure.py` reports PASS.
5. Confirm `python scripts/check-published-action-surface.py` reports `SOURCE_CONTRACT_ONLY` before workspace publication and never falsely reports publication PASS without `--actual-file`.
6. Confirm the QNAP candidate artifact checksum and container revision equal the candidate SHA.

## Delegated owner execution

For a delegated task:

1. Canonical task owner must exist and be ACTIVE/routable.
2. Canonical delegation must bind the parent owner, child owner, task, authority, approval gates, permitted actions, and permitted capabilities.
3. Call `delegation.execute_owner` using `protocol_version=mesh.cos.owner-execution.v2`.
4. The caller supplies no owner identity. The server derives the accountable owner from canonical delegation state.
5. For `skills.invoke_governed`, capability must be explicitly present in the delegation and in the owner registry.
6. Consequential execution resolves canonical approval before the action.
7. Inspect the `owner_execution` receipt and `owner_execution_route` after success or denial.

## Approval troubleshooting

A rejected L4/L5 operation should be diagnosed in this order:

- approval record exists for the exact task;
- status is `APPROVED`;
- approval authority meets or exceeds requested authority;
- approval owner is a qualified human principal;
- `decided_by` equals `approval_owner`;
- action matches the governed action;
- caller-supplied approver, when present, matches canonical evidence;
- L5 canonical actor is Michael.

Do not repair an approval failure by changing task authority, bypassing Message Operations, or accepting a string approval reference that has no canonical record.

## Nested delegation troubleshooting

Supported nested routes are registry-derived. Current bounded routes include:

- `cos -> cmo -> vp-content`
- `cos -> coo -> consultant-network-steward`

A nested execution must:

- be created by the canonical current owner;
- descend from the current delegated task;
- target the canonical nested child task;
- remain within delegation depth and capability bounds.

Do not route a nested task through CoS under the child's identity as a workaround.

## Publication acceptance

After a human administrator refreshes/recreates the ChatGPT custom app:

1. Export/capture the actual published/draft tool snapshot including `name` and `inputSchema` for every action.
2. Save the snapshot as JSON in the accepted structure: `{ "tools": [{"name": ..., "inputSchema": ...}, ...] }`.
3. Run `python scripts/check-published-action-surface.py --actual-file <snapshot.json>`.
4. Require exact 28/28 machine actions for the CoS surface.
5. Require zero unexpected actions.
6. Require exact input-schema equality for every action.
7. Require human-only `approval.record_decision` and `reliability.human_override` to remain absent from the agent-published surface.
8. Record the resulting schema digest and compare it to runtime `publication_schema_digest`.

Only then may the Workspace publication gate move to PASS.

## Production provenance verification

After human deployment of v4.4.0:

1. Call any safe MCP read operation.
2. Verify `mcp_version=4.0.0`.
3. Verify `deployment_release=4.4.0`.
4. Verify `source_commit` equals the merged release candidate commit.
5. Verify `publication_schema_digest` equals the accepted ChatGPT snapshot digest for the bound principal.
6. Verify the registry contains exactly 10 ACTIVE agents and canonical parentage.
7. Verify the audit chain is valid.
8. Run safe synthetic delegated owner tests for direct and nested routes.
9. Confirm `COMPLETED != VERIFIED` through a negative verifier-separation test.

## Rollback

If the v4.4.0 deployment fails production verification:

- preserve TaskLedger state and approval evidence;
- stop new delegated/consequential execution;
- roll back the QNAP container/image using the existing versioned release and backup procedures;
- restore the last verified deployment release;
- do not rewrite or delete failed execution/audit receipts;
- keep the ChatGPT app on the last accepted publication snapshot until the replacement source and schema are reverified.

## Manual control boundary

Git tag/GitHub Release creation, QNAP production deployment, and ChatGPT Workspace publication may remain human-controlled. Their absence must be reported as an explicit external/manual gate, not as a source verification failure and not as a completed production release.
