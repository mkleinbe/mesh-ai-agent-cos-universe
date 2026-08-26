# QNAP Security Review v4.1.8

## Classification

Security applicability: **TARGETED**.

v4.1.8 changes the MCP request-contract boundary, error projection, governed Skill registration/handoff, and the packaged production runtime. It does not change the canonical Phase 1 authority model, TaskLedger ownership, Secure MCP Tunnel architecture, or human approval model.

## Trust boundaries reviewed

1. ChatGPT client to MCP `tools/list` and `tools/call`.
2. TypeScript MCP server to the Python stdio bridge.
3. Python request validation to `MCPRuntime` authorization and handlers.
4. Bound `MESH_COS_AGENT_ID` to the per-agent tool allowlist.
5. `skills.invoke_governed` to server-declared Skill handoff adapters.
6. MCP writes to canonical SQLite TaskLedger and governance audit records.
7. QNAP deployment bundle to the existing Secure MCP Tunnel production boundary.

## Security properties

- Public tool schemas are closed, deterministic, and match runtime request binding.
- Missing, malformed, enum-invalid, and unknown fields fail before business execution with bounded field-level diagnostics.
- Validation responses never expose stack traces, credentials, filesystem internals, raw exception text, private data, or chain-of-thought.
- Runtime identity is server-bound and cannot be supplied or changed by tool payloads.
- `approval.record_decision` and `reliability.human_override` remain human-principal-only and absent from agent-facing catalogs.
- Governed Skills are limited to registry-declared, agent-allowlisted capabilities.
- Client payloads cannot supply code, import paths, callables, shell commands, plugin executables, or Skill implementations for execution.
- The QNAP MCP does not execute ChatGPT Skills as arbitrary server code. It returns a bounded `CHATGPT_SKILL_HANDOFF` authorization record that is audited and leaves actual Skill execution to the ChatGPT Skill runtime.
- TaskLedger remains canonical and material governed operations remain auditable.
- `COMPLETED != VERIFIED` remains enforced.

## Findings and remediation

### SEC-QNAP-030 Public schema/runtime drift

**Finding:** v4.1.7 projected generic MCP object schemas while Python handlers required specific fields. Request-shape failures could reach handler code and be reported opaquely.

**Remediation:** v4.1.8 adds an exact checked-in input-schema registry for the full runtime tool catalog, projects those schemas through `tools/list`, and validates arguments before dispatch.

**Status:** remediated by automated contract and runtime tests.

### SEC-QNAP-031 Error classification ambiguity

**Finding:** request-binding `KeyError` could be classified as resource `not_found`, and invalid structured inputs provided no safe corrective detail.

**Remediation:** request validation now has a dedicated `validation_failed` category with bounded `{field, reason}` details. Runtime errors are separated into deterministic categories without returning raw exception messages.

**Status:** remediated by regression tests.

### SEC-QNAP-032 Declared Skill without server registration

**Finding:** registry-declared governed Skills could be allowlisted but unresolved by the default runtime registry.

**Remediation:** declared Skills are server-registered as non-executable, auditable ChatGPT Skill handoffs. Unknown and unauthorized capabilities fail closed. Executable material supplied by clients is rejected.

**Status:** remediated by authorization, handoff, provenance, and arbitrary-execution rejection tests.

## Verification requirements

Release verification must include:

- TypeScript build and MCP contract tests;
- Python unit/integration tests with 100% branch-aware coverage;
- `npm audit --audit-level=high`;
- Bandit high-severity scan;
- contract/documentation drift checks;
- exact 10-agent identity and allowlist tests;
- governed Skill allowed/denied tests;
- QNAP shell, bundle, Compose, production-image, modern MCP transport, non-root ownership, hardened runtime, restart, and SQLite backup gates;
- post-deploy hosted acceptance through the published ChatGPT app.

## Residual risk

Repository and container verification cannot prove the final on-premises serving instance or ChatGPT-hosted path. Production acceptance remains pending until v4.1.8 is deployed to QNAP and the hosted interface is retested. No release process may convert that environmental evidence gap into a technical PASS.
