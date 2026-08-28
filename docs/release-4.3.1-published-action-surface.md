# Release v4.3.1: Published MCP Action-Surface Closure

## Release purpose

v4.3.1 hardens the release and production-acceptance process around the ChatGPT workspace-approved MCP action snapshot. It does not introduce new delegated authority or require a QNAP runtime code change beyond the already-deployed v4.3.0 owner-execution implementation.

## Material change

The release adds an independent external-publication invariant:

> Published CoS machine actions == canonical `agent_tool_allowlists.cos` - `human_tool_allowlist`.

For the current canonical contract this is exactly 28 machine actions. `delegation.execute_owner` is required. The two human-only tools remain excluded.

## Evidence

- Canonical MCP catalog: 30 tools.
- Human-only tools: 2.
- Expected CoS machine surface: 28.
- Observed pre-remediation workspace snapshot: 27.
- Missing action: `delegation.execute_owner`.
- Production QNAP release 4.3.0 already advertises and implements `delegation.execute_owner` in source/runtime contract.
- 10 ACTIVE canonical agents and parentage verified.
- Audit chain verified.
- Repository regressions cover exact-pass and missing-owner-executor fail cases.
- Existing owner-execution readiness remains the registry/allowlist/parentage gate.

## Release boundary

GitHub release publication does not update the already-approved ChatGPT workspace app action snapshot. The release is therefore **repository-integrated but production acceptance remains blocked** until the workspace app is refreshed/recreated and republished and the live connector is re-read at exact 28/28.

## Business workspace remediation

For a ChatGPT Business workspace, recreate and republish the custom Mesh CoS MCP app using the existing approved Secure MCP Tunnel endpoint, run Scan Tools, and confirm the exact 28-action CoS machine surface including `delegation.execute_owner` before publication.

For Enterprise/Edu, use Action control Refresh, review and enable the new action, and publish/update the app as required.

## Acceptance after workspace publication

1. Live connector exposes exactly 28 CoS machine actions.
2. `delegation.execute_owner` is present.
3. Human-only actions remain absent.
4. Registry remains exactly 10 ACTIVE agents with canonical parentage.
5. Audit chain remains valid.
6. Direct CMO-owned synthetic/internal execution succeeds through server-derived CMO identity.
7. Nested CMO -> VP Content execution succeeds.
8. Nested COO -> Consultant Network Steward execution succeeds.
9. Parent direct completion of child-owned work remains denied.
10. Owner completion and separate verification both succeed.
11. Outstanding Marketing execution keys are resumed in place.

## Rollback

No QNAP runtime rollback is required for the publication-snapshot defect. If the refreshed/recreated workspace app exposes an unexpected action set, do not activate it for governed work. Keep child-owner execution fail-closed, preserve the prior approved app, and correct the scanned/published tool set before recovery.
