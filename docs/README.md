# Documentation Index

Current release target: **`v1.1.0 Local ChatGPT MCP`**.

The documentation set covers the canonical operating constitution, governed runtime, 11-agent ChatGPT Workspace Agent projection, bundled local MCP, security and decision rights, production preflight, release verification, and target-environment activation. Historical release and Phase 1 closure records remain preserved as historical snapshots.

## Current release documentation

- `release-1.1.0-local-chatgpt-mcp.md`: semantic release record and TDD/loop-engineering summary.
- `production-readiness.md`: current fail-closed readiness model.
- `architecture.md`: current ChatGPT-local `LOCAL_STDIO` topology.
- `security-governance.md`: authority, local identity binding, human-only separation, replay safety, and audit controls.
- `testing-evaluation.md`: release gates and evaluation strategy.
- `runbook.md`: build, certification, preflight, preview, and incident operations.
- `../RELEASE.md`: canonical release notes.
- `../CHANGELOG.md`: semantic release history.

## Canonical runtime

- `phase-1-operating-contract.md`: operating constitution.
- `../agents/registry.json`: canonical agent definitions and authority.
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
- `../chatgpt/skills/`: 11 validated role Skills.
- `../chatgpt/workspace-agents/`: exact Workspace Agent manifests aligned to release `1.1.0`.
- `../chatgpt/mcp/mesh-cos-mcp.v1.json`: MCP contract, per-agent allowlists, local runtime metadata, and human-only tools.
- `../chatgpt/mcp/README.md`: bundled MCP implementation and security boundary.
- `../chatgpt/workspace-agent-builder-prompt.md`: Workspace Agent deployment handoff.
- `../mcp/`: TypeScript local stdio MCP transport package.

The ChatGPT runtime path is `Workspace Agent -> LOCAL_STDIO -> node mcp/dist/index.js -> mesh_cos.mcp_stdio_bridge -> MCPRuntime -> TaskLedger`.

A separately deployed remote MCP service is optional and not required for ChatGPT-local operation.

## Architecture and governance

- `decision-rights.md`: L0-L5 authority.
- `explainable-decisions-audit.md`: governance schemas, provenance, mirrors, privacy, and integrity.
- `delegation-model.md`: bounded delegation and one-owner policy.
- `task-lifecycle.md`: completion, independent verification, and rework.
- `agent-registry.md`: workforce definitions and deployment projection rules.
- `agent-performance.md`: AgentOps performance management.
- `conflict-resolution.md`: functional authority and arbitration.
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

`release-1.0.0-production-readiness.md`, `production-hardening-2026-08-17.md`, the original Workspace Agent gap assessment, and Phase 1 closure/remediation documents remain historical. They are not rewritten to imply they were authored against `v1.1.0`.

Current documentation must describe the bundled local runtime. CI enforces contract validation, runtime/documentation drift, Workspace Agent package drift, TypeScript/Node MCP certification, strict source Ruff, mypy, 100% branch-aware Python coverage, Bandit high-severity scanning, and compileall.
