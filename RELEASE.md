# v4.1.8 MCP Contract Validation and Governed Skill Handoff

`v4.1.8` is a corrective production-interface and QNAP deployment release for the published **Mesh CoS MCP** ChatGPT app connected through the **OpenAI Secure MCP Tunnel**.

The canonical Mesh CoS Phase 1 authority/runtime contract remains **`4.0.0`**. Phase 1 remains exactly 10 agents, including Message Operations as the tenth registered agent. Human-only operations, canonical TaskLedger, `COMPLETED != VERIFIED`, resource policy, and the Secure MCP Tunnel trust boundary are unchanged.

## Defects remediated

### Public MCP schema drift

The hosted MCP previously projected generic object inputs while Python handlers required specific fields. Valid-looking client requests could therefore fail after dispatch with opaque `invalid_request` responses.

v4.1.8 adds a canonical input-schema registry covering the complete runtime catalog and projects the actual closed schema through `tools/list`. Structured arguments are validated before business handler execution.

### Opaque request and lookup errors

Request-binding `KeyError` could be confused with a missing canonical TaskLedger record. v4.1.8 introduces bounded `validation_failed` responses with safe `{field, reason}` details and separates request validation from resource lookup and lifecycle failures.

### Governed Skill registration

Registry-declared Skills such as `mesh-ppmd-bot` could be allowlisted but unresolved by the default runtime adapter registry. v4.1.8 server-registers declared prompt Skills as auditable `CHATGPT_SKILL_HANDOFF` capabilities. The QNAP runtime does not import or execute arbitrary Skill code. Unknown or unauthorized capabilities continue to fail closed, and client-supplied code, import paths, callables, shell commands, plugin executables, and Skill implementations are rejected.

### AgentOps request binding

`agentops.recommend` now uses the same explicit structured schema and validation boundary as the rest of the hosted MCP.

## BDD and TDD evidence

Ready scenarios QNAP-059 through QNAP-068 cover:

- schema/runtime agreement;
- safe structured validation;
- consistent canonical task identifiers;
- governed Skill resolution and fail-closed denial;
- AgentOps request binding;
- exact 10-agent immutable identity and allowlist projection;
- delegation limits;
- `COMPLETED != VERIFIED`;
- audit integrity;
- packaged and hosted release identity agreement.

The changes were driven through RED/GREEN regression loops and must pass the full repository and QNAP release gate before integration.

## Security boundary

Security applicability is **TARGETED** because MCP input validation, agent authorization, governed Skill handoff, persistence-facing operations, and deployment/runtime packaging are touched.

Preserved controls include:

- `MCP_AUTH_MODE=tunnel` for remote production;
- private tunnel-client source-IP gating before `/mcp` dispatch;
- immutable server-bound `MESH_COS_AGENT_ID`;
- no agent-facing exposure of `approval.record_decision` or `reliability.human_override`;
- deny-by-default per-agent tool allowlists;
- no client-supplied executable code path;
- canonical SQLite TaskLedger and audit-chain semantics;
- long-running runtime UID/GID 65532, read-only rootfs, all capabilities dropped, no-new-privileges, and no Docker socket;
- existing tunnel secret handling and network architecture unchanged.

See `docs/qnap-security-review-v4.1.8.md`.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.8.zip`
- `mesh-cos-mcp-qnap-v4.1.8.zip.sha256`

The bundle contains the release-bound build context, QNAP operator tooling, the current acceptance procedure, v4.1.8 BDD scenarios, targeted security review, release handoff, and hosted acceptance contract. It contains no tunnel runtime secret and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.8`
- Semantic tag: `v4.1.8`
- Container image label default: `4.1.8-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 agents
- Mesh Devil's Advocate remains a governed shared Skill, not agent 11
- CoS production agent-facing catalog: 27 governed tools
- Two human-principal-only operations remain separate from agent catalogs
- Production transport: OpenAI Secure MCP Tunnel

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the newly deployed on-premises serving instance. After deploying v4.1.8 to QNAP, repeat the published-app acceptance suite and require successful governed responses to report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.8
agent_id: cos
```

Do not mark production acceptance PASS until the actual hosted Mesh CoS MCP app is green.

See:

- `docs/qnap-security-review-v4.1.8.md`
- `docs/release-4.1.8-mcp-contract-acceptance.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.8.md`
- `specs/qnap-mcp-production-acceptance-v4.1.8.feature`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
