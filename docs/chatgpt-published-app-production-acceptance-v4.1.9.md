# ChatGPT Published App Production Acceptance v4.1.9

Use this acceptance contract only after the v4.1.9 QNAP deployment path passes local deployment, verification, and post-deploy backup.

The published **Mesh CoS MCP** ChatGPT app remains connected to the QNAP-hosted runtime through the **OpenAI Secure MCP Tunnel**. The canonical Phase 1 authority/runtime contract remains `4.0.0`; the deployment release is `4.1.9`.

## Required hosted identity

Every successful governed response must include:

```text
mcp_version: 4.0.0
deployment_release: 4.1.9
agent_id: cos
```

Local `/healthz` and `/readyz` must additionally report `transport: SECURE_MCP_TUNNEL`.

## Catalog and authority

- Exactly 27 CoS agent-facing tools are exposed.
- Exactly 10 registered agents remain canonical.
- `approval.record_decision` and `reliability.human_override` are absent from agent catalogs.
- Mesh Devil's Advocate remains a governed shared Skill, not an agent principal.

## v4.1.8 behavior carried forward

The hosted interface must continue to demonstrate exact closed input schemas, bounded `validation_failed` field details, canonical task lookup semantics, governed `CHATGPT_SKILL_HANDOFF`, AgentOps request binding, `COMPLETED != VERIFIED`, and valid governance audit-chain behavior.

## Consequential-action exclusion

Acceptance must not perform external sends, publishing, client commitments, pricing or discount approvals, final staffing commitments, human approval decisions, human reliability overrides, or other consequential real-world actions.

## Pass rule

v4.1.9 is production-accepted only when the deployed QNAP instance and actual published ChatGPT app both demonstrate the expected dual release identity, unchanged authority boundaries, preserved v4.1.8 MCP contract behavior, valid audit chain, and Secure MCP Tunnel-only production path.