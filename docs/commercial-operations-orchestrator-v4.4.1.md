# Commercial Operations Orchestrator v4.4.1

## Decision

Repair the orchestration contract and TaskLedger control plane, not the QNAP runtime.

The production Mesh CoS MCP 4.4.0 deployment is healthy. The observed Commercial Operations failures came from caller-created work packages that stored descriptive prerequisite text in `TaskRecord.dependencies`. The runtime correctly interpreted each value as a canonical predecessor task identifier and correctly blocked `IN_PROGRESS` when those identifiers did not exist.

Changing the QNAP runtime would weaken a correct dependency gate and add unnecessary deployment risk. v4.4.1 therefore changes the orchestration contract, live scheduler configuration, durable TaskLedger guidance, regression coverage, and release documentation only.

## Root cause

Canonical task dependencies are hard work-graph edges. They are not a place to store source requirements, evidence labels, provider availability, Revenue Intelligence requirements, or other narrative prerequisites.

Correct rule:

- `TaskRecord.dependencies` and `task.decompose` dependency lists contain only real canonical predecessor task IDs.
- Narrative prerequisites belong in job contracts, acceptance tests, constraints, trigger conditions, evidence supplied, or the TaskLedger operating mirror.
- If no canonical predecessor exists, omit dependencies.
- A retry reuses the existing canonical work graph and deterministic IDs.

## Recovery model

A legacy malformed child is not rewritten into success. Preserve its terminal or isolated state and audit evidence. If the defect is deterministic and no provider side effect needs replay, create exactly one dependency-clean successor under the same CoS parent with the same accountable owner, authority, acceptance boundary, and inherited approval gates. Use normal owner execution, separate completion, and separate CoS verification.

This path was used successfully for the response-intake and banking-intelligence defects while the QNAP runtime remained unchanged.

## Operating ownership

- Chief of Staff: orchestration, work-graph integrity, scoped recovery, cross-job coordination, and separate verification.
- Revenue Intelligence: canonical account fit, lifecycle, priority, buying groups, activation readiness, commercial evidence, and buyer-response interpretation.
- CRO: commercial analysis and seller-support work assigned by the ledger.
- CMO: marketing and authority strategy that may contribute context to commercial outcomes.
- VP Content: bounded production and adaptation under CMO.
- GTM Orchestrator: governed activation.
- Messaging Governance and Message Operations: exact human approval and external-execution boundaries.
- LinkedIn Authority OS: authority, relationship, content, and performance context only. It cannot create account-level commercial truth.

## Business-first run contract

Every evaluated run reports:

1. Business outcome and material movement against the objective.
2. Evidence, confidence, and meaningful evidence gaps.
3. Action taken, recommendation, accountable owner, and any decision needed.
4. Material risks and unknowns.
5. Technical health separately as GREEN, DEGRADED, or FAILED, with scoped defects and recovery.

A business block or valid no-trigger result may coexist with technical GREEN. A blocked job does not downgrade unrelated jobs or the whole platform.

## Scheduling

The central Commercial Operations Orchestrator is active weekdays at 08:00, 10:00, 12:00, and 16:00 America/New_York. TaskLedger logical due times and trigger conditions remain authoritative. `COM-EMAIL-SEND-DLY-001` remains event-driven under `LOOP-COM-HITL-001` and is never converted to polling.

## Architecture

The validated Mermaid architecture for this release is `Mesh Commercial Operations Orchestration v4.4.1` and shows the TaskLedger-controlled CoS dispatcher, CRO and CMO/VP Content ownership, Revenue Intelligence truth boundary, governed messaging chain, dependency-clean recovery, business-first reporting, and unchanged QNAP 4.4.0 runtime.

## Production acceptance evidence

- `task-f6302605caa9` and dependency-clean CRO successor `task-c380cb27fabc` are VERIFIED for the Aug. 31 banking-intelligence occurrence.
- `task-bc85dfca0c54` and its dependency-clean response successor are VERIFIED with zero ACTIVE response sources and zero Gmail content reads.
- `task-b69cf093fd9e` is CMO-owned and verified after nested VP Content task `task-29c935b9ef98` completed and was separately verified.
- TaskLedger guide controls `COM-OUTCOME-001`, `COM-ROUTING-001`, `COM-SELFHEAL-001`, `COM-BRIEF-001`, `COM-SCHED-001`, and `COM-CANONICAL-DEPS-001` are durable.
- The Commercial Operations automation is active on the declared weekday schedule.

## QNAP disposition

No QNAP action is required for v4.4.1. The live Mesh CoS MCP 4.4.0 deployment remains production. If a future defect is proven to originate in the MCP runtime rather than caller work-package construction, QNAP changes remain operator-proxied through Michael and require a separate justified deployment plan.
