# Architecture

## Purpose

Phase 1 is a governed executive control plane for a bounded hybrid organization of agents, reusable Mesh capabilities, authoritative data sources, and human decision owners. The architecture is intentionally a Python modular monolith with a narrow persistence boundary rather than a distributed agent swarm.

## Runtime topology

```mermaid
flowchart TB
    subgraph HumanAuthority[Human authority]
      CEO[Michael / CEO]
      APPROVER[Qualified L4 approvers]
    end

    subgraph ControlPlane[Executive control plane]
      COS[Chief of Staff Service]
      AO[AgentOps Evaluator]
      AD[Answer Desk Service]
      AUTH[Invocation Authorization]
    end

    subgraph FunctionalLayer[Functional agents and adapters]
      CRO[CRO]
      CFO[CFO v1]
      COO[COO v1]
      CNS[Consultant Network Steward]
      CMO[CMO]
      VPC[VP Content]
      DA[Devil's Advocate]
      MO[Message Operations]
    end

    subgraph CanonicalState[Canonical state]
      REG[agents/registry.json]
      CONTRACTS[Versioned JSON contracts]
      LEDGER[(SQLite TaskLedger)]
      PERF[performance-policy.v1.json]
    end

    subgraph Collaboration[Collaboration boundary]
      SC[Slack Coordinator / Web API boundary]
      OPS[#mesh-agent-ops\nC0BRL4GCL3A]
    end

    subgraph External[Approved external boundaries]
      SOURCES[Authoritative Mesh sources]
      SKILLS[Existing Mesh skills]
    end

    CEO --> COS
    APPROVER --> COS
    COS --> CRO
    COS --> CFO
    COS --> COO
    COO --> CNS
    COS --> CMO
    CMO --> VPC
    COS --> DA
    COS --> MO
    COS --> AO
    COS --> AD

    REG --> AUTH
    AUTH --> FunctionalLayer
    CONTRACTS --> ControlPlane
    ControlPlane --> LEDGER
    FunctionalLayer --> LEDGER
    PERF --> AO

    SOURCES --> AUTH
    SKILLS --> AUTH
    SC <--> COS
    SC --> LEDGER
    OPS <--> SC
```

## Canonical state

`TaskLedger` is the authoritative runtime persistence boundary. It stores tasks plus durable consequential records through typed record categories, audit events, idempotency claims, and Slack task/thread mappings. Slack messages and agent conversations are views of state, not state itself.

Canonical sources of operating truth:

1. `agents/registry.json` for agent identity, hierarchy, authority, source/tool policy, delegation permissions, prohibited actions, confidentiality, and runtime health.
2. `contracts/*.schema.json` for versioned data contracts.
3. `TaskLedger` for task lifecycle and consequential records.
4. `config/performance-policy.v1.json` for versioned AgentOps weighting and thresholds.

## Chief of Staff execution loop

```mermaid
sequenceDiagram
    participant R as Requester
    participant C as CoS Service
    participant L as TaskLedger
    participant F as Functional Agent/Adapter
    participant H as Human Approver

    R->>C: Outcome request
    C->>L: Persist INTAKE task
    C->>L: TRIAGED -> PLANNED -> ASSIGNED
    C->>F: Governed delegation / execution
    F->>L: Evidence, updates, consequential records
    alt approval required
        C->>H: Decision brief / approval request
        H-->>C: approve / reject
        C->>L: Persist approval disposition
    end
    F-->>C: Completed deliverable + evidence
    C->>L: COMPLETED
    C->>C: Execute acceptance test
    alt acceptance passes
        C->>L: Persist verification result
        C->>L: VERIFIED -> CLOSED
    else acceptance fails
        C->>L: Persist failed verification
        C->>L: REWORK
    end
```

## Delegation architecture

Delegation is contractual and bounded. A delegated work package cannot widen authority, drop parent approval obligations, create circular ownership, exceed the normal two-level depth below CoS, or define overlapping permitted and prohibited actions. Delegation records are durable.

## Slack architecture

`#mesh-agent-ops` is the private agent-operations coordination channel. The Slack boundary implements request-signature verification, durable event idempotency, task/thread mapping, structured message rendering, and a Web API client boundary. Live Slack calls remain configuration-dependent on the bot token and signing secret.

The separate Answer Desk channel is intentionally not inferred. Its channel ID must be supplied before team-facing Slack operation is activated.

## Security architecture

All source, tool, and action calls must pass runtime authorization from registry policy. Retrieved content is treated as untrusted data. L4 actions fail closed pending qualified human approval, and L5 authority remains Michael-exclusive. The kill switch and quarantine controls remain part of the Phase 1 safety model.

## Deployment boundary

The repository is implementation-ready for Phase 1 control-plane behavior, but production operation depends on credentials, source permissions, approval-owner mapping, and runtime infrastructure. SQLite is appropriate for Phase 1/local operation and should be revisited before multi-instance deployment.
