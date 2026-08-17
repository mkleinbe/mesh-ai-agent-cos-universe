# Architecture

## Purpose

Phase 1 is a governed executive control plane for a bounded hybrid organization of agents, reusable Mesh skills, authoritative data sources, and explicit human decision owners. It is a Python modular monolith with SQLite behind a narrow persistence boundary. It deliberately avoids swarms, brokers, and unnecessary microservices.

## Runtime topology

```mermaid
flowchart TB
    CEO[Michael / L5] --> COS[ChiefOfStaffService]
    APPROVER[Qualified L4 approvers] --> COS
    COS --> WM[ChiefOfStaffWorkforceManager]
    COS --> AO[AgentOpsEvaluator]
    COS --> AD[AnswerDeskService]
    WM --> CRO[CRO]
    WM --> CFO[CFO v1]
    WM --> COO[COO v1]
    WM --> CMO[CMO]
    WM --> DA[Devil's Advocate]
    WM --> MO[Message Operations]
    COO --> CNS[Consultant Network Steward]
    CMO --> VPC[VP Content]

    REG[Agent Registry] --> AUTH[Invocation authorization]
    AUTH --> CRO
    AUTH --> CFO
    AUTH --> COO
    AUTH --> CMO
    AUTH --> DA
    AUTH --> MO

    COS --> LEDGER[(TaskLedger)]
    WM --> LEDGER
    AO --> LEDGER
    AD --> LEDGER

    OPS[#mesh-agent-ops\nC0BRL4GCL3A] <--> SLACK[Slack inbound/outbound boundary]
    SLACK <--> COS
    SLACK --> LEDGER
    ADS[Separate Answer Desk Slack] <--> AD
```

## Work-management loop

```mermaid
sequenceDiagram
    participant M as Michael / requester
    participant C as CoS
    participant W as Workforce manager
    participant F as Functional agent / skill
    participant L as TaskLedger
    participant H as Human approver

    M->>C: Outcome request
    C->>L: Persist INTAKE
    C->>W: Decompose work graph
    W->>L: Persist child tasks and delegation
    W->>F: Governed work package
    F->>L: Evidence / check-in / state
    W->>W: Monitor dependencies, SLA and stalls
    alt stalled or misdirected
        W->>L: Remediate or reassign with audit
    end
    alt L4/L5 required
        C->>H: Decision brief / approval
        H-->>C: Explicit decision
        C->>L: Persist approval
    end
    F-->>C: Completed output + evidence
    C->>C: Execute acceptance test
    alt accepted
        C->>L: VERIFIED -> CLOSED
    else rejected
        C->>L: REWORK
    end
```

## Canonical source-of-truth map

| Subject | Canonical authority |
|---|---|
| Agent definition and authority | `agents/registry.json`, normalized by `mesh_cos.registry` |
| Task/work graph and outcomes | `TaskLedger` |
| Decisions, conflicts, approvals | `TaskLedger` typed records and audit events |
| Performance | performance-event/scorecard records plus versioned performance policy |
| Slack state | TaskLedger task/thread and event-idempotency records, not Slack history |
| Financial calculations | CFO v1 within supported engagement-finance sources |
| Commercial/account evidence | Revenue Intelligence where available |
| Delivery/resource feasibility | COO v1 and approved resource sources |

## Structured contracts

Nine versioned JSON schemas define AgentRecord, TaskRecord, Delegation, AgentEvent, Decision, Conflict, Approval, PerformanceEvent, and PerformanceScorecard. Contracts reject undeclared fields. Runtime records are validated through `mesh_cos.contracts`, and CI runs a runtime/documentation drift check.

## Functional execution boundary

`GovernedAdapterRegistry` maps only registered skills/tools to the agent allowed to invoke them. It composes existing Mesh capabilities instead of reimplementing them. External executors remain configuration-dependent until credentials and connectivity are supplied.

## Slack boundary

The Slack layer verifies request signatures and timestamps, rejects stale replayed requests, deduplicates event IDs durably, parses structured messages, persists one-task/one-thread mappings, and posts approval notifications. `#mesh-agent-ops` remains an observable collaboration surface, never canonical state. The Answer Desk uses a separate configurable Slack boundary.

## Reliability and governance

The runtime includes idempotent intake, bounded retries, timeouts, execution leases, failure records, explicit replay, human override, task supersession, stalled-work remediation, invocation allowlists, prompt-injection boundaries, L4/L5 fail-closed approval, audit events, health restrictions, and the emergency kill switch.

## Deployment boundary

Phase 1 operating logic is complete at the repository boundary. Production use still requires Slack credentials, the Answer Desk channel ID, approved source/skill credentials, approval-owner configuration, and deployment infrastructure. SQLite should be revisited before multi-instance or high-availability deployment.
