# v4.8.3 Historical Publisher Retirement Gap Audit

## Verification-discovered defect

Post-release verification of v4.8.2 found that historical v4.4.1 and v4.4.2 workflows reacted to the new `main` commit. Their immutable-release guards prevented retargeting, but the workflows still retained publication authority. A repository-wide audit found the same stale publisher capability in v4.1.15, v4.2.3, v4.3.0, v4.3.1, v4.6.0, and the newly published v4.8.2 workflow.

## Remediation

| Gap | v4.8.3 action | Disposition |
|---|---|---|
| Historical workflow retains `gh release create` | remove executable publisher from all identified published workflows, including v4.6.0 | REMEDIATED |
| Historical workflow retains write token | reduce historical permissions to `contents: read` | REMEDIATED |
| Historical workflow can react to future main | make historical SemVer workflows `workflow_dispatch` only | REMEDIATED |
| Rule protected only release-by-release | add systemic regression across all published v4.x workflows through v4.8.2 | REMEDIATED |
| Current publisher ownership ambiguous after v4.8.2 | v4.8.3 is sole current publisher | REMEDIATED |
| v4.8.3 source/release record omitted v4.6.0 from the explicit inventory | correct current-source record in v4.8.4 without mutating the historical v4.8.3 tag | REMEDIATED BY v4.8.4 |

## Non-change audit

No v4.8.3 diff was justified in:

- `src/` runtime code;
- agent registry or parentage;
- ChatGPT Skill packages;
- MCP catalog, authentication, or transport;
- QNAP runtime/deployment;
- shared PPMD Bot or Messaging repositories;
- source authority, decision rights, or external-action approvals.

## Remaining blocker

The only known v4.8.x requirement blocker remains `BLOCKED_SOURCE_IDENTIFICATION` for the unresolved fourth donor source. This prevents four-source completeness claims but does not represent an unremediated implementation defect in the evidenced three-source scope.

## Completion standard

After v4.8.4 exact-head and post-merge verification, the intended final state is:

- zero known implementation or release-record defects in the bounded v4.8.x remediation scope;
- one explicit source-completeness blocker, `BLOCKED_SOURCE_IDENTIFICATION`.
