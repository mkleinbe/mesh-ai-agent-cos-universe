# v4.1.9 Documentation and Release Closeout

`v4.1.9` is a release-integrity and documentation-closeout patch for the QNAP-hosted **Mesh CoS MCP** runtime and published ChatGPT app connected through the **OpenAI Secure MCP Tunnel**.

The canonical Mesh CoS Phase 1 authority/runtime contract remains **`4.0.0`**. Phase 1 remains exactly 10 agents, including Message Operations as the tenth registered agent. Human-only operations, canonical TaskLedger, `COMPLETED != VERIFIED`, resource policy, and the Secure MCP Tunnel trust boundary are unchanged.

## Why this release exists

v4.1.8 correctly shipped the MCP request-contract remediation and passed the repository/QNAP release gate, but several active documentation surfaces still described v4.1.7 and the canonical changelog lacked the v4.1.8 entry. v4.1.9 closes that release-documentation drift and advances the deployment/release identity consistently across the active bundle, QNAP runbooks, CI, release automation, and acceptance evidence.

## v4.1.8 behavior carried forward

- Canonical closed input schemas are projected through `tools/list` and validated before business dispatch.
- Invalid structured input returns bounded `validation_failed` field/reason details without raw exceptions or secrets.
- Request validation is distinguished from canonical TaskLedger `not_found` lookup behavior.
- Registry-declared governed Skills resolve as auditable `CHATGPT_SKILL_HANDOFF` capabilities rather than arbitrary QNAP code execution.
- Client-supplied code, import paths, callables, shell commands, plugin executables, and Skill implementations remain rejected.
- `agentops.recommend` uses the documented structured request contract.
- Image reuse remains bound to OCI version/revision labels matching extracted release metadata.
- Post-deploy verification executes a governed read-only MCP call from the tunnel network namespace and validates the running dual release identity.

## BDD and TDD evidence

v4.1.8 ready scenarios QNAP-059 through QNAP-068 remain the behavior contract for MCP request validation, governed Skill handoff, immutable identity, delegation, lifecycle separation, and audit integrity.

v4.1.9 adds ready scenarios QNAP-069 through QNAP-073 for:

- active documentation release consistency;
- bundle/image/Compose/governed-envelope deployment identity agreement;
- unchanged Phase 1 authority;
- deterministic secret/state-safe release packaging;
- explicit post-deploy hosted acceptance boundaries.

## Security boundary

Security applicability is **TARGETED** because CI/CD, deployment identity, QNAP packaging, and release evidence are touched.

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

See `docs/qnap-security-review-v4.1.9.md`.

## Release assets

- `mesh-cos-mcp-qnap-v4.1.9.zip`
- `mesh-cos-mcp-qnap-v4.1.9.zip.sha256`

The bundle contains the release-bound build context, QNAP operator tooling, current deployment and acceptance procedures, historical release evidence, the v4.1.9 security/release/hosted-acceptance receipts, and v4.1.9 BDD scenarios. It contains no tunnel runtime secret and no canonical TaskLedger data.

## Version identity

- Repository/QNAP deployment release: `4.1.9`
- Semantic tag: `v4.1.9`
- Container image label default: `4.1.9-qnap`
- Canonical Phase 1 authority/runtime contract: `4.0.0` unchanged
- Canonical workforce: exactly 10 agents
- Mesh Devil's Advocate remains a governed shared Skill, not agent 11
- CoS production agent-facing catalog: 27 governed tools
- Two human-principal-only operations remain separate from agent catalogs
- Production transport: OpenAI Secure MCP Tunnel

## Verification gate

The exact candidate must pass the full repository and QNAP release suite before integration, including Python 100% branch-aware coverage, TypeScript MCP checks, contract/documentation drift checks, Ruff, mypy, npm audit, Bandit, QNAP shell regressions, deterministic bundle/checksum generation, Compose validation, OCI image provenance, modern MCP discovery, sequential requests, non-root ownership, hardened runtime, direct-ingress denial, restart, and SQLite backup integrity.

## Post-deploy acceptance boundary

Repository, container, and release-package verification cannot prove the newly deployed on-premises serving instance. After deploying v4.1.9 to QNAP, repeat the published-app acceptance suite and require successful governed responses to report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.9
agent_id: cos
```

Do not mark production acceptance PASS until the actual hosted Mesh CoS MCP app is green.

See:

- `docs/qnap-security-review-v4.1.9.md`
- `docs/release-4.1.9-documentation-closeout.md`
- `docs/chatgpt-published-app-production-acceptance-v4.1.9.md`
- `specs/qnap-release-closeout-v4.1.9.feature`
- `deployment/qnap/DEPLOYMENT-STEPS.md`
- `deployment/qnap/CHATGPT-ACCEPTANCE.md`
