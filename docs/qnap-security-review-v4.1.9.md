# QNAP Security Review v4.1.9

## Classification

Security applicability: **TARGETED**.

v4.1.9 is a release-integrity and documentation-closeout patch. It changes deployment/release identity, CI/release automation, packaged operator documentation, and version-bound acceptance evidence. It does **not** change the canonical Phase 1 authority/runtime contract, agent roster, tool allowlists, TaskLedger semantics, Secure MCP Tunnel architecture, or human approval model.

## Trust boundaries reviewed

1. GitHub CI/release automation to the generated QNAP bundle and semantic tag.
2. Release metadata and OCI image labels to QNAP image provenance checks.
3. QNAP Compose deployment identity to the running MCP response envelope.
4. OpenAI Secure MCP Tunnel ingress to the existing private `/mcp` source-IP gate.
5. Canonical SQLite TaskLedger persistence across upgrade and rollback.

## Security properties preserved

- Canonical runtime/authority contract remains `4.0.0`.
- Exactly 10 registered agents remain canonical.
- CoS agent-facing catalog remains exactly 27 governed tools.
- `approval.record_decision` and `reliability.human_override` remain human-principal-only.
- Mesh Devil's Advocate remains a governed shared Skill, not an agent principal.
- `COMPLETED != VERIFIED` remains enforced.
- Production ingress remains OpenAI Secure MCP Tunnel only.
- QNAP runtime remains non-root UID/GID 65532, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket.
- Release bundle excludes the tunnel runtime secret and canonical TaskLedger data.
- Image reuse remains bound to release metadata version and commit provenance.

## Required evidence

The exact candidate must pass the existing repository and QNAP release gates, including Python 100% branch-aware coverage, TypeScript MCP checks, npm audit, Bandit, contract/documentation drift checks, QNAP shell regressions, deterministic bundle/checksum generation, Compose rendering, OCI provenance, modern MCP discovery, sequential requests, non-root ownership, hardened runtime, direct-ingress denial, restart, and SQLite backup integrity.

## Findings

No new authentication, authorization, secret-handling, persistence, executable trust, or network boundary is introduced by v4.1.9. The primary risk is release/documentation drift. The release therefore fails closed if the generated bundle, deployment release identity, OCI labels, or packaged current-version documentation disagree.

## Residual boundary

Repository and container evidence cannot prove the newly deployed on-premises serving instance. Production acceptance remains pending until v4.1.9 is deployed to QNAP and the published Mesh CoS MCP app is retested through the Secure MCP Tunnel.