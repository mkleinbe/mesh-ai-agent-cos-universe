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
from .slack_hitl import DEFAULT_ALLOWED_NOTICE_AUTHORS, SlackHITLConfig
from .slack_socket_approval import DEFAULT_APPROVAL_COMMAND

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


def _protected_file_matches(path_value: str, prefix: str) -> bool:
    if not path_value:
        return False
    path = Path(path_value).expanduser()
    try:
        return path.is_file() and path.read_text(encoding="utf-8").strip().startswith(prefix)
    except OSError:
        return False


@dataclass(slots=True)
class ProductionPreflight:
    """Fail-closed repository/runtime readiness checks for a production activation.

    Results report configuration presence and validation state only. Credentials,
    personal Slack IDs, and local state paths are never echoed.
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
                self.root / "mcp" / "src" / "slack-socket-mode.ts",
            )
        )
        checks.append(
            self._result(
                "mcp_local_package",
                local_package_ok,
                "bundled local MCP and Slack Socket Mode source package present"
                if local_package_ok
                else "bundled local MCP package is incomplete",
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
        except Exception as exc:  # noqa: BLE001
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
        except Exception as exc:  # noqa: BLE001
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
        except Exception as exc:  # noqa: BLE001
            runtime_ok = False
            runtime_detail = f"serialized MCP runtime validation failed: {type(exc).__name__}"
        checks.append(self._result("mcp_runtime", runtime_ok, runtime_detail))

        if self.require_slack:
            channel = str(env.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")).strip()
            checks.append(
                self._result(
                    "agent_ops_channel",
                    channel == "C0BRL4GCL3A",
                    "governed agent-operations channel configured"
                    if channel == "C0BRL4GCL3A"
                    else "governed agent-operations channel missing or mismatched",
                )
            )

            try:
                slack_config = SlackHITLConfig.from_env(env)
                identity_ok = (
                    bool(slack_config.approver_user_id)
                    and slack_config.approver_principal == "michael"
                )
                authors_ok = slack_config.allowed_notice_author_ids == DEFAULT_ALLOWED_NOTICE_AUTHORS
            except RuntimeError:
                identity_ok = False
                authors_ok = False
            checks.append(
                self._result(
                    "slack_approver_identity",
                    identity_ok,
                    "protected Slack identity maps to canonical principal michael"
                    if identity_ok
                    else "Slack approver identity binding is missing or invalid",
                )
            )
            checks.append(
                self._result(
                    "slack_notice_authors",
                    authors_ok,
                    "official OpenAI Slack notice identities configured"
                    if authors_ok
                    else "official OpenAI Slack notice identity set is invalid",
                )
            )

            verifier_path = str(env.get("MESH_COS_SLACK_VERIFIER_TOKEN_FILE", "")).strip()
            verifier_ok = _protected_file_matches(verifier_path, "xoxb-")
            checks.append(
                self._result(
                    "slack_verifier_credential",
                    verifier_ok,
                    "provider-verifier bot credential file is mounted"
                    if verifier_ok
                    else "provider-verifier credential file is missing or invalid",
                )
            )

            socket_path = str(env.get("MESH_COS_SLACK_SOCKET_APP_TOKEN_FILE", "")).strip()
            socket_ok = _protected_file_matches(socket_path, "xapp-")
            checks.append(
                self._result(
                    "slack_socket_app_credential",
                    socket_ok,
                    "Socket Mode app-level credential file is mounted"
                    if socket_ok
                    else "Socket Mode app-level credential file is missing or invalid",
                )
            )
            command = str(env.get("MESH_COS_SLACK_APPROVAL_COMMAND", "")).strip()
            checks.append(
                self._result(
                    "slack_approval_command",
                    command == DEFAULT_APPROVAL_COMMAND,
                    "dedicated approval slash command configured"
                    if command == DEFAULT_APPROVAL_COMMAND
                    else "approval slash command is missing or mismatched",
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
