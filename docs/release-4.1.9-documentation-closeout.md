# v4.1.9 Documentation and Release Closeout

v4.1.9 closes release-documentation drift left after the v4.1.8 corrective release and advances the QNAP deployment identity and release automation to a single consistent patch version.

## Scope

This patch does not add agent authority or product behavior. It carries forward the v4.1.8 MCP contract validation, safe structured errors, governed `CHATGPT_SKILL_HANDOFF`, AgentOps request binding, QNAP image provenance, modern MCP transport, non-root runtime, persistence, backup, and Secure MCP Tunnel controls.

## Canonical invariants

- Phase 1 authority/runtime contract: `4.0.0`
- Registered workforce: exactly 10 agents
- CoS agent-facing catalog: exactly 27 governed tools
- Human-principal-only operations: `approval.record_decision`, `reliability.human_override`
- Mesh Devil's Advocate: governed shared Skill, not agent 11
- Canonical persistence: SQLite TaskLedger
- Lifecycle: `COMPLETED != VERIFIED`
- Production ingress: OpenAI Secure MCP Tunnel

## Documentation closeout

v4.1.9 updates the active repository, QNAP operator, deployment, acceptance, checklist, changelog, release, CI, and release-automation references so the current release is described consistently. Historical versioned documents remain historical evidence and are not rewritten.

The v4.1.8 changelog entry is restored so the shipped MCP contract corrections are represented in the canonical release history.

## Release identity

- Repository/QNAP deployment release: `4.1.9`
- Semantic tag: `v4.1.9`
- Container image label: `4.1.9-qnap`
- Canonical MCP/runtime contract: `4.0.0`

## Verification gate

The exact v4.1.9 candidate must pass the full repository/QNAP CI suite and deterministic bundle/checksum gate before merge. The semantic tag and GitHub Release must target the verified merged `main` commit.

## Production acceptance boundary

After QNAP deployment, successful governed responses must report:

```text
mcp_version: 4.0.0
deployment_release: 4.1.9
agent_id: cos
```

Final production acceptance remains a post-deploy hosted check through the installed Mesh CoS MCP ChatGPT app and OpenAI Secure MCP Tunnel.