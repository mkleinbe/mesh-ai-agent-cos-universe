# Release Authorization: v4.3.1

Date: 2026-08-28

## Scope

The standing Mesh engineering execution and release standard requires material engineering turns to be documented, verified, integrated to `main`, semantically versioned, tagged, and published as a GitHub Release when the repository change is releasable.

This authorization applies to **v4.3.1 Published MCP Action-Surface Closure**, the repository/release-control hardening associated with PF-058/PF-059.

## Authorized GitHub actions

- verify the exact release candidate;
- merge the release-control PR to `main` after green checks;
- create semantic tag `v4.3.1` at the final integrated `main` commit;
- publish GitHub Release `v4.3.1` using the reviewed v4.3.1 release/changelog documentation;
- close the release PR after merge.

## Explicit boundary

This GitHub release authorization does **not** represent or authorize a false production-acceptance claim.

The active QNAP deployment may remain 4.3.0 because it already implements the owner executor. The production ChatGPT app remains blocked until a workspace admin/owner refreshes or recreates and republishes the Mesh CoS MCP app action snapshot and the live connector is independently verified at exact 28/28 CoS machine actions, including `delegation.execute_owner` and excluding the two human-only operations.

No blocked Marketing occurrence may be recreated or advanced before that live workspace acceptance gate passes.
