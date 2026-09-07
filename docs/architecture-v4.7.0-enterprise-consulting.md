# v4.7.0 Enterprise Consulting Skill Architecture

## Architecture intent

The ten-agent organization remains unchanged. Consulting-method capability is strengthened at existing Skill boundaries, while canonical facts, agent authority, approval, execution, and verification remain separate.

```mermaid
flowchart TD
    CEO[Michael / CEO L5] --> COS[Chief of Staff]

    COS -->|direct Skill| PPMD[Mesh PPMD Bot 1.1+]
    COS -->|direct advisory Skill| DA[Devil's Advocate 1.4+]

    COS --> CRO[CRO]
    COS --> CFO[CFO]
    COS --> COO[COO]
    COS --> CMO[CMO]
    COS --> AD[Answer & Decision Desk]

    CRO --> RI[Revenue Intelligence 1.4+]
    CRO --> F360[Firm 360 1.5+]
    CRO --> CDE[Competitive Displacement 1.14+]
    CRO --> GTM[GTM Orchestrator 2.3+]
    CRO --> BP[Buyer Psychology 3.1+]
    CRO --> DA

    CMO --> EC[Executive Communications / Messaging 1.2+]

    PPMD -->|method outputs| COS
    RI -->|canonical commercial and stakeholder evidence| CRO
    F360 -->|evidence-bound synthesis| CRO
    CDE -->|deterministic scored analysis plus synthesis| CRO
    GTM -->|meeting preparation and governed activation| CRO
    BP -->|observed decision-confidence interpretation| CRO
    EC -->|governed decision memo| CMO

    CFO -->|financial evidence contribution| COS
    COO -->|delivery/workshop evidence contribution| COS
    CMO -->|marketing/decision artifact contribution| COS
    AD -->|permission-scoped answer/routing| COS

    DS[Mesh Design System / Artifact Designer 0.4+] -->|critic QA only| COS
    DS -->|critic QA only| CMO

    COS --> VERIFY[Independent acceptance verification]
    VERIFY --> STATE[TaskLedger VERIFIED state]
```

## Control-plane rules

1. **Method is not truth.** PPMD owns consulting method, not functional source authority.
2. **Commercial truth remains canonical.** Revenue Intelligence owns designated account, buying-group, lifecycle, and stakeholder truth.
3. **Financial truth remains scoped.** CFO owns supported engagement-finance and management-FP&A analysis within approved sources.
4. **Delivery truth remains scoped.** COO owns delivery feasibility, capacity, resource-readiness, and operational constraints.
5. **Design authority remains separate.** Critic QA cannot replace Mesh Design System or Artifact Designer authority.
6. **Communication execution remains separate.** Decision memos and drafts cannot bypass Message Operations and human approval.
7. **Completion and verification remain separate.** Artifact completion cannot self-establish `VERIFIED`.
8. **No capability-to-authority transitivity.** A Skill's richer reasoning cannot expand the invoking agent's L0-L5 decision rights, tool allowlist, delegation depth, or source permissions.

## Runtime impact

No Phase 1 runtime-contract change is required. No new MCP tool, database migration, credential, connector, QNAP restart, or network authority is introduced. Production QNAP remains `4.4.0`; canonical Phase 1 authority/runtime contract remains `4.0.0`.
