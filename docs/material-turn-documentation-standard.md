# Material Turn Documentation Standard

## Purpose

Every material application turn must leave a durable, reviewable, release-bound record of what changed, why it changed, how authority and security boundaries moved or stayed fixed, how the change was verified, how it is released, and how it can be recovered or rolled back.

A material turn includes any change that affects externally visible behavior, agent authority, orchestration, security, persistence, MCP or connector contracts, runtime topology, deployment architecture, approval boundaries, production recovery, or a semantic release.

## Required documentation set

For every material turn, update or create all applicable records before integration:

1. `README.md` current-release and architecture pointers.
2. `RELEASE.md` current semantic release contract.
3. A versioned changelog, for example `CHANGELOG-vX.Y.Z.md`.
4. A versioned material-turn record in `docs/material-turn-vX.Y.Z.md`.
5. Architecture documentation covering before/after behavior and trust boundaries.
6. Delegation, registry, data, transport, or lifecycle documentation when those contracts change.
7. A versioned security review when security applicability is not `NOT_APPLICABLE`.
8. A versioned verification receipt bound to the exact candidate revision.
9. Production-readiness and operator runbook changes.
10. Deployment, upgrade, rollback, backup, and recovery instructions when runtime behavior changes.
11. Production acceptance instructions that distinguish candidate verification from live acceptance.
12. Updated BDD or equivalent executable behavior specifications for behavior-changing work.
13. Updated tests and CI gates sufficient to prevent regression or authority drift.
14. A skill/package manifest when ChatGPT Skills, workspace agents, MCP manifests, or package contracts change.
15. Release artifacts, checksums, semantic tag, release notes, and exact commit provenance.

Historical versioned records must remain immutable except to correct an explicit documentation defect without rewriting historical facts.

## Diagram requirement

Use Mermaid diagrams whenever a material turn changes architecture, sequence, authority flow, state flow, deployment flow, or recovery flow. Validate/render the Mermaid with the connected Mermaid Chart capability before integration.

At minimum, a material architecture turn should include:

- a flowchart or component diagram showing the new topology or control path;
- a sequence diagram when caller, server, owner, approval, verifier, or provider interactions materially change;
- a recovery or deployment flow when stateful cutover or rollback behavior changes.

The Mermaid source belongs in the durable Markdown record even when the rendered interactive diagram is produced externally.

## Required material-turn record structure

Each `docs/material-turn-vX.Y.Z.md` must include:

- Executive summary
- Trigger / defect / business reason
- Scope and non-scope
- Requirements and acceptance criteria
- Root cause, when defect-driven
- Before / after behavior
- Architecture and Mermaid diagrams
- Authority and trust-boundary analysis
- Data and persistence implications
- Security review summary
- Reliability, idempotency, and observability implications
- Compatibility and migration
- Production recovery
- Rollback
- Updated Skills / agents / manifests
- Test and verification evidence
- Exact candidate and merge commit identity
- Semantic version rationale
- Release artifacts and checksums
- Production acceptance boundary
- Residual risks / known constraints
- Decision log

## Release governance

A material turn is not complete merely because code exists or a PR is open. Completion requires:

1. exact-candidate verification;
2. applicable security receipt;
3. material documentation complete;
4. integration into the protected default branch under authorized release authority;
5. semantic tag bound to the integrated commit;
6. immutable release artifacts or release record;
7. release receipt with checksums/provenance when artifacts exist;
8. production acceptance and recovery explicitly separated from repository integration unless the same authorization covers production deployment.

## Authority preservation

Documentation must distinguish:

- orchestration identity from accountable owner;
- task completion from verification;
- agent authority from human-only authority;
- candidate verification from production acceptance;
- release publication from deployment;
- rollback of software from mutation of canonical business state.

No documentation may imply that a technical PASS creates business authority, approval authority, or production deployment authority that does not otherwise exist.

## Skill/package turns

When a material turn updates ChatGPT Skills or workspace-agent packages:

- list every affected Skill by canonical name;
- describe the contract change;
- state whether the Skill itself changed or only a workspace-agent package changed;
- preserve exact tool/authority allowlists;
- generate a versioned install/update bundle for human-controlled Skill directory updates when requested;
- include a manifest in the bundle identifying source repository, release, integrated commit, and included paths.

## Definition of documented

A material turn is `DOCUMENTED` only when a reviewer can reconstruct, from repository records alone:

- what changed;
- why it changed;
- what authority it has;
- how it was proven;
- what shipped;
- how to deploy it;
- how to recover it;
- how to roll it back;
- which Skills or agent packages were affected;
- and exactly which commit/tag/release represents the turn.
