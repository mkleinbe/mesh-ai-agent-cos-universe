# QNAP Release Identity Debugging Record v4.1.5

## Incident

The v4.1.4 QNAP upgrade built the new image successfully but stopped during host preflight before Compose replacement. The existing v4.1.3 containers remained healthy.

## Observed failure

The deployment log contained one causal preflight check failure:

```text
MESH_COS_DEPLOYMENT_RELEASE must be 4.1.3
```

All surrounding runtime ownership, canonical TaskLedger, tunnel image, tunnel ID, resource, image-identity, and Compose-render checks passed. The later `prepare failed` messages were propagation of this single preflight failure.

## Root cause

`deployment/qnap/scripts/mesh-cos-mcp-preflight.sh` retained a hardcoded `4.1.3` comparison after the QNAP deployment release advanced to v4.1.4. The v4.1.4 builder, image tag, generated `.env`, release workflow, and documentation had advanced, but preflight carried an independent stale patch-release constant.

The defect was therefore release/code drift, not a Docker, QNAP, TaskLedger, Secure MCP Tunnel, resource, or MCP transport failure.

## Why prior CI missed it

Existing QNAP tests validated the current release bundle, Compose environment, runtime controls, transport behavior, and documentation, but did not assert that preflight obtained its expected release identity from the bundle itself. The release number was duplicated across multiple implementation surfaces, so the stale preflight literal remained internally testable but operationally inconsistent.

## TDD evidence

A regression test was added before the implementation correction. It required preflight to:

- read `$APP_ROOT/release-metadata.txt`;
- derive the expected release from its `version=` record;
- reject the stale v4.1.3 literal gate.

The test failed against the v4.1.4 implementation for exactly those two reasons. After the causal change, the same test and the full repository CI passed.

## Causal correction

Preflight now treats release metadata shipped in the verified QNAP bundle as the release-identity authority. It compares the generated `MESH_COS_DEPLOYMENT_RELEASE` value to the bundle `version=` value and fails closed when the metadata is missing or the values differ.

This removes the duplicated patch-release constant from preflight and makes future QNAP patch releases self-consistent with their bundle metadata.

## Production safety outcome

The v4.1.4 failed run behaved safely:

- pre-deploy online SQLite backup completed;
- the v4.1.4 image build completed;
- the canonical TaskLedger remained valid;
- the existing tunnel secret was preserved;
- preflight stopped before Compose replacement;
- the running v4.1.3 application and tunnel remained healthy.

No rollback was required because replacement never began.

## Corrective release

The durable correction is released as v4.1.5. The canonical Mesh CoS authority/runtime contract remains 4.0.0 and the MCP transport correction introduced in v4.1.4 remains unchanged.
