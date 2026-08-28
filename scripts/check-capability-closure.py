#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "capability-execution.v1.json"
VALID_MODES = {
    "MCP_CONTROL_PLANE",
    "SERVER_OWNED_ADAPTER",
    "MODEL_NATIVE_ROLE_CAPABILITY",
    "CHATGPT_APP_BOUNDARY",
    "DECLARED_NON_EXECUTABLE",
}


def main() -> int:
    registry = load_registry()
    policy = WorkspaceAgentMCPPolicy.from_file()
    adapters = GovernedAdapterRegistry(registry)
    payload = json.loads(CONFIG.read_text())
    failures: list[str] = []
    if payload.get("version") != "mesh.cos.capability-execution.v1":
        failures.append("capability execution manifest version mismatch")
    configured_agents = payload.get("agents", {})
    if set(configured_agents) != set(registry):
        failures.append("capability manifest must cover exactly the canonical agent roster")

    skill_count = 0
    tool_count = 0
    for agent_id, record in registry.items():
        allowed_mcp = set(policy.allowed_tools(agent_id))
        for capability in record.get("skills", []):
            skill_count += 1
            adapter = adapters.adapters.get((agent_id, str(capability)))
            if adapter is None:
                failures.append(f"{agent_id}:{capability}: declared Skill has no governed handoff")
                continue
            result = adapter.execute({"task_id": "closure-probe", "authority_level": 0})
            if result.get("execution_mode") != "CHATGPT_SKILL_HANDOFF":
                failures.append(f"{agent_id}:{capability}: Skill is not a ChatGPT handoff")
            if result.get("execution_claim") != "AUTHORIZATION_HANDOFF_ONLY":
                failures.append(f"{agent_id}:{capability}: Skill handoff overclaims execution")
            if result.get("synchronous_workspace_agent_execution") is not False:
                failures.append(f"{agent_id}:{capability}: synchronous Workspace Agent execution is not proven")
            if result.get("result_provenance_required") is not True:
                failures.append(f"{agent_id}:{capability}: result provenance requirement missing")

        declared_tools = set(record.get("tools", []))
        configured_tools = configured_agents.get(agent_id, {}).get("tools", {})
        if set(configured_tools) != declared_tools:
            missing = sorted(declared_tools - set(configured_tools))
            extra = sorted(set(configured_tools) - declared_tools)
            failures.append(f"{agent_id}: tool closure drift missing={missing} extra={extra}")
            continue
        for capability, config in configured_tools.items():
            tool_count += 1
            mode = config.get("mode")
            if mode not in VALID_MODES:
                failures.append(f"{agent_id}:{capability}: unsupported execution mode {mode!r}")
                continue
            if mode == "MCP_CONTROL_PLANE":
                backing = set(config.get("backing_mcp_tools", []))
                if not backing:
                    failures.append(f"{agent_id}:{capability}: MCP control capability lacks backing tools")
                missing = backing - allowed_mcp
                if missing:
                    failures.append(f"{agent_id}:{capability}: backing MCP tools unavailable {sorted(missing)}")
            elif mode == "SERVER_OWNED_ADAPTER":
                adapter_capability = str(config.get("capability") or capability)
                if (agent_id, adapter_capability) not in adapters.adapters:
                    failures.append(f"{agent_id}:{capability}: server-owned adapter is not registered")
            elif mode == "MODEL_NATIVE_ROLE_CAPABILITY":
                if config.get("not_mcp_callable") is not True or not str(config.get("reason") or "").strip():
                    failures.append(f"{agent_id}:{capability}: model-native boundary is not explicit")
                backing_skill = config.get("backing_skill")
                if backing_skill and backing_skill not in set(record.get("skills", [])):
                    failures.append(f"{agent_id}:{capability}: backing Skill is not declared")
            elif mode == "CHATGPT_APP_BOUNDARY":
                if config.get("human_approval_required") is not True:
                    failures.append(f"{agent_id}:{capability}: app-boundary write lacks human approval requirement")
                backing_skill = str(config.get("backing_skill") or "")
                if backing_skill not in set(record.get("skills", [])):
                    failures.append(f"{agent_id}:{capability}: app boundary lacks declared backing Skill")
            elif mode == "DECLARED_NON_EXECUTABLE":
                if not str(config.get("reason") or "").strip():
                    failures.append(f"{agent_id}:{capability}: non-executable declaration lacks rationale")
                if (agent_id, capability) in adapters.adapters:
                    failures.append(f"{agent_id}:{capability}: marked non-executable but adapter is registered")

    if failures:
        print("CAPABILITY_CLOSURE=FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(
        "CAPABILITY_CLOSURE=PASS "
        f"agents={len(registry)} skills={skill_count} declared_tools={tool_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
