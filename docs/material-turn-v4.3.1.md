# Mesh CoS MCP v4.3.1 Material Turn

## Decision

Classify PF-058 as a published ChatGPT MCP action-snapshot defect, not a QNAP runtime implementation defect.

The v4.3.0 source contract and live backend already define `delegation.execute_owner` and preserve server-derived accountable-owner identity. The ChatGPT workspace connector exposes 27 CoS machine actions instead of the required 28 because the workspace-approved MCP app uses a frozen action snapshot that was not refreshed/recreated after the v4.3.0 tool addition.

## Root cause

- Canonical source catalog: 30 operations.
- Human-only operations: `approval.record_decision`, `reliability.human_override`.
- Expected CoS published machine surface: 28 operations.
- Observed ChatGPT connector surface on 2026-08-28: 27 operations.
- Missing operation: `delegation.execute_owner`.
- QNAP deployment release observed: 4.3.0.
- Bound agent: `cos`.
- Registry: 10 ACTIVE agents, valid parentage.
- Audit chain: valid.

OpenAI documents that workspace-approved MCP apps use a frozen snapshot of available tools and inputs. For Business workspaces, a published custom app must be recreated and republished to change tools or metadata; Enterprise/Edu can refresh actions through Action control. Source: https://help.openai.com/en/articles/12584461-developer-mode-apps-and-full-mcp-connectors-in-chatgpt-beta

## Required published action invariant

The published ChatGPT action surface for the bound `cos` connector MUST equal:

`agent_tool_allowlists.cos - human_tool_allowlist`

Exact expected count for this release: 28.

The invariant is set equality, not minimum-count equality. Missing tools fail closed. Unexpected tools also fail closed.

## Active-agent capability universe

The canonical 10-agent roster is:

1. `cos`
2. `agentops`
3. `answer-desk`
4. `cro`
5. `cfo`
6. `coo`
7. `consultant-network-steward`
8. `cmo`
9. `vp-content`
10. `message-ops`

Every ACTIVE downstream owner requires `task.get`, `task.transition`, `task.check_in`, and `task.complete` in its own allowlist.

Every canonical parent-child edge requires the parent to have `delegation.create` and `delegation.execute_owner` for owner execution transport. Parents with an ACTIVE registered nested child additionally require `task.decompose`.

Current nested routes remain intentionally bounded to:

- `cos -> cmo -> vp-content`
- `cos -> coo -> consultant-network-steward`

CRO and CFO have no ACTIVE registered child in the current roster, so nested executor authority is not added merely because their registry records allow future bounded specialist delegation.

## Security properties

1. Caller cannot supply the acting child principal.
2. `delegation.execute_owner` derives owner identity from canonical delegation and TaskLedger state.
3. Child allowlist is reapplied server-side.
4. Inherited approval gates remain in force.
5. Human-only actions remain absent from the agent-published action surface.
6. A frozen or drifted ChatGPT action snapshot fails preflight before canonical intake of child-owned work.
7. No prompt, task metadata, Sheet value, or caller argument may substitute for owner identity.

## Test and release controls

Added `scripts/check-published-action-surface.py`.

The script derives the expected published action set from the canonical MCP contract. With `--actual-file`, it compares a captured ChatGPT action snapshot using exact set equality. A snapshot missing `delegation.execute_owner` must fail.

Added integration regression coverage proving:

- the exact 28-action snapshot passes;
- the observed 27-action pattern with `delegation.execute_owner` missing fails.

The existing `check-owner-execution-readiness.py` remains responsible for registry/allowlist/parentage readiness. The new published-surface verifier covers the external ChatGPT approval snapshot that source-level and container-level tests cannot prove.

## Production remediation

Backend redeployment is not the first corrective action because v4.3.0 already serves the correct tool contract. The required action is to refresh the workspace-approved MCP app action snapshot.

For ChatGPT Business:

1. Workspace admin/owner recreates the custom Mesh CoS MCP app using the same approved Secure MCP Tunnel endpoint.
2. Run **Scan Tools**.
3. Verify the scanned CoS machine action set is exactly 28 and includes `delegation.execute_owner`.
4. Publish the recreated app for the workspace.
5. Rebind/update any Workspace Agent tool attachment if the recreated app receives a distinct app identity.
6. Re-read the connector catalog from ChatGPT and run the published-surface verifier.
7. Only after PASS, resume the exact outstanding execution keys. Do not create replacement logical occurrences.

For Enterprise/Edu, use Workspace settings -> Apps -> Action control -> Refresh, review the new action, explicitly enable it, and republish/update as required.

## Recovery targets

Preserve and resume in place:

- `MKT-LI-OPT-WED-001:2026-08-26T15:00:00-04:00`
- `MKT-LI-REV-FRI-001:2026-08-28T15:00:00-04:00`

No provider mutation occurred on either blocked run.

## Release status

Repository remediation can be merged and released as v4.3.1 only after CI and independent verification pass. Production acceptance remains blocked until the ChatGPT workspace app action snapshot exposes the exact 28-action CoS machine surface.
