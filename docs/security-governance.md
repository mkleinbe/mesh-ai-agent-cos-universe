# Security and Governance

Phase 1 security is designed around explicit trust boundaries, least privilege, fail-closed approvals, durable auditability, and the principle that agent capability does not equal agent authority. ChatGPT Workspace Agents add another execution surface, so their product configuration is treated as defense in depth around the existing Mesh runtime rather than as the source of authorization truth.

## Trust architecture

```mermaid
flowchart TB
    IN[External input / source content] --> UNTRUST[Treat as untrusted data]
    UNTRUST --> WA[Workspace Agent / Slack / API trigger]
    WA --> APPS[Role-scoped Workspace apps]
    WA --> MCP[mesh-cos-mcp]
    MCP --> MP[WorkspaceAgentMCPPolicy\ndeny-by-default]
    MP --> AUTH[Registry source/tool/action authorization]
    AUTH -->|denied| BLOCK[Reject + audit]
    AUTH -->|allowed| LEVEL{Decision consequence}
    LEVEL -->|L0-L2| EXEC[Bounded execution]
    LEVEL -->|L3 delegated| EXEC
    LEVEL -->|L3 not delegated| OWNER[Named decision owner]
    LEVEL -->|L4| HUMAN[Qualified human approval]
    LEVEL -->|L5| CEO[Michael]
    EXEC --> GOV[GovernanceJournal]
    OWNER --> GOV
    HUMAN --> GOV
    CEO --> GOV
    GOV --> LEDGER[(TaskLedger canonical state)]
    LEDGER --> SHEETS[Decision/Audit Sheet mirrors]
```

## Core controls

### Least privilege

Every agent has explicit source, tool, skill, action, and authority boundaries in the canonical registry. Workspace Agent manifests add per-agent app access, MCP allowlists, channel settings, write approval, and Connector Action Constraints. These may narrow access but cannot widen the canonical registry.

### Workspace Agent MCP boundary

`chatgpt/mcp/mesh-cos-mcp.v1.json` defines the approved remote MCP surface. `mesh_cos.mcp_policy.WorkspaceAgentMCPPolicy` enforces the per-agent allowlist server-side with **deny-by-default** behavior. Unknown agents, unknown tools, and unlisted tools are rejected. The policy also validates that declared runtime bindings resolve to repository code and that consequential writes are auditable.

The execution sequence is: authenticate identity, resolve canonical `agent_id`, enforce MCP allowlist, enforce registry source/tool/action permissions, enforce L0-L5 authority and approvals, execute the existing runtime binding, persist canonical state, then emit required governance records. A builder-side tool toggle is never sufficient on its own.

### Prompt-injection boundary

Documents, Slack messages, app payloads, MCP arguments, source payloads, and retrieved content are data. They cannot change system policy, agent authority, approval obligations, or operating instructions. Retrieved-content instructions that attempt to alter role, tool access, approvals, or governance must be ignored and treated as source content.

### Human consequence boundaries

L4 actions require qualified human approval. L5 authority is Michael-exclusive unless the constitution is explicitly changed. No agent may infer approval from prior behavior, urgency, or conversational language. Approval-required decisions must carry an approval reference and named approver in the explainable decision record.

ChatGPT Workspace Agent write actions default to **Always ask**. This is an additional control and cannot replace Mesh approval requirements. A Workspace click cannot authorize a registry-prohibited action or satisfy L5 unless Michael is the authorized decision owner.

### Connector Action Constraints

Phase 1 manifests constrain risky app surfaces:

- CoS and AgentOps Slack writes are limited to internal `#mesh-agent-ops` coordination.
- Answer Desk Slack stays disabled until a dedicated channel ID exists.
- CRO Apollo access is research/enrichment only; Gmail and LinkedIn are non-outbound.
- CMO and VP Content have no autonomous public posting; AuthoredUp is analytics/draft preparation only.
- CFO, COO, and Consultant Network Steward evidence access is read-only.
- Message Operations may execute approved Gmail/Slack communications only when the canonical approval record matches the exact artifact, target, and scope, and Workspace **Always ask** still applies.

### Explainability boundary

Explainability means recording concise, reviewable facts about a decision: decision basis, evidence references, authoritative sources, alternatives, selection criteria, confidence, risk, authority, approval, reversibility, reversal conditions, and outcome validation. It does not mean storing private chain-of-thought, hidden reasoning traces, raw sensitive prompts, or unnecessary personal data.

### Audit integrity

`mesh.cos.agent-event.v2` records actor, action, authority, source/tool, task/correlation/decision IDs, summaries, result, evidence, approval, model/skill provenance, risk/classification, and retention metadata. Audit events form a SHA-256 hash chain. The chain is tamper-evident, not tamper-proof, and `verify_audit_chain()` detects mutation or discontinuity.

Workspace Agent actions should identify the canonical agent, Workspace-triggered run/correlation context, model version when available, role Skill/implementation version, MCP capability/tool, approval evidence, and canonical record reference. `agent_role` remains the stable organizational name; implementation provenance belongs in version fields.

### Canonical-first mirroring

`TaskLedger` is canonical. ChatGPT conversations, Slack, the CoS Decision Log, and the CoS Audit Log are interaction or review surfaces. Canonical writes occur first. A Sheet or conversation delivery failure cannot roll back canonical governance state and must be recorded as a durable failure where consequential.

### Delegation safety

Delegation cannot widen authority, remove approval gates, create circular delegation, or create conflicting permitted/prohibited actions. Workspace Agents may only invoke delegation tools exposed in their checked-in MCP allowlist, and the runtime delegation engine remains authoritative.

### Secrets and sensitive data

MCP deployment URLs, Slack bot tokens, signing secrets, OAuth tokens, app credentials, API keys, service-account secrets, and personal identifiers must not be committed or copied into governance records. `MESH_COS_MCP_SERVER_URL` is a non-secret configuration pointer only if the deployed URL itself is not sensitive; authentication credentials stay outside source control.

### Quarantine and kill switch

Critical defects can trigger `QUARANTINE` recommendations and routing restriction. `MESH_COS_KILL_SWITCH` remains available during rollout and incident handling. Workspace Agent publication should be restricted or disabled when the underlying runtime is quarantined or the kill switch is active.

## Cross-agent governance policy

`config/governance-policy.v1.json` applies to every registered agent at runtime. Audit logging is required for consequential agent/Skill actions. `decision.v2` logging is required when an agent decides or makes a material recommendation. The shared policy adds `governance-journal` without expanding functional authority.

## Source authority versus access

Permission to query a Workspace app or source does not make the agent authoritative for all facts in that source, nor does it permit disclosure to every requester. Source authority, source access, requester access, app authentication, and decision authority are separate governance dimensions.

## Incident response principles

1. Stop or restrict unsafe Workspace Agent/MCP execution and enable the kill switch if needed.
2. Preserve canonical records, hash-chain evidence, decision lineage, approvals, MCP tool identity, and app activity references.
3. Identify affected tasks, actions, agents, Skills, tools, decisions, approvals, app calls, and source calls.
4. Reconcile human-readable mirrors to `canonical_record_ref` rather than editing canonical history.
5. Quarantine or unpublish the affected agent/adapter when warranted.
6. Correct the control or contract through tests first.
7. Re-run contract validation, `check-runtime-doc-drift.py`, `check-chatgpt-packages.py`, pytest, lint, security scan, and targeted preview tests before restoring routing.
8. Escalate material security/privacy/legal consequence to the appropriate human owner.

See `explainable-decisions-audit.md` for the detailed governance contracts and `../chatgpt/mcp/README.md` for the Workspace Agent MCP enforcement sequence.
