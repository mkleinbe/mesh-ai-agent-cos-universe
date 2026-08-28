from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mcp_validation import load_input_schemas

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_REGISTRY = "chatgpt/mcp/tool-input-schemas.v1.json"


@dataclass(frozen=True, slots=True)
class WorkspaceAgentMCPPolicy:
    """Fail-closed policy view of the checked-in Workspace Agent MCP contract."""

    contract: dict[str, Any]

    @classmethod
    def from_file(cls, path: str | Path | None = None) -> WorkspaceAgentMCPPolicy:
        contract_path = (
            Path(path)
            if path is not None
            else ROOT / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
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
        strict_contract = self.contract.get("schema_version") == "mesh.cos.mcp-contract.v1"
        if strict_contract and self.contract.get("serialized_runtime") != "mesh_cos.mcp_runtime.MCPRuntime":
            raise ValueError("MCP contract must use the serialized MCPRuntime boundary")
        if strict_contract:
            if self.contract.get("transport") != "LOCAL_STDIO":
                raise ValueError("MCP contract must use bundled LOCAL_STDIO as the primary ChatGPT transport")
            local_runtime = self.contract.get("local_runtime")
            if not isinstance(local_runtime, dict):
                raise ValueError("MCP contract requires local_runtime configuration")
            if local_runtime.get("command") != "node":
                raise ValueError("Local MCP runtime command must be node")
            if local_runtime.get("args") != ["mcp/dist/index.js"]:
                raise ValueError("Local MCP runtime must launch mcp/dist/index.js")
            if local_runtime.get("agent_identity_env") != "MESH_COS_AGENT_ID":
                raise ValueError("Local MCP runtime must bind agent identity through MESH_COS_AGENT_ID")
            if local_runtime.get("ledger_path_env") != "MESH_COS_LEDGER_PATH":
                raise ValueError("Local MCP runtime must bind canonical persistence through MESH_COS_LEDGER_PATH")
            if local_runtime.get("python_bridge") != "mesh_cos.mcp_stdio_bridge":
                raise ValueError("Local MCP runtime must bridge to mesh_cos.mcp_stdio_bridge")
            deployment = self.contract.get("deployment", {})
            if deployment.get("chatgpt_runtime") != "BUNDLED_LOCAL_STDIO":
                raise ValueError("ChatGPT deployment must use the bundled local stdio MCP")
            if deployment.get("managed_remote") != "OPTIONAL_NOT_REQUIRED":
                raise ValueError("Managed remote MCP transport must remain optional")
            if "server_url_env" in self.contract:
                raise ValueError("Local ChatGPT MCP must not require a remote server URL")

        security = self.contract.get("security", {})
        if security.get("deny_by_default") is not True:
            raise ValueError("MCP policy must deny by default")
        if security.get("approval_fail_closed") is not True:
            raise ValueError("MCP approval policy must fail closed")
        if strict_contract and security.get("server_derived_agent_identity") is not True:
            raise ValueError("MCP agent identity must be derived server-side")
        if strict_contract and security.get("human_principal_required_for_human_tools") is not True:
            raise ValueError("Human-only MCP tools require an authenticated human principal")
        if strict_contract and security.get("client_supplied_code_execution") is not False:
            raise ValueError("Client-supplied code execution must remain disabled")

        tools = self._tools()
        if not tools:
            raise ValueError("MCP contract requires tools")
        if strict_contract:
            registry_ref = self.contract.get("input_schema_registry", DEFAULT_SCHEMA_REGISTRY)
            if not isinstance(registry_ref, str) or not registry_ref.strip():
                raise ValueError("MCP input schema registry reference must be non-empty")
            registry_path = Path(registry_ref)
            if not registry_path.is_absolute():
                registry_path = ROOT / registry_path
            try:
                input_schemas = load_input_schemas(registry_path)
            except TypeError as exc:
                raise ValueError("MCP input schema registry must exactly match the tool catalog") from exc
            except ValueError as exc:
                if "registry version" in str(exc):
                    raise ValueError("Unsupported MCP input schema registry version") from exc
                raise
            if registry_ref == DEFAULT_SCHEMA_REGISTRY:
                input_schemas = load_input_schemas()
            if set(input_schemas) != set(tools):
                raise ValueError("MCP input schema registry must exactly match the tool catalog")
            for tool_name, schema in input_schemas.items():
                if not isinstance(schema, dict) or schema.get("type") != "object":
                    raise ValueError(f"MCP input schema must be an object: {tool_name}")
                if schema.get("additionalProperties") is not False:
                    raise ValueError(f"MCP input schema must be closed: {tool_name}")
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

        if strict_contract:
            human_tools = set(self.contract.get("human_tool_allowlist", []))
            unknown_human = human_tools - set(tools)
            if unknown_human:
                raise ValueError(f"Human allowlist references unknown MCP tools: {sorted(unknown_human)}")
            if not human_tools:
                raise ValueError("Human-only MCP tools must be explicitly allowlisted")
            agent_tools = {tool_name for allowed in allowlists.values() for tool_name in allowed}
            overlap = human_tools & agent_tools
            if overlap:
                raise ValueError(f"Human-only MCP tools cannot appear in agent allowlists: {sorted(overlap)}")
            for tool_name in human_tools:
                if tools[tool_name].get("runtime_binding") != "mesh_cos.mcp_runtime.MCPRuntime.call_human":
                    raise ValueError(f"Human-only MCP tool must bind to call_human: {tool_name}")
            for tool_name in agent_tools:
                if tools[tool_name].get("runtime_binding") != "mesh_cos.mcp_runtime.MCPRuntime.call_agent":
                    raise ValueError(f"Agent MCP tool must bind to call_agent: {tool_name}")

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

    def authorize_human(self, tool_name: str) -> dict[str, Any]:
        tools = self._tools()
        if tool_name not in tools:
            raise PermissionError(f"Unknown MCP tool: {tool_name}")
        if tool_name not in set(self.contract.get("human_tool_allowlist", [])):
            raise PermissionError(f"MCP tool is not human-authorized: {tool_name}")
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
