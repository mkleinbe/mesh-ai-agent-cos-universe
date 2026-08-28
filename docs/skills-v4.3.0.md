# Mesh CoS MCP v4.3.0 Skill Update Manifest

## Purpose

This manifest identifies every ChatGPT Skill package whose role contract changed as part of the v4.3.0 cross-agent owner-execution turn.

## Updated Skills

### mesh-chief-of-staff

Updated to document the Chief of Staff orchestration identity, delegation-bound owner execution, no-impersonation rule, owner-only completion for child-owned work, and current MCP allowlist.

### mesh-agentops-controller

Updated to align AgentOps lifecycle authority and delegated owner execution with the v4.3.0 owner-scoped runtime contract.

### mesh-answer-decision-desk

Updated to align Answer & Decision Desk task ownership, allowed operations, and delegated execution boundaries with the current MCP contract.

### mesh-cro

Updated to align CRO owner identity, owner-only lifecycle behavior, and MCP allowlist. CRO does not receive nested child-executor/decompose authority because the current registry has no CRO child.

### mesh-cfo

Updated to align CFO owner identity, owner-only lifecycle behavior, and MCP allowlist. CFO does not receive nested child-executor/decompose authority because the current registry has no CFO child.

### mesh-coo

Updated to align COO owner identity and nested delegated execution for its registered child, Consultant Network Steward.

### mesh-cmo

Updated to align CMO owner identity and nested delegated execution for its registered child, VP Content.

### mesh-message-operations

Updated to align Message Operations owner identity and lifecycle execution without widening external send authority or bypassing explicit approval requirements.

## Participating but not modified Skills

The following registered child Skills participate in the v4.3.0 nested execution architecture, but their Skill role-contract files were not changed in this turn:

- `mesh-vp-content`
- `mesh-consultant-network-steward`

## Workspace-agent package changes

The following workspace-agent manifests were updated separately from the Skill role contracts:

- `cos`
- `agentops`
- `answer-desk`
- `cro`
- `cfo`
- `coo`
- `cmo`
- `message-ops`

Their `mcp.allowed_tools` and builder configuration were aligned to the v4.3.0 contract.

## Installation bundle contract

A human-installable v4.3.0 Skill update bundle should contain exactly the eight updated Skill directories listed above, preserving each directory's internal structure. The bundle should also include a root manifest identifying:

- source repository: `mkleinbe/mesh-ai-agent-cos-universe`;
- semantic release: `v4.3.0`;
- integrated main commit;
- included Skill names;
- source paths under `chatgpt/skills/`;
- statement that workspace-agent manifests are not ChatGPT Skill directories and are therefore not included in the Skill-install ZIP.
