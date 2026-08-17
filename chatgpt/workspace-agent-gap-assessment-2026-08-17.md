# ChatGPT Workspace Agent gap assessment - 2026-08-17

## Result

Repository-level requirements for translating the Phase 1 organization into ChatGPT Workspace Agent packages are closed in this increment. Remaining items require the Workspace Agent builder or production infrastructure and are not represented as completed integrations.

## TDD and loop-engineering findings

| Priority | Gap found | Resolution |
|---|---|---|
| P0 | No Workspace Agent Skills, manifests, or MCP contract existed. | Added 11 role Skills, 11 exact builder manifests, and `mesh-cos-mcp.v1.json`. |
| P0 | Builder-only tool restrictions would not be sufficient server-side enforcement. | Added `WorkspaceAgentMCPPolicy` with deny-by-default agent/tool authorization and runtime-binding validation. |
| P0 | Message Operations could not prove recorded approval through the initial MCP tool set. | Added read-only `approval.get`; Message Operations cannot decide approvals. |
| P0 | Existing `task.verify` used an in-process Python callable that a remote MCP client cannot supply. | Added an MCP-safe verification recording path requiring verifier identity and explicit evidence, with fail-closed evidence requirements. |
| P1 | Registry discovery was missing from the initial MCP contract. | Added read-only `registry.list_agents` for CoS and AgentOps. |
| P1 | A generic manifest was not an exact Builder field mapping. | Added `builder_configuration` for name, description, model preference/fallback, reasoning, Skill, knowledge files, custom MCP, apps, write approval, connector constraints, channels, starter prompts, and private-until-tested state. |
| P1 | Risky app surfaces needed explicit fail-closed constraints. | LinkedIn/AuthoredUp remain non-publishing, Apollo remains research-only, Gmail/Slack sends through Message Operations remain approval-bound, and Answer Desk Slack remains disabled until a dedicated channel exists. |
| P1 | Skill source packages needed independent validation. | All 11 Skills were initialized with OpenAI skill-creator, validated with `quick_validate.py`, and packaged with `package_skill.py`. |
| P2 | Future registry/config drift could silently widen access. | Added CI package audit/tests comparing registry identity/authority to manifests and validating MCP allowlists/runtime bindings. |

## Production dependencies, not repository gaps

- Publish the remote `mesh-cos-mcp` endpoint and configure `MESH_COS_MCP_SERVER_URL`.
- Connect approved Workspace apps with least-privilege user or agent-owned authentication.
- Configure the separate Answer Desk Slack channel ID before enabling that Slack channel.
- Configure production approval-owner mappings and secrets outside source control.
- Use Workspace Agent builder to create, preview-test, and publish the 11 agents because this repository cannot press the product UI's final create/publish controls.

Do not mark any production dependency complete until it is actually configured and tested in the target workspace.
