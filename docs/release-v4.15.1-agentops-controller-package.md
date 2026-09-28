# Mesh CoS v4.15.1 AgentOps Controller Skill Package

Release date: 2026-09-28

## Outcome

Publishes the current `mesh-agentops-controller` ChatGPT Skill as a dedicated human-installable release asset.

## Semantic version

This is a PATCH release. The AgentOps behavior is already present in the v4.15.0 repository source. v4.15.1 closes the distribution gap by packaging that exact Skill independently for manual ChatGPT installation.

## Release asset

- `mesh-agentops-controller-v4.15.1.zip`
- `mesh-agentops-controller-v4.15.1.zip.sha256`

The ZIP contains only the `mesh-agentops-controller` Skill directory and its existing supporting files.

## Scope

Included:
- `chatgpt/skills/mesh-agentops-controller/SKILL.md`
- `chatgpt/skills/mesh-agentops-controller/agents/openai.yaml`
- `chatgpt/skills/mesh-agentops-controller/references/**`
- `chatgpt/skills/mesh-agentops-controller/scripts/**`

No other ChatGPT Skill is included.

## Runtime boundary

Canonical MCP authority/runtime contract remains 4.0.0. QNAP deployment remains 4.4.2. This release packages an existing ChatGPT Skill and requires no QNAP redeployment.

## Installation

Download `mesh-agentops-controller-v4.15.1.zip` from this GitHub release and use it to manually replace the installed `mesh-agentops-controller` Skill in ChatGPT.
