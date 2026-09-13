# v4.9.0 Security Review

Applicability: **TARGETED**

Sensitive surface: shared Skill entitlement and AI-native delegation/composition boundary. No new network, OAuth, credential, secret, persistence, or external-write surface is introduced.

Verified security properties:
- `mesh-opex-bot` remains a Skill, never an agent principal.
- Consumer scope is exactly `coo`.
- `canonical_facts_modified` is false.
- `external_action_included` is false.
- COO, CoS, CFO, AgentOps, and qualified-human authority remains explicit.
- Missing shared Skill availability degrades to a bounded handoff, never fabricated execution.
- Existing MCP allowlists and human-only operations remain unchanged.

Codex Security is not claimed unless separately evidenced. Repository tests, package drift checks, and independent verification provide the available bounded evidence for this change.
