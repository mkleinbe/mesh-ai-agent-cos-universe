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

    active_children_by_parent: dict[str, list[str]] = {}
    for agent_id, record in registry.items():
        if record.get("status") != "ACTIVE":
            continue
        parent_id = record.get("parent_agent_id")
        if parent_id:
            active_children_by_parent.setdefault(parent_id, []).append(agent_id)

    for agent_id, record in registry.items():
        parent_id = record.get("parent_agent_id")
        if not parent_id or record.get("status") != "ACTIVE":
            continue

        checked += 1
        parent = registry.get(parent_id)
        if parent is None or parent.get("status") != "ACTIVE":
            failures.append(f"{parent_id}->{agent_id}: active parent missing")
            continue
        if not parent.get("delegation_permissions") or int(parent.get("max_delegation_depth", 0)) <= 0:
            failures.append(f"{parent_id}->{agent_id}: canonical parent cannot delegate")

        allowed = set(policy.allowed_tools(agent_id))
        missing_owner = OWNER_LIFECYCLE - allowed
        if missing_owner:
            failures.append(f"{agent_id}: owner lifecycle missing {sorted(missing_owner)}")

        parent_allowed = set(policy.allowed_tools(parent_id))
        missing_parent = PARENT_TRANSPORT - parent_allowed
        if missing_parent:
            failures.append(f"{parent_id}->{agent_id}: parent transport missing {sorted(missing_parent)}")

        if active_children_by_parent.get(agent_id):
            if not record.get("delegation_permissions") or int(record.get("max_delegation_depth", 0)) <= 0:
                failures.append(f"{agent_id}: registered active child exists but delegation authority is absent")
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
