# Release Notes: v4.4.0 Authority Closure

## Summary

v4.4.0 hardens the Mesh CoS MCP authority model across human approvals, delegated owner execution, nested delegation, capability scope, logical Skill-agent provenance, runtime provenance, and ChatGPT publication acceptance.

This is a **MINOR** release because it materially expands enforceable runtime behavior and observability while preserving the Phase 1 runtime contract (`4.0.0`) and the existing 10-agent roster.

## Material changes

- Canonical TaskLedger approval validation for all L4/L5 authority paths.
- Michael-only canonical L5 approval actor requirement.
- Delegation-level capability intersection and nested-delegation scope enforcement.
- Versioned `mesh.cos.owner-execution.v2` protocol.
- Durable failure receipts for rejected delegated capability attempts.
- Explicit logical Skill-agent handoff provenance.
- 10-agent capability execution closure manifest.
- Exact ChatGPT action+input-schema publication attestation.
- Runtime source commit and publication-schema digest in MCP response envelopes.
- Release-neutral CI and v4.4.0 candidate artifact packaging.
- Historical v4.3.0 release workflow isolation from future PRs.

## Compatibility

- Runtime contract remains `4.0.0`.
- Existing agent IDs and canonical parentage remain unchanged.
- Human-only tools remain excluded from all agent surfaces.
- A bounded legacy fingerprint path preserves replay of exact pre-v4.4 successful owner-execution results when no approval references were part of the request.
- Callers of the public `delegation.execute_owner` surface must use the v2 input schema and protocol fields exposed through MCP discovery.

## Migration

No TaskLedger data migration is required.

Operational migration requires:

1. human deployment of the v4.4.0 QNAP artifact;
2. human refresh/recreation and publication of the ChatGPT custom app where required by the workspace plan;
3. exact action+schema attestation against the actual workspace snapshot;
4. post-deployment provenance and delegated-route acceptance tests.

## Known limitations / manual gates

- Git tag and GitHub Release creation may remain human-controlled.
- QNAP production deployment is not performed by repository CI.
- ChatGPT Workspace publication is not performed by repository CI.
- Until the actual Workspace snapshot is supplied, publication status remains blocked and must not be represented as PASS.

## Release artifacts

The final verified `main` SHA should produce:

- `mesh-cos-mcp-qnap-v4.4.0.zip`
- `mesh-cos-mcp-qnap-v4.4.0.zip.sha256`
- `mesh-cos-chatgpt-skills-v4.4.0.zip`
- `mesh-cos-chatgpt-skills-v4.4.0.zip.sha256`
- verification receipt binding the candidate SHA, capability closure, owner readiness, source publication schema digest, and manual workspace publication status.
