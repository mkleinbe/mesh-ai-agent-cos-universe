# ChatGPT Workspace Agent gap assessment - 2026-08-17

## Result

Repository-level requirements for translating the canonical Phase 1 organization into ChatGPT Workspace Agent packages are closed for release `0.2.0`. The remaining items require the Workspace Agent builder or production infrastructure and are explicitly not represented as completed integrations.

The final pre-merge PR-head quality run completed successfully with **85 tests passed and 79.71% branch-aware coverage**, all 11 JSON contract schemas validated, runtime/documentation drift green, ChatGPT Workspace Agent package drift green, Ruff critical lint green, Bandit high-severity scanning green, dependency integrity green, and compileall green.

## TDD and loop-engineering findings

| Priority | Gap found | Resolution |
|---|---|---|
| P0 | No Workspace Agent Skills, manifests, or MCP contract existed. | Added 11 role Skills, 11 exact builder manifests, and `mesh-cos-mcp.v1.json`. |
| P0 | Builder-only tool restrictions would not be sufficient server-side enforcement. | Added `WorkspaceAgentMCPPolicy` with deny-by-default agent/tool authorization and runtime-binding validation. |
| P0 | Message Operations could not prove recorded approval through the initial MCP tool set. | Added read-only `approval.get`; Message Operations cannot decide approvals. |
| P0 | Existing `task.verify` used an in-process Python callable that a remote MCP client cannot supply. | Added `ChiefOfStaffService.record_verification_result()` requiring verifier identity and explicit evidence; passing verification without evidence fails closed without changing the task to `VERIFIED`. |
| P1 | Registry discovery was missing from the initial MCP contract. | Added read-only `registry.list_agents` for CoS and AgentOps. |
| P1 | A generic manifest was not an exact Builder field mapping. | Added `builder_configuration` for name, description, model preference/fallback, reasoning, Skill, knowledge files, custom MCP, apps, write approval, Connector Action Constraints, channels, starter prompts, and private-until-tested state. |
| P1 | Risky app surfaces needed explicit fail-closed constraints. | LinkedIn/AuthoredUp remain non-publishing, Apollo remains research/enrichment only, Gmail/Slack sends through Message Operations remain approval-bound, and Answer Desk Slack remains disabled until a dedicated channel exists. |
| P1 | Skill source packages needed independent validation. | All 11 Skills were initialized with OpenAI skill-creator, validated with `quick_validate.py`, and packaged with `package_skill.py`. |
| P1 | Exact Builder governance was initially compared to normalized runtime authority and produced a false failure. | Classified as a test defect. Exact Builder values are now compared to the raw canonical registry, while normalized authority behavior remains tested separately at runtime. |
| P1 | Advancing the repository release left a stale test assertion at `0.1.4`. | Corrected the test and added release drift enforcement across package/runtime, Workspace Agent manifests, and MCP contract at `0.2.0`. |
| P2 | Future registry/config drift could silently widen access. | Added `scripts/check-chatgpt-packages.py` plus CI checks comparing registry identity/authority to manifests and validating Skill structure, MCP allowlists, runtime bindings, app constraints, and release metadata. |

## Loop evidence

1. **RED:** commit `17464764eb6c73c3ca98b89554a0a0b84c8c08d6` added the Workspace Agent acceptance suite before implementation. CI run `32065566172` reported 74 passing tests and 7 expected failures because the Skills, manifests, MCP contract, and builder handoff did not yet exist.
2. **Architecture gap closure:** added `registry.list_agents`, read-only `approval.get`, `WorkspaceAgentMCPPolicy`, exact per-agent allowlists, role-specific app constraints, and the MCP-safe verification path.
3. **Test-defect loop:** CI run `32067172916` reached 84 passing tests with one failure caused by comparing raw human-readable authority to the runtime-normalized value. The test was corrected without weakening runtime authorization.
4. **Release-drift loop:** CI run `32068111857` passed contracts, both drift gates, and Ruff, then exposed only the stale `0.1.4` release assertion. That test was advanced to the intended `0.2.0` release.
5. **GREEN:** PR-head CI run `32068375297`, job `95505651541`, completed successfully: 85 tests passed, 79.71% branch-aware coverage, contracts green, runtime/documentation drift green, Workspace Agent package drift green, Ruff green, Bandit green, dependency integrity green, and compileall green.

## Requirements pressure test

The repository now enforces the following invariants rather than relying on prompt convention:

- every canonical registry agent maps to exactly one Workspace Agent manifest and one OpenAI Skill,
- stable role identity is separate from implementation/repository release versioning,
- Builder authority, approvals, prohibited actions, delegation depth, and accountable domain match the raw canonical registry,
- Workspace app permissions and Connector Action Constraints are least-privilege and cannot widen the registry,
- Workspace writes default to **Always ask** as defense in depth,
- MCP authorization is deny-by-default and server-side,
- only CoS receives task reassignment authority,
- Message Operations can read but cannot decide canonical approvals,
- Answer Desk Slack cannot activate without a dedicated channel ID,
- remote verification cannot claim success without named verifier identity and evidence,
- `TaskLedger` remains canonical and governance remains canonical-first,
- material decisions/recommendations remain explainable through `decision.v2`, consequential actions remain auditable through `agent-event.v2`, and private chain-of-thought remains prohibited,
- the Workspace Agent builder handoff requires positive tests, negative authority tests, missing-evidence tests, and permission-denial tests before publication.

## Production dependencies, not repository gaps

- Publish the approved remote `mesh-cos-mcp` endpoint and configure `MESH_COS_MCP_SERVER_URL`.
- Connect approved Workspace apps with least-privilege user or agent-owned authentication.
- Configure the separate Answer Desk Slack channel ID before enabling that Slack channel.
- Configure production approval-owner mappings, source credentials, MCP authentication, and other secrets outside source control.
- Run private Workspace Agent preview acceptance tests in the target workspace and publish through the intended RBAC only after those tests pass.

Do not mark any production dependency complete until it is actually configured and tested in the target workspace.

<!-- mesh-cos-v2-shared-da -->
## v2.0.0 current architecture

The live Phase 1 runtime is a **10-agent** organization. The former repository-local Devil's Advocate agent and duplicate role Skill are removed. **Mesh Devil's Advocate** is an external **shared Skill** available only to Chief of Staff and CRO through governed Skill invocation. It is **advisory** only, cannot overwrite **canonical facts**, cannot execute external actions, and returns decision authority to the owning role or qualified human. `TaskLedger` remains canonical state; ChatGPT uses `LOCAL_STDIO` through `MCPRuntime` with deny-by-default allowlists, human-only approval/override paths, `check-chatgpt-packages.py` drift enforcement, and the 100% branch-aware coverage gate. Historical references to an 11-agent roster or a local Devil's Advocate role describe superseded releases only.

