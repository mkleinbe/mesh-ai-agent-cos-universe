from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class WorkspaceAgentMCPPolicy:
    """Fail-closed policy view of the checked-in Workspace Agent MCP contract."""

    contract: dict[str, Any]

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> WorkspaceAgentMCPPolicy:
        contract_path = (
            Path(path)
            if path is not None
            else Path(__file__).resolve().parents[2] / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
        )
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        policy = cls(contract)
        policy.validate()
        return policy

    def validate(self) -> None:
        if self.contract.get("name") != "mesh-cos-mcp":
            raise ValueError("Unexpected MCP contract name")
        if self.contract.get("canonical_state") != "TaskLedger":
            raise ValueError("TaskLedger must remain canonical")
        security = self.contract.get("security", {})
        if security.get("deny_by_default") is not True:
            raise ValueError("MCP policy must deny by default")
        if security.get("approval_fail_closed") is not True:
            raise ValueError("MCP approval policy must fail closed")

        tools = self._tools()
        if not tools:
            raise ValueError("MCP contract requires tools")
        for name, tool in tools.items():
            if tool.get("authority_enforced") is not True:
                raise ValueError(f"Authority enforcement missing for {name}")
            if not tool.get("runtime_binding"):
                raise ValueError(f"Runtime binding missing for {name}")
            if tool.get("read_only") is not True and tool.get("audit_required") is not True:
                raise ValueError(f"Consequential MCP write is not auditable: {name}")

        allowlists = self.contract.get("agent_tool_allowlists", {})
        unknown = {
            tool_name
            for allowed in allowlists.values()
            for tool_name in allowed
            if tool_name not in tools
        }
        if unknown:
            raise ValueError(f"Agent allowlists reference unknown MCP tools: {sorted(unknown)}")

    def authorize(self, agent_id: str, tool_name: str) -> dict[str, Any]:
        """Return the tool contract only when the agent is explicitly allowlisted."""

        tools = self._tools()
        allowlists = self.contract.get("agent_tool_allowlists", {})
        if agent_id not in allowlists:
            raise PermissionError(f"Unknown or unconfigured Workspace Agent: {agent_id}")
        if tool_name not in tools:
            raise PermissionError(f"Unknown MCP tool: {tool_name}")
        if tool_name not in set(allowlists[agent_id]):
            raise PermissionError(f"MCP tool not allowed for {agent_id}: {tool_name}")
        return dict(tools[tool_name])

    def allowed_tools(self, agent_id: str) -> tuple[str, ...]:
        allowlists = self.contract.get("agent_tool_allowlists", {})
        if agent_id not in allowlists:
            raise PermissionError(f"Unknown or unconfigured Workspace Agent: {agent_id}")
        return tuple(allowlists[agent_id])

    def validate_runtime_bindings(self) -> list[str]:
        """Return unresolved runtime bindings without executing business logic."""

        errors: list[str] = []
        for name, tool in self._tools().items():
            binding = str(tool["runtime_binding"])
            try:
                self._resolve_binding(binding)
            except (ImportError, AttributeError) as exc:
                errors.append(f"{name}: {binding}: {type(exc).__name__}: {exc}")
        return errors

    def _tools(self) -> dict[str, dict[str, Any]]:
        return {
            str(tool["name"]): dict(tool)
            for tool in self.contract.get("tools", [])
            if isinstance(tool, dict) and tool.get("name")
        }

    @staticmethod
    def _resolve_binding(binding: str) -> Any:
        parts = binding.split(".")
        for split_at in range(len(parts), 0, -1):
            module_name = ".".join(parts[:split_at])
            try:
                target: Any = importlib.import_module(module_name)
            except ImportError:
                continue
            for attribute in parts[split_at:]:
                target = getattr(target, attribute)
            return target
        raise ImportError(f"Cannot import runtime binding {binding}")
