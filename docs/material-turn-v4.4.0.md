# Material Turn v4.4.0: Authority Closure

## Decision

Advance the Mesh CoS MCP release candidate to v4.4.0 to close material authority, delegation, provenance, publication-attestation, and release-engineering defects found after v4.3.x production acceptance work.

## Problem statement

The prior implementation had several unsafe or ambiguous boundaries:

- L4/L5 governance paths could rely too heavily on caller-supplied approval metadata.
- A delegated owner could inherit more of its role capability universe than the specific delegation intended.
- Nested delegation and delegated reads required tighter task-local containment.
- Rejected delegated capabilities could fail before a durable owner-execution receipt existed.
- Skill handoffs could be misread as evidence that a separate synchronous Workspace Agent process had executed.
- Source action checks could not prove the frozen ChatGPT Workspace action/input-schema snapshot.
- Runtime contract, deployment release, source revision, and publication surface were not independently observable enough.
- Historical release workflows could be triggered by unrelated future pull requests.

## Implemented contract

v4.4.0 establishes:

1. canonical TaskLedger approval resolution for L4/L5;
2. Michael-only canonical L5 approval actor;
3. server-derived execution principals;
4. delegation-level `permitted_capabilities` intersection;
5. bounded nested owner execution;
6. task-local read and write restrictions;
7. `mesh.cos.owner-execution.v2`;
8. durable success and denial receipts;
9. explicit logical Skill-agent handoff provenance;
10. a 10-agent capability-execution closure manifest;
11. exact action+input-schema Workspace publication attestation;
12. source commit and publication schema digest in MCP response provenance;
13. release-neutral CI and v4.4.0 immutable candidate artifacts.

## Security classification

FULL_REVIEW. Authorization, agent identity, human approvals, MCP, persistent state, external consequential writes, CI/release provenance, and Workspace publication boundaries are all in scope.

## Compatibility

The Phase 1 runtime contract remains `4.0.0`, the canonical 10-agent roster remains intact, and human-only operations remain excluded from agent publication. The release advances to v4.4.0 because enforceable behavior and operator provenance materially expand without intentionally breaking the overall Phase 1 contract.

## Evidence required before merge

- exact-tree CI green;
- 100% branch-aware Python coverage;
- TypeScript build/test/smoke and npm security audit green;
- contract, drift, owner-readiness, capability-closure, and source publication checks green;
- Bandit and static typing green;
- QNAP POSIX regression suite green;
- v4.4.0 QNAP and Skill artifacts generated with checksums and exact source SHA;
- production-equivalent container built and modern MCP transport verified;
- independent verification receipt on the final candidate.

## Human-controlled post-merge gates

- semantic tag/GitHub Release if handled manually;
- QNAP production deployment;
- ChatGPT Workspace app refresh/recreation and publication;
- exact live action+input-schema snapshot attestation and post-publication synthetic acceptance.

These gates must remain explicit. Their absence does not invalidate verified source, but production/Workspace readiness must not be claimed until they are completed.