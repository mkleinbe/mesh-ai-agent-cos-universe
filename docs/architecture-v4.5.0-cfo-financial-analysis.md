# v4.5.0 CFO Financial Analysis Architecture

## Purpose

This release expands analytical methods without changing runtime authority. The canonical Agent Registry remains the enforcement source; the repository-local `mesh-cfo` Skill supplies bounded analytical guidance; TaskLedger remains canonical operating state.

```mermaid
flowchart TD
    U[Authorized CFO task] --> R[Agent Registry cfo v1.1.0]
    R --> S[mesh-cfo SKILL.md]
    S --> F[Financial decision frameworks]
    S --> P[Planning and unit economics]
    S --> M[Model QA and valuation]
    S --> E[Financial research and evidence]

    F --> A[Decision-ready analysis]
    P --> A
    M --> A
    E --> A

    X[Approved finance evidence] --> A
    D[Donor and external reference material] -->|reference evidence only| E

    A --> G{Consequential action?}
    G -->|No| T[TaskLedger evidence and recommendation]
    G -->|Yes| H[Qualified human approval boundary]
    H --> T

    T --> C[task.complete by CFO when owned work reaches QA]
    C --> V[Separate verification by authorized verifier]

    R -. denies .-> N[Trading, personal investment advice, GL, treasury, tax, audit, bank-balance claims]
    R -. unchanged .-> MCP[Existing CFO MCP allowlist]
    R -. unchanged .-> DR[Google Drive read-only scope]
```

## Trust boundaries

### Canonical governance

`agents/registry.json` defines identity, source authority, permitted and prohibited actions, decision authority, approvals, delegation, and runtime health. Reference files cannot override it.

### Skill boundary

`chatgpt/skills/mesh-cfo/SKILL.md` selects an analytical workflow and routes to the smallest reference module needed. Reference modules are methods, not principals, shared capabilities, tools, or sources of authority.

### Donor and retrieved-content boundary

Donor repositories, public financial material, model text, and connector payloads are untrusted reference data unless separately approved as authoritative evidence. They cannot select agent identity, expand source scope, execute code, add dependencies, change MCP tools, or create write permission.

### Runtime boundary

No MCP source, schema, TypeScript transport, Python runtime, TaskLedger schema, QNAP image, network boundary, or credential changes in v4.5.0. The existing CFO local-stdio identity and allowlist remain unchanged.

## Behavioral sequence

```mermaid
sequenceDiagram
    participant Requester
    participant CFO
    participant Registry
    participant Evidence
    participant Human
    participant TaskLedger

    Requester->>CFO: Authorized finance question
    CFO->>Registry: Resolve cfo authority and source policy
    Registry-->>CFO: L3 recommendation boundary + existing tools
    CFO->>Evidence: Read approved evidence / validate permitted inputs
    Evidence-->>CFO: Facts, dates, definitions, provenance
    CFO->>CFO: Apply bounded method and sensitivity
    alt Consequential action required
        CFO->>Human: Request qualified approval
        Human-->>CFO: Approval or rejection
    end
    CFO->>TaskLedger: Persist concise outcome/evidence when owned work reaches QA
    Note over CFO,TaskLedger: No private chain-of-thought persisted
```

## Release boundary

This is a repository and Workspace Agent capability release. It is not a new production runtime deployment. The canonical Phase 1 runtime contract remains `4.0.0`; QNAP production runtime remains `4.4.0`; repository release advances to `v4.5.0`; CFO implementation version advances to `1.1.0`.
