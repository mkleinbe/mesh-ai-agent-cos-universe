# Changelog v4.4.0

## 2026-08-28

### Security and authority

- Replaced caller-trusted L4/L5 approval metadata with canonical TaskLedger approval resolution.
- Enforced exact task, approval status, authority level, approval owner, decision actor, action, and Michael-only L5 authority requirements.
- Added delegated capability intersection so a delegated owner can execute only capabilities explicitly granted by the canonical delegation and already present in the owner registry.
- Restricted nested delegation to canonical parent-child routes and task-local state.
- Added server-side owner validation before intake, decomposition, reassignment, and stall remediation.
- Versioned delegated owner execution as `mesh.cos.owner-execution.v2` and preserved a bounded legacy idempotency fingerprint migration path.
- Preserved canonical denial receipts for rejected delegated capability execution.

### Runtime and provenance

- Made logical Skill-agent handoffs explicit as authorization handoffs, not proof that a separate Workspace Agent process executed.
- Added capability-execution closure for all 10 registered agents across MCP control-plane, server-owned adapter, model-native role, ChatGPT app boundary, and deliberately non-executable modes.
- Added immutable source-commit and principal-specific publication-schema digest provenance to MCP response envelopes.
- Added exact published action-and-schema attestation; source-only validation now reports `SOURCE_CONTRACT_ONLY` instead of publication PASS.

### CI and release engineering

- Made normal CI release-neutral and moved current candidate packaging to v4.4.0.
- Added 100% branch-aware Python coverage for the new authority/security paths.
- Added capability-closure and published action-schema checks to CI.
- Hardened historical v4.3.0 workflow so future pull requests cannot rebuild historical release candidates.
- Prepared v4.4.0 QNAP and ChatGPT Skill artifacts for human-controlled release.

### Compatibility

- Runtime contract remains `4.0.0`; deployment/release identity advances to `4.4.0`.
- Human-only operations remain excluded from all agent action surfaces.
- Existing approved v4.3 owner-execution results remain replay-compatible through the bounded legacy fingerprint path.

### Manual gates

- Git tag/GitHub Release creation remains human-controlled when required.
- QNAP production deployment remains human-controlled.
- ChatGPT Workspace app publication remains blocked until an actual draft action+input-schema snapshot exactly matches the v4.4.0 source contract.
