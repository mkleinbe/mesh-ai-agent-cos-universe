# v4.1.8 MCP Contract Validation and Governed Skill Handoff

## Purpose

v4.1.8 is a corrective production-interface release for Mesh CoS MCP. It closes request-schema drift, opaque validation behavior, canonical task-identifier ambiguity caused by request binding, and missing runtime registration for declared governed Skills.

The canonical MCP and Phase 1 authority/runtime contract remains **4.0.0**. The workforce remains exactly 10 agents. Human-only operations, authority ceilings, TaskLedger canonicality, `COMPLETED != VERIFIED`, and the OpenAI Secure MCP Tunnel architecture are unchanged.

## Corrective changes

- Added a checked-in input-schema registry covering the complete runtime tool catalog.
- MCP `tools/list` now projects the actual closed schema each runtime handler accepts.
- Python validates structured inputs before handler dispatch.
- Safe `validation_failed` responses contain bounded field/reason details.
- Request-binding errors no longer masquerade as missing canonical TaskLedger records.
- AgentOps uses the same structured request contract as the rest of the MCP.
- Registry-declared Skills are server-registered as auditable `CHATGPT_SKILL_HANDOFF` capabilities.
- Unknown and unauthorized Skills continue to fail closed.
- Client-supplied executable fields are rejected and are never interpreted as server code.
- Existing dual response identity remains `mcp_version: 4.0.0`, `deployment_release: 4.1.8`, and immutable bound `agent_id`.

## Acceptance evidence

BDD scenarios QNAP-059 through QNAP-068 cover request validation, canonical task lookup, governed Skill resolution, AgentOps, all ten bound identities, delegation boundaries, lifecycle separation, audit integrity, and packaged/hosted agreement.

The release gate requires the full Python and Node suites, 100% branch-aware coverage, security checks, QNAP shell tests, release-bundle inspection, Compose validation, production container build, modern MCP transport checks, non-root ownership handoff, hardened runtime verification, restart recovery, and Docker-mediated SQLite backup.

## Deployment boundary

The release package may be published after repository, security, and QNAP candidate gates pass. Final **production acceptance** remains pending until the package is deployed on QNAP and the published ChatGPT app is exercised again through the Secure MCP Tunnel.

Expected hosted identity after deployment:

```text
mcp_version: 4.0.0
deployment_release: 4.1.8
agent_id: cos
```

See `docs/qnap-security-review-v4.1.8.md`, `specs/qnap-mcp-production-acceptance-v4.1.8.feature`, and `deployment/qnap/CHATGPT-ACCEPTANCE.md`.
