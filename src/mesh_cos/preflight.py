from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .governance import verify_audit_chain
from .ledger import TaskLedger
from .mcp_policy import WorkspaceAgentMCPPolicy
from .mcp_runtime import MCPRuntime
from .registry import load_registry

EXPECTED_AGENT_IDS = {
    "cos",
    "agentops",
    "answer-desk",
    "cro",
    "cfo",
    "coo",
    "consultant-network-steward",
    "cmo",
    "vp-content",
    "message-ops",
}


@dataclass(slots=True)
class ProductionPreflight:
    """Fail-closed repository/runtime readiness checks for a production activation.

    The result deliberately reports only configuration presence and validation state.
    It never echoes credential, token, or local state-path values.
    """

    root: Path
    env: Mapping[str, str] | None = None
    ledger: TaskLedger | None = None
    require_slack: bool = False
    require_answer_desk: bool = False

    @property
    def environment(self) -> Mapping[str, str]:
        return self.env if self.env is not None else os.environ

    @staticmethod
    def _result(name: str, passed: bool, detail: str) -> dict[str, str]:
        return {"name": name, "status": "PASS" if passed else "FAIL", "detail": detail}

    def check(self) -> dict[str, object]:
        checks: list[dict[str, str]] = []
        env = self.environment

        killed = str(env.get("MESH_COS_KILL_SWITCH", "false")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        checks.append(
            self._result(
                "kill_switch",
                not killed,
                "automation enabled" if not killed else "emergency kill switch is enabled",
            )
        )

        ledger_path_present = bool(str(env.get("MESH_COS_LEDGER_PATH", "")).strip())
        checks.append(
            self._result(
                "mcp_ledger_path",
                ledger_path_present,
                "canonical local ledger path configured"
                if ledger_path_present
                else "MESH_COS_LEDGER_PATH is missing",
            )
        )

        local_package_ok = all(
            path.is_file()
            for path in (
                self.root / "mcp" / "package.json",
                self.root / "mcp" / "src" / "index.ts",
                self.root / "mcp" / "src" / "server.ts",
                self.root / "mcp" / "src" / "python-bridge.ts",
            )
        )
        checks.append(
            self._result(
                "mcp_local_package",
                local_package_ok,
                "bundled local stdio MCP source package present"
                if local_package_ok
                else "bundled local stdio MCP package is incomplete",
            )
        )

        try:
            registry = load_registry(self.root / "agents" / "registry.json")
            agent_set_ok = set(registry) == EXPECTED_AGENT_IDS
            unsafe_health = sorted(
                agent_id
                for agent_id, record in registry.items()
                if record.get("runtime_health") in {"QUARANTINED", "RETIRED"}
            )
            registry_ok = agent_set_ok and not unsafe_health
            detail = "10 governed agents loaded with routable health"
            if not agent_set_ok:
                detail = "canonical agent set does not match the Phase 1 organization"
            elif unsafe_health:
                detail = "non-routable agent health present: " + ", ".join(unsafe_health)
        except Exception as exc:  # noqa: BLE001 - preflight converts any validation defect to fail-closed status
            registry_ok = False
            detail = f"registry validation failed: {type(exc).__name__}"
        checks.append(self._result("agent_registry", registry_ok, detail))

        contract_path = self.root / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
        try:
            policy = WorkspaceAgentMCPPolicy.from_file(contract_path)
            binding_errors = policy.validate_runtime_bindings()
            mcp_contract_ok = not binding_errors
            mcp_detail = (
                "local stdio contract valid and runtime bindings resolvable"
                if mcp_contract_ok
                else f"{len(binding_errors)} runtime binding error(s)"
            )
        except Exception as exc:  # noqa: BLE001 - preflight must report MCP defects instead of crashing
            mcp_contract_ok = False
            mcp_detail = f"MCP contract validation failed: {type(exc).__name__}"
        checks.append(self._result("mcp_contract", mcp_contract_ok, mcp_detail))

        try:
            runtime_policy = WorkspaceAgentMCPPolicy.from_file(contract_path)
            runtime = MCPRuntime(TaskLedger(), policy=runtime_policy)
            contract_tools = {
                str(tool["name"])
                for tool in runtime_policy.contract.get("tools", [])
                if isinstance(tool, dict) and tool.get("name")
            }
            runtime_tools = runtime.tool_names()
            runtime_ok = runtime_tools == contract_tools
            runtime_detail = (
                "serialized MCP runtime tool surface matches contract"
                if runtime_ok
                else "serialized MCP runtime tool surface differs from contract"
            )
        except Exception as exc:  # noqa: BLE001 - composition defects must fail preflight, not crash it
            runtime_ok = False
            runtime_detail = f"serialized MCP runtime validation failed: {type(exc).__name__}"
        checks.append(self._result("mcp_runtime", runtime_ok, runtime_detail))

        if self.require_slack:
            channel_present = bool(
                str(env.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")).strip()
            )
            checks.append(
                self._result(
                    "agent_ops_channel",
                    channel_present,
                    "configured" if channel_present else "missing channel ID",
                )
            )
            credentials_present = bool(
                str(env.get("MESH_COS_SLACK_BOT_TOKEN", "")).strip()
            ) and bool(str(env.get("MESH_COS_SLACK_SIGNING_SECRET", "")).strip())
            checks.append(
                self._result(
                    "slack_credentials",
                    credentials_present,
                    "configured" if credentials_present else "bot token and/or signing secret missing",
                )
            )

        if self.require_answer_desk:
            answer_channel_present = bool(
                str(env.get("MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID", "")).strip()
            )
            checks.append(
                self._result(
                    "answer_desk_channel",
                    answer_channel_present,
                    "configured" if answer_channel_present else "missing dedicated channel ID",
                )
            )

        if self.ledger is not None:
            audit_ok = verify_audit_chain(self.ledger.list_records("audit_event_v2"))
            checks.append(
                self._result(
                    "audit_chain",
                    audit_ok,
                    "canonical chain verified" if audit_ok else "canonical chain integrity failure",
                )
            )

        ready = all(check["status"] == "PASS" for check in checks)
        return {"ready": ready, "checks": checks}

    def assert_ready(self) -> dict[str, object]:
        result = self.check()
        if not result["ready"]:
            checks = result["checks"]
            assert isinstance(checks, list)
            failed = [
                str(check["name"])
                for check in checks
                if isinstance(check, dict) and check.get("status") == "FAIL"
            ]
            raise RuntimeError("Production preflight failed: " + ", ".join(failed))
        return result
