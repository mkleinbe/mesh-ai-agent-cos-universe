# ChatGPT Skills v4.4.0

## Bundle

The v4.4.0 human-installable ChatGPT Skill bundle contains eight governed Mesh skills:

1. `mesh-chief-of-staff`
2. `mesh-agentops-controller`
3. `mesh-answer-decision-desk`
4. `mesh-cro`
5. `mesh-cfo`
6. `mesh-coo`
7. `mesh-cmo`
8. `mesh-message-operations`

Specialist roles such as VP Content and Consultant Network Steward remain registered in the canonical 10-agent roster and are reached through bounded parent-child delegation and their governed capability context; they are not added as duplicate top-level install packages merely to simulate process separation.

## Execution boundary

A declared Skill handoff is a **logical Skill-agent authorization handoff** inside the governed ChatGPT reasoning environment. It does not prove that a separate synchronous Workspace Agent process executed.

The v4.4.0 handoff response explicitly identifies:

- `execution_mode=CHATGPT_SKILL_HANDOFF`
- `agent_execution_model=LOGICAL_SKILL_AGENT`
- `handoff_semantics=AUTHORIZATION_HANDOFF_ONLY`
- `synchronous_workspace_agent_execution=false`
- `result_provenance_required=true`

Canonical ownership, delegation, authority, approvals, audit, completion, and verification state remain with Mesh CoS MCP and TaskLedger.

## Installation and release boundary

The bundle is prepared by repository CI but installation remains human-controlled, one Skill at a time, according to Workspace policy. The bundle intentionally does not contain Workspace Agent manifests and does not publish or modify a ChatGPT custom app.

## Provenance

`MANIFEST.txt` binds the bundle to:

- release `v4.4.0`
- source repository `mkleinbe/mesh-ai-agent-cos-universe`
- exact source commit used by the artifact build
- skill count 8
- manual installation mode

The Skill bundle does not replace the separate ChatGPT MCP action+schema publication acceptance gate.