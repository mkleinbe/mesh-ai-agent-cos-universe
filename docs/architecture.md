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
    WM --> CFO[CFO]
    WM --> COO[COO]
    WM --> CMO[CMO]
    WM --> DA[Devil's Advocate]
    WM --> MO[Message Operations]
    COO --> CNS[Consultant Network Steward]
    CMO --> VPC[VP Content]

    REG[Agent Registry + shared governance policy] --> AUTH[Invocation authorization]
    AUTH --> CRO
    AUTH --> CFO
    AUTH --> COO
    AUTH --> CMO
    AUTH --> DA
    AUTH --> MO

    COS --> GOV[GovernanceJournal]
    WM --> GOV
    AO --> GOV
    AD --> GOV
    AUTH --> GOV
    GOV --> DEC[decision.v2]
    GOV --> EVT[agent-event.v2]
    DEC --> LEDGER[(TaskLedger)]
    EVT --> LEDGER
    COS --> LEDGER
    WM --> LEDGER
    AO --> LEDGER
    AD --> LEDGER

    LEDGER --> DLOG[CoS Decision Log mirror]
    LEDGER --> ALOG[CoS Audit Log mirror]

    OPS[#mesh-agent-ops\nC0BRL4GCL3A] <--> SLACK[Slack inbound/outbound boundary]
    SLACK <--> COS
    SLACK --> LEDGER
    ADS[Separate Answer Desk Slack] <--> AD
```

## Stable role identity model

Organizational role identity and software version are separate concerns. `display_name` is a stable organizational identity. The registry `version` field carries the agent implementation version using `MAJOR.MINOR.PATCH`; repository releases carry the control-plane release version. Accountable domain, source authority, permitted/prohibited actions, approval rules, and delegation rules express scope. Runtime registry validation rejects display names that embed a version token.

Canonical Phase 1 organizational names are `CRO`, `CFO`, `COO`, `Consultant Network Steward`, `CMO`, and `VP Content`.

## Functional accountability boundaries

```mermaid
flowchart LR
    CRO[CRO\nCommercial strategy and pursuits] -->|requests economics| CFO[CFO\nEngagement Finance / FP&A]
    CRO -->|requests feasibility| COO[COO\nDelivery feasibility and capacity]
    COO --> CNS[Consultant Network Steward\nNetwork readiness]
    CMO[CMO\nMarketing strategy and demand] --> VPC[VP Content\nEditorial production]
    CRO --> COS[CoS\nCross-functional orchestration]
    CFO --> COS
    COO --> COS
    CMO --> COS
```

- **CRO:** opportunity qualification, pipeline health, pursuit prioritization, buyer dynamics, proposal commercial architecture, next-best commercial action, expansion, and commercial-risk framing. Revenue Intelligence remains authoritative for designated commercial/account facts.
- **CFO:** Engagement Finance / FP&A only, including engagement economics, pricing scenarios, cost-to-serve, contribution economics, margins, supported working-capital implications, forecast-versus-actual, margin leakage, assumption management, scenario comparison, and financial-risk recommendations. It is not enterprise accounting, treasury, tax, audit, or unrestricted financial authority.
- **COO:** delivery feasibility, delivery configuration, capacity, POD/resource composition, dependency readiness, partner capacity, delivery-risk sensing, operational constraints, and staffing recommendations. The CoS retains enterprise work-graph orchestration.
- **Consultant Network Steward:** consultant identification/matching, fit, freshness, validation timestamp, rate, availability, readiness-gap, refresh, and contracting-readiness evidence under COO authority.
- **CMO:** marketing strategy, audience/ICP strategy, category positioning, campaign/demand architecture, distribution, brand governance, campaign optimization, editorial priorities, and marketing-commercial feedback.
- **VP Content:** editorial planning/calendar, source/evidence assembly, drafting, channel adaptation, derivatives, repurposing, Mesh IP reuse, content inventory, editorial QA, and performance feedback under CMO authority.

## Work-management loop

```mermaid
sequenceDiagram
    participant M as Michael / requester
    participant C as CoS
    participant W as Workforce manager
    participant F as Functional agent / skill
    participant G as GovernanceJournal
    participant L as TaskLedger
    participant H as Human approver

    M->>C: Outcome request
    C->>L: Persist INTAKE
    C->>W: Decompose work graph
    W->>L: Persist child tasks and delegation
    W->>F: Governed work package
    F->>G: Audit consequential skill/tool action
    G->>L: Persist agent-event.v2
    F->>L: Evidence / check-in / state
    W->>W: Monitor dependencies, SLA and stalls
    alt material recommendation or decision
        W->>G: Persist decision.v2 basis/evidence/criteria/risk
    end
    alt stalled or misdirected
        W->>L: Remediate or reassign with audit
    end
    alt L4/L5 required
        C->>H: Decision brief / approval
        H-->>C: Explicit decision
        C->>G: Persist approval-linked decision.v2
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
| Agent definition and authority | `agents/registry.json`, normalized by `mesh_cos.registry` plus `config/governance-policy.v1.json` |
| Task/work graph and outcomes | `TaskLedger` |
| Explainable decisions | `TaskLedger` `decision_v2` records; CoS Decision Log is a mirror |
| Auditable consequential events | `TaskLedger` `audit_event_v2` records; CoS Audit Log is a mirror |
| Conflicts and approvals | `TaskLedger` typed records linked to decision/audit records |
| Performance | performance-event/scorecard records plus versioned performance policy |
| Slack state | TaskLedger task/thread and event-idempotency records, not Slack history |
| Financial calculations | CFO within supported Engagement Finance / FP&A sources |
| Commercial/account evidence | Revenue Intelligence where available |
| Delivery/resource feasibility | COO and approved resource sources |
| Consultant readiness | Consultant Network Steward under COO using approved network data |
| Marketing strategy | CMO within approved brand/marketing sources |
| Editorial production | VP Content under CMO intent and approved Mesh IP |

## Structured contracts

The repository retains the original v1 contract set for compatibility and adds richer `mesh.cos.decision.v2` and `mesh.cos.agent-event.v2` governance contracts. Contracts reject undeclared fields. Runtime records are validated through `mesh_cos.contracts`, and CI runs a runtime/documentation drift check.

`decision.v2` captures explainable basis, evidence, alternatives, criteria, confidence, risk, authority, approval, reversibility, provenance, lineage, and outcome validation. `agent-event.v2` captures fully auditable actor/action/result/provenance metadata plus a tamper-evident SHA-256 hash chain.

## Cross-agent governance policy

`config/governance-policy.v1.json` applies at registry load to every registered agent. It adds the shared `governance-journal` tool and v2 governance output contracts without changing functional authority. Audit logging is required for consequential actions. Decision logging is required when an agent decides or recommends.

`TaskLedger.record_event()` bridges existing v1 `AuditEvent` producers into the v2 governance stream during migration. `GovernedAdapterRegistry` can emit v2 events directly for skill/tool invocations.

## Google Sheets mirror boundary

`config/governance-logs.v1.json` identifies the two non-secret human-readable operational mirrors:

- CoS Decision Log: `1IJcwPuulqsNAa1lCW2MsmNgH6Vm5INPqTlcH4NR0xpw`
- CoS Audit Log: `1T8vKx4gaUJdeG8kSc18MsBbXpY4EbDF3exZ0RGpvND0`

Writes are canonical-first. Mirror failures are persisted, not silently ignored. Sheets do not become decision authority or system of record.

## Functional execution boundary

`GovernedAdapterRegistry` maps only registered skills/tools to the agent allowed to invoke them. It composes existing Mesh capabilities instead of reimplementing them. External executors remain configuration-dependent until credentials and connectivity are supplied. Adding a permitted action does not fabricate a new external skill: native typed tools and existing approved Mesh skills remain distinct implementation mechanisms.

## Slack boundary

The Slack layer verifies request signatures and timestamps, rejects stale replayed requests, deduplicates event IDs durably, parses structured messages, persists one-task/one-thread mappings, and posts approval notifications. `#mesh-agent-ops` remains an observable collaboration surface, never canonical state. The Answer Desk uses a separate configurable Slack boundary.

## Reliability and governance

The runtime includes idempotent intake, bounded retries, timeouts, execution leases, failure records, explicit replay, human override, task supersession, stalled-work remediation, invocation allowlists, prompt-injection boundaries, L4/L5 fail-closed approval, explainable decisions, tamper-evident audit events, health restrictions, and the emergency kill switch.

Private chain-of-thought, hidden reasoning traces, credentials, tokens, and unnecessary personal data are prohibited from governance records. Evidence should be referenced rather than copied when a protected pointer is sufficient.

## Deployment boundary

Phase 1 operating logic is complete at the repository boundary. Production use still requires Slack credentials, the Answer Desk channel ID, approved source/skill credentials, approval-owner configuration, deployment infrastructure, and a runtime adapter with authenticated Google Sheets write capability if automatic mirroring is enabled. SQLite should be revisited before multi-instance or high-availability deployment.
