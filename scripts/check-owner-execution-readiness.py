#!/usr/bin/env python3
from __future__ import annotations

from mesh_cos.mcp_policy import WorkspaceAgentMCPPolicy
from mesh_cos.registry import load_registry

OWNER_LIFECYCLE = {"task.get", "task.transition", "task.check_in", "task.complete"}
PARENT_TRANSPORT = {"delegation.create", "delegation.execute_owner"}
DELEGATING_OWNER_TOOLS = {"task.decompose", "delegation.create", "delegation.execute_owner"}


def main() -> int:
    registry = load_registry()
    policy = WorkspaceAgentMCPPolicy.from_file()
    failures: list[str] = []
    checked = 0

    for agent_id, record in registry.items():
        parent_id = record.get("parent_agent_id")
        if not parent_id or record.get("status") != "ACTIVE":
            continue
        parent = registry[parent_id]
        if not parent.get("delegation_permissions") or int(parent.get("max_delegation_depth", 0)) <= 0:
            continue
        checked += 1
        allowed = set(policy.allowed_tools(agent_id))
        missing_owner = OWNER_LIFECYCLE - allowed
        if missing_owner:
            failures.append(f"{agent_id}: owner lifecycle missing {sorted(missing_owner)}")

        parent_allowed = set(policy.allowed_tools(parent_id))
        missing_parent = PARENT_TRANSPORT - parent_allowed
        if missing_parent:
            failures.append(f"{parent_id}->{agent_id}: parent transport missing {sorted(missing_parent)}")

        if int(record.get("max_delegation_depth", 0)) > 0 and record.get("delegation_permissions"):
            missing_delegate = DELEGATING_OWNER_TOOLS - allowed
            if missing_delegate:
                failures.append(f"{agent_id}: nested-delegation path missing {sorted(missing_delegate)}")

    if failures:
        print("OWNER_EXECUTION_READINESS=FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"OWNER_EXECUTION_READINESS=PASS checked={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
