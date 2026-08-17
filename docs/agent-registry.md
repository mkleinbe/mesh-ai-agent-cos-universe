# Agent Registry

`agents/registry.json` is the canonical Phase 1 registry for operating identities. Agents are executive/functional identities. Skills are reusable capabilities and are not interchangeable with agents.

## AgentRecord contract

The machine-readable record follows `agent-record.v1` and includes:

- agent ID and display name
- role and description
- parent agent ID
- agent type: executive, controller, specialist, worker, reviewer, or operations
- status and version
- accountable domain
- authoritative and allowed sources
- skills and tools
- input and output contracts
- permitted and prohibited actions
- decision authority
- required approvals
- delegation permissions and maximum delegation depth
- normal SLA
- performance policy
- confidentiality class
- runtime health
- created/updated timestamps where persisted

## Phase 1 identities

| ID | Role | Parent | Core authority |
|---|---|---|---|
| `cos` | Chief of Staff | Michael | orchestration, decomposition, cross-functional tradeoffs, escalation, outcome verification |
| `agentops` | AgentOps Controller | `cos` | workforce health, performance, workload, defects, routing recommendations |
| `answer-desk` | Answer & Decision Desk | `cos` | permission-aware answers, routing, bounded recommendations |
| `cro` | Commercial executive | `cos` | pursuit and commercial interpretation within delegated authority |
| `cfo` | Engagement Finance / FP&A executive | `cos` | engagement economics and financial analysis within source scope |
| `coo` | Delivery/resource executive | `cos` | feasibility, capacity, staffing readiness |
| `consultant-network-steward` | specialist | `coo` | consultant fit, freshness, rate, availability confidence, contracting readiness |
| `cmo` | Marketing executive | `cos` | marketing strategy and execution accountability |
| `vp-content` | content executive/worker | `cmo` | editorial production execution |
| `devils-advocate` | independent reviewer | `cos` | challenge, premortem, evidence gaps, reversibility review |
| `message-ops` | communications operations | `cos` | controlled execution of approved communications |

## Health states

- `SHADOW`: new/changed agent, limited authority, reviewed output
- `ACTIVE`: normal production routing
- `WATCH`: degraded quality or elevated rework
- `RESTRICTED`: reduced workload or authority
- `QUARANTINED`: no new production work after severe defect, unauthorized action, provenance/security failure, or equivalent event
- `RETIRED`: no active routing

## Registry governance

CoS may reallocate workload among registered agents and may recommend new agents or revisions. Phase 1 does not permit CoS or any agent to autonomously create an agent, materially expand agent authority, or bypass required approval.

Registry changes that alter material authority, executive decision rights, or CoS authority require Michael approval and an audit event.

## Source authority

Registry metadata distinguishes `authoritative_sources` from merely `allowed_sources`. Access does not make a source canonical. An agent must preserve the source-of-truth boundaries in the operating contract.

## Skills

Existing Mesh skills should be composed rather than duplicated where practical. The registry may grant an agent access to a skill, but the skill does not become a separate executive decision owner unless explicitly represented as an agent record.
