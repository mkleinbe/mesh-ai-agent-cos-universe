# ChatGPT Published App Production Acceptance v4.4.0

## Status rule

The Mesh CoS MCP v4.4.0 source contract is **not** equivalent to an accepted ChatGPT Workspace publication. Source-only validation must remain `SOURCE_CONTRACT_ONLY` until the actual Workspace action snapshot has been captured and attested.

## Required source state

- runtime contract: `4.0.0`
- deployment/release candidate: `4.4.0`
- canonical roster: exactly 10 active registered agents
- CoS machine action surface: exactly 28 actions
- full catalog: 30 actions, including two human-only operations
- human-only operations excluded from agent publication:
  - `approval.record_decision`
  - `reliability.human_override`
- `delegation.execute_owner` present with the v2 protocol/input schema

## Human Workspace publication step

The Workspace administrator performs the plan-appropriate publication operation using the same approved Secure MCP Tunnel endpoint and authentication configuration.

For ChatGPT Business, recreate/scan/publish the custom app when the workspace does not support in-place tool refresh.

For Enterprise/Edu, use Workspace Settings -> Apps -> Mesh CoS MCP -> Action control -> Refresh, review the diff, explicitly enable new or changed actions, and publish the updated app.

This repository does not treat either administrative action as complete until the actual action snapshot is available for verification.

## Snapshot format

Capture every published/draft action with its exact input schema in JSON form:

```json
{
  "tools": [
    {
      "name": "task.get",
      "inputSchema": {}
    }
  ]
}
```

The snapshot must contain all actions. A names-only snapshot is insufficient for v4.4.0 production acceptance.

## Attestation

Run:

`python scripts/check-published-action-surface.py --actual-file <snapshot.json>`

Acceptance requires all of the following:

1. exact equality to the expected 28 CoS machine action names;
2. no unexpected actions;
3. `delegation.execute_owner` present;
4. both human-only operations absent;
5. exact input-schema equality for every action;
6. published schema digest equals the `publication_schema_digest` reported by the bound v4.4.0 runtime principal.

Any missing action, unexpected action, or schema difference is a production acceptance failure.

## Post-publication live checks

After the human publication action:

1. Re-read the live Mesh CoS MCP action catalog from ChatGPT.
2. Require exactly 28 machine actions.
3. Verify `registry.list_agents` returns exactly 10 active agents with canonical parentage.
4. Verify the audit chain is valid.
5. Run a safe direct delegated-owner execution under a non-consequential operation.
6. Run nested synthetic routes:
   - `cos -> cmo -> vp-content`
   - `cos -> coo -> consultant-network-steward`
7. Prove the parent cannot complete child-owned work directly.
8. Prove the canonical owner can complete it.
9. Prove completion remains separate from verification.
10. For Message Operations, prove a consequential execution cannot proceed without canonical approved authority.

## Disposition

Until the human Workspace publication and exact snapshot attestation occur, record:

`workspace_publication_status=BLOCKED_PENDING_ACTUAL_ACTION_SCHEMA_SNAPSHOT`

Do not translate that status into a source-code failure, and do not represent the ChatGPT app as production-accepted.