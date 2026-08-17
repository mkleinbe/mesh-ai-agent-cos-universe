from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse

from .governance import verify_audit_chain
from .ledger import TaskLedger
from .mcp_policy import WorkspaceAgentMCPPolicy
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
    "devils-advocate",
    "message-ops",
}


@dataclass(slots=True)
class ProductionPreflight:
    """Fail-closed repository/runtime readiness checks for a production activation.

    The result deliberately reports only configuration presence and validation state.
    It never echoes credential or token values.
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

        mcp_url = str(env.get("MESH_COS_MCP_SERVER_URL", "")).strip()
        parsed = urlparse(mcp_url)
        valid_mcp_url = parsed.scheme == "https" and bool(parsed.netloc)
        checks.append(
            self._result(
                "mcp_server_url",
                valid_mcp_url,
                "configured HTTPS endpoint" if valid_mcp_url else "missing or non-HTTPS endpoint",
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
            detail = "11 governed agents loaded with routable health"
            if not agent_set_ok:
                detail = "canonical agent set does not match the Phase 1 organization"
            elif unsafe_health:
                detail = "non-routable agent health present: " + ", ".join(unsafe_health)
        except Exception as exc:
            registry_ok = False
            detail = f"registry validation failed: {type(exc).__name__}"
        checks.append(self._result("agent_registry", registry_ok, detail))

        try:
            policy = WorkspaceAgentMCPPolicy.from_file(
                self.root / "chatgpt" / "mcp" / "mesh-cos-mcp.v1.json"
            )
            binding_errors = policy.validate_runtime_bindings()
            mcp_contract_ok = not binding_errors
            mcp_detail = (
                "contract valid and runtime bindings resolvable"
                if mcp_contract_ok
                else f"{len(binding_errors)} runtime binding error(s)"
            )
        except Exception as exc:
            mcp_contract_ok = False
            mcp_detail = f"MCP contract validation failed: {type(exc).__name__}"
        checks.append(self._result("mcp_contract", mcp_contract_ok, mcp_detail))

        if self.require_slack:
            channel_present = bool(str(env.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")).strip())
            checks.append(
                self._result(
                    "agent_ops_channel",
                    channel_present,
                    "configured" if channel_present else "missing channel ID",
                )
            )
            credentials_present = bool(str(env.get("MESH_COS_SLACK_BOT_TOKEN", "")).strip()) and bool(
                str(env.get("MESH_COS_SLACK_SIGNING_SECRET", "")).strip()
            )
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
