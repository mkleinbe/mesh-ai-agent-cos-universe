# v1.0.0 Production Readiness

Release `v1.0.0` is the first semantic production-readiness release of the Mesh AI Chief of Staff operating core. It marks the repository, runtime contracts, governed Skills, Workspace Agent deployment packages, MCP control plane, release gates, and operating documentation as production-ready for activation when environment-specific dependencies pass preflight.

Production readiness is not the same as production activation. This release does not claim that a remote MCP endpoint, Workspace authentication, Slack credentials, Answer Desk channel, production approver mapping, source credentials, or deployment infrastructure have already been configured.

## Release flow

```mermaid
flowchart LR
    A[Canonical TaskLedger] --> B[Mesh CoS MCP Runtime]
    B --> C[Workspace Agents]
    C --> D[Governed Skills]
    B --> E[Authority and Approval Controls]
    B --> F[Audit and Metrics]
    D --> G[Production Preflight]
    E --> G
    F --> G
    G --> H[100% Branch Coverage CI]
    H --> I[Release Candidate]
    I --> J[v1.0.0 Semantic Tag]
    J --> K[GitHub Release]
```

## Governed execution path

```mermaid
sequenceDiagram
    participant U as User or Executive
    participant W as Workspace Agent
    participant M as mesh-cos-mcp
    participant R as Canonical Registry
    participant L as TaskLedger
    participant H as Human Approver
    U->>W: Delegate outcome
    W->>M: Governed tool call
    M->>R: Resolve identity and authority
    M->>L: Read canonical task and evidence
    alt L0-L3 within authority
        M->>L: Persist action and audit event
        L-->>W: Canonical result
    else L4 approval required
        M->>L: Persist approval request
        L-->>H: Approval required
        H->>M: Authenticated decision
        M->>L: Persist approval and action
    else L5 decision
        M->>L: Escalate to Michael-exclusive decision
    end
```

## Production readiness versus activation

```mermaid
flowchart TD
    A[Repository v1.0.0] --> B[100% Branch-Aware CI]
    B --> C[Production Preflight]
    C --> D{External Dependencies Configured?}
    D -->|No| E[Production-Ready Repository]
    D -->|Yes| F[Live Integration Smoke Tests]
    F --> G{All Negative and Positive Tests Pass?}
    G -->|No| H[Block Activation and Remediate]
    G -->|Yes| I[Production Activation]
    E --> J[Configure MCP URL, Workspace Auth, Slack, Answer Desk, Approvers, Source Credentials]
    J --> F
```

## v1.0.0 release invariants

- `mesh_cos` branch-aware coverage is release-gated at 100%.
- Contract validation, runtime/documentation drift, Workspace Agent package drift, strict source Ruff, mypy, dependency integrity, high-severity Bandit, and compileall are release gates.
- `mesh_cos.mcp_runtime.MCPRuntime` is the serialized execution boundary.
- Agent identity, role, implementation provenance, and authority are derived server-side from the canonical Agent Registry.
- Human-only approval and reliability-override operations require authenticated human principals.
- L4 fails closed without qualified human approval. L5 remains Michael-exclusive.
- Remote replay uses only server-registered replay executors named by canonical failure state. Client-supplied code or import paths are never executed.
- `task.complete` persists accountable-owner outcome evidence. `task.verify` remains separate acceptance verification.
- Slack and governance-event idempotency are atomic with canonical persistence.
- `TaskLedger` remains canonical. ChatGPT conversations, Slack, and governance Sheets remain non-canonical surfaces.
- Every one of the 11 Workspace Agent manifests declares repository release `1.0.0` and is checked against the MCP allowlist and canonical registry.

## Required production activation dependencies

Before live activation, configure and test the approved HTTPS `mesh-cos-mcp` endpoint, `MESH_COS_MCP_SERVER_URL`, Workspace authentication and app permissions, Slack bot/signing credentials where used, a dedicated Answer Desk Slack channel, production approval-owner mapping, approved source/Skill credentials, secrets management, runtime deployment ownership, and optional authenticated governance-Sheets mirroring.

Run `python scripts/production-preflight.py` before activation. Use `--require-slack`, `--require-answer-desk`, and `--require-ledger` when those surfaces are in scope.

## Release identity

- Repository release: `1.0.0`
- Git tag: `v1.0.0`
- Release title: `v1.0.0 Production Readiness`
- Release class: stable semantic production-readiness milestone
- Activation status: environment-dependent and fail-closed until preflight and live smoke tests pass

Historical Phase 1 closure and remediation records remain historical snapshots and are intentionally not rewritten to pretend they were authored against v1.0.0.
