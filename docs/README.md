# Documentation Index

Current release target: **`v3.0.0 Shared Mesh Message Operations`**.

The documentation set covers the canonical operating constitution, governed runtime, **9-agent** ChatGPT Workspace Agent projection, external shared Mesh Devil's Advocate and Mesh Message Operations capabilities, bundled local MCP, security and decision rights, production preflight, release verification, and target-environment activation. Historical release and Phase 1 closure records remain preserved as historical snapshots.

## Current release documentation

- `release-3.0.0-shared-message-operations.md`: semantic release record, breaking topology change, and TDD/loop-engineering summary.
- `production-readiness.md`: current fail-closed readiness model.
- `architecture.md`: current ChatGPT-local `LOCAL_STDIO` topology and shared capability boundaries.
- `agent-registry.md`: exact 9-agent runtime roster and shared capability entitlement model.
- `decision-rights.md`: L0-L5 authority plus advisory and approval-bound shared-capability semantics.
- `security-governance.md`: authority, local identity binding, human-only separation, replay safety, shared-Skill constraints, and audit controls.
- `testing-evaluation.md`: release gates and evaluation strategy.
- `runbook.md`: build, certification, preflight, preview, and incident operations.
- `../RELEASE.md`: canonical release notes.
- `../CHANGELOG.md`: semantic release history.

## Canonical runtime

- `phase-1-operating-contract.md`: operating constitution.
- `../agents/registry.json`: canonical 9-agent definitions, authority, and shared capability entitlements.
- `../contracts/`: machine contracts, including `decision.v2` and `agent-event.v2`.
- `../config/performance-policy.v1.json`: AgentOps policy.
- `../config/governance-policy.v1.json`: explainability and audit policy.
- `../config/governance-logs.v1.json`: non-secret Decision/Audit Sheet mirror configuration.
- `../src/mesh_cos/ledger.py`: canonical persistence boundary.
- `../src/mesh_cos/mcp_runtime.py`: serialized business/governance execution core.
- `../src/mesh_cos/mcp_stdio_bridge.py`: bounded local MCP bridge.
- `../src/mesh_cos/preflight.py`: production preflight.

## ChatGPT deployment

- `../chatgpt/README.md`: Workspace Agent package architecture.
- `../chatgpt/skills/`: 9 validated repository-local role Skills.
- `../chatgpt/workspace-agents/`: 9 exact Workspace Agent manifests aligned to release `3.0.0`.
- external `mesh-devils-advocate`: shared Mesh Devil's Advocate Skill attached only to Chief of Staff and CRO.
- external `mesh-message-operations`: shared approval-bound execution Skill attached only to Chief of Staff, CRO, and CMO. VP Content remains drafting/editorial-production only.
- `../chatgpt/mcp/mesh-cos-mcp.v1.json`: MCP contract, per-agent allowlists, local runtime metadata, governed shared-Skill invocation boundary, and human-only tools.
- `../chatgpt/mcp/README.md`: bundled MCP implementation and security boundary.
- `../chatgpt/workspace-agent-builder-prompt.md`: Workspace Agent deployment handoff.
- `../mcp/`: TypeScript local stdio MCP transport package.

The ChatGPT runtime path is `Workspace Agent -> LOCAL_STDIO -> node mcp/dist/index.js -> mesh_cos.mcp_stdio_bridge -> MCPRuntime -> TaskLedger`.

The shared challenge path is `Chief of Staff or CRO -> skills.invoke_governed -> Mesh Devil's Advocate shared Skill -> advisory challenge packet -> owning role or qualified human`.

The shared execution path is `Chief of Staff, CRO, or CMO -> skills.invoke_governed -> Mesh Message Operations shared Skill -> exact approved connector execution -> per-attempt receipt -> observed provider state`. Mesh Message Operations is not an agent principal, cannot infer or broaden approval, and cannot create strategy/copy, select recipients, set pricing, make commitments, or define publishing policy.

A separately deployed remote MCP service is optional and not required for ChatGPT-local operation.

## Architecture and governance

- `explainable-decisions-audit.md`: governance schemas, provenance, mirrors, privacy, and integrity.
- `delegation-model.md`: bounded delegation, one-owner policy, and explicit rule that shared Skills are not delegated agents.
- `task-lifecycle.md`: completion, independent verification, and rework.
- `agent-performance.md`: AgentOps performance management.
- `conflict-resolution.md`: functional authority, optional governed challenge, and arbitration.
- `escalation-policy.md`: escalation routing.
- `observability.md`: audit, explainability, and metrics model.

## Collaboration

- `slack-agent-protocol.md`: `#mesh-agent-ops` and Slack runtime controls.
- `answer-desk.md`: team-facing Answer Desk interface and dispositions.

## Governance registers

- **CoS Decision Log**: `1IJcwPuulqsNAa1lCW2MsmNgH6Vm5INPqTlcH4NR0xpw`.
- **CoS Audit Log**: `1T8vKx4gaUJdeG8kSc18MsBbXpY4EbDF3exZ0RGpvND0`.

They are operational mirrors. `TaskLedger` remains canonical.

## Historical records

`release-2.0.0-shared-devils-advocate.md`, `release-1.1.0-local-chatgpt-mcp.md`, `release-1.0.0-production-readiness.md`, `production-hardening-2026-08-17.md`, the original Workspace Agent gap assessment, and Phase 1 closure/remediation documents remain historical. They are not mechanically rewritten to imply they were authored against `v3.0.0`.

Current documentation must describe the 9-agent plus shared Mesh Devil's Advocate and Mesh Message Operations model and bundled local runtime. CI enforces contract validation, runtime/documentation drift, Workspace Agent package drift, TypeScript/Node MCP certification, strict source Ruff, mypy, 100% branch-aware Python coverage, Bandit high-severity scanning, and compileall.
