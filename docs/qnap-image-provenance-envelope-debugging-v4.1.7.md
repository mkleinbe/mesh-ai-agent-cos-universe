# v4.1.7 QNAP Image Provenance and Hosted Envelope Debugging Record

## Observed production defect

The published `Mesh CoS MCP` ChatGPT app remained functionally healthy through the OpenAI Secure MCP Tunnel, but governed tool responses omitted the required top-level `deployment_release` field. A live `registry.get_agent` call on 2026-08-25 returned `ok`, `request_id`, `mcp_version: 4.0.0`, `agent_id: cos`, and `result`, with no `deployment_release`.

This violates QNAP-053 and blocks acceptance of the deployed v4.1.6 identity envelope.

## Bounded evidence

The final tagged v4.1.6 repository implementation is not missing the field:

- `mcp/src/server.ts` serializes `deployment_release` on successful and error tool envelopes.
- `deployment/qnap/compose.yaml` injects `MESH_COS_DEPLOYMENT_RELEASE` into `mesh-cos-mcp`.
- the exact v4.1.6 release workflow artifact contains those files plus `release-metadata.txt` with commit `e95e9f3afad6d282a30fedb27dc5a8add815bd14`.
- the exact v4.1.6 release ZIP SHA-256 is `003fc6363dc96aa642923fa9a38abffd155892bd36414b08c3f09a8d3218627f`.

Therefore the hosted response cannot have been produced by the exact final v4.1.6 release-built `server.ts` implementation.

## Deployment-path defect

The v4.1.6 preparation path trusted an existing local image solely because the mutable tag `mesh-cos-mcp:qnap-v4.1.6` existed. It did not compare the image OCI `org.opencontainers.image.version` and `org.opencontainers.image.revision` labels with the extracted release metadata before reuse.

That creates a concrete path for a prerelease, partial, or otherwise stale local image under the final tag to survive extraction of a newer verified bundle.

The v4.1.6 post-deploy verifier also checked `/healthz` and `/readyz` dual identity but did not execute a real governed `tools/call`. A runtime whose status endpoints were current while its tool-envelope implementation was stale could therefore pass local verification and still fail hosted acceptance.

## Falsifiable root-cause statement

Root cause is release-image provenance not being enforced at the QNAP reuse boundary, combined with an acceptance gap at the governed tool-envelope boundary, because:

1. the final release source and release artifact contain the required envelope field;
2. the live hosted envelope does not;
3. the deployment script allowed a pre-existing same-tag image to bypass rebuilding without proving that image came from the final release commit; and
4. post-deploy verification did not call the governed tool path that would expose the mismatch.

The exact historical origin of the stale live image cannot be proven without the corresponding QNAP deployment log/image-label evidence. v4.1.7 therefore fixes the demonstrated release-integrity mechanism and adds a runtime gate that directly tests the failed contract.

## v4.1.7 causal correction

v4.1.7:

- reads release version and commit from the extracted `release-metadata.txt` as data;
- requires a valid 40-character release commit and a release-version match before image preparation;
- compares any existing local Mesh image OCI version/revision labels with the extracted release metadata;
- rebuilds the image when either label differs;
- verifies the built/reused image labels before recording the image ID;
- retains explicit force-rebuild support;
- extends post-deploy verification with a read-only `registry.get_agent` modern MCP `tools/call` issued from an ephemeral verifier sharing only the tunnel client's network namespace;
- requires that returned tool envelope to contain `mcp_version: 4.0.0`, `deployment_release: 4.1.7`, and `agent_id: cos` before deployment is reported successful.

## Preserved invariants

- canonical Phase 1 authority/runtime contract remains `4.0.0`;
- exactly 10 registered agents and 27 governed CoS tools;
- human-only operations remain excluded;
- canonical TaskLedger is preserved;
- `COMPLETED != VERIFIED`;
- Secure MCP Tunnel remains the production transport;
- direct non-tunnel ingress remains denied;
- long-running runtime remains UID/GID 65532, read-only, capability-dropped, no-new-privileges, and without a Docker socket;
- no tunnel secret is exposed to the verification container.

## Acceptance

The defect is not closed merely because v4.1.7 CI is green. After QNAP deployment, the published app must return all three identity fields on sequential hosted tool calls without restart or reconnect.
