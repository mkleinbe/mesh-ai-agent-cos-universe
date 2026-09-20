from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from . import __version__
from .ledger import TaskLedger
from .mcp_runtime import HUMAN_ONLY_TOOLS, MCPRuntime
from .mcp_validation import RequestValidationError, validate_tool_arguments
from .reliability import assert_runtime_enabled

MAX_REQUEST_BYTES = 1_000_000


def _environment(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return env if env is not None else os.environ


def _bound_agent_id(env: Mapping[str, str]) -> str:
    agent_id = str(env.get("MESH_COS_AGENT_ID", "")).strip()
    if not agent_id:
        raise PermissionError("MESH_COS_AGENT_ID is required for local MCP execution")
    return agent_id


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _ledger_target(env: Mapping[str, str]) -> str:
    value = str(env.get("MESH_COS_LEDGER_PATH", "")).strip()
    if not value:
        raise RuntimeError("MESH_COS_LEDGER_PATH is required for canonical local persistence")
    require_existing = _truthy(env.get("MESH_COS_REQUIRE_EXISTING_LEDGER"))
    if value == ":memory:":
        if require_existing:
            raise RuntimeError("Production runtime forbids in-memory TaskLedger")
        return value
    path = Path(value).expanduser()
    if require_existing:
        if not path.is_file():
            raise RuntimeError("Canonical TaskLedger is missing")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)


def _validate_request(payload: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        raise TypeError("MCP bridge request must be a JSON object")
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ValueError("tool_name is required")
    arguments = payload.get("arguments", {})
    if not isinstance(arguments, dict):
        raise TypeError("arguments must be a JSON object")
    if tool_name in HUMAN_ONLY_TOOLS:
        raise PermissionError("Human-only MCP tools are not exposed by the local agent runtime")
    return tool_name, dict(arguments)


def execute_request(
    payload: Any,
    *,
    env: Mapping[str, str] | None = None,
    runtime_factory: type[MCPRuntime] = MCPRuntime,
) -> dict[str, Any]:
    environment = _environment(env)
    assert_runtime_enabled(environment)
    agent_id = _bound_agent_id(environment)
    tool_name, arguments = _validate_request(payload)
    arguments = validate_tool_arguments(tool_name, arguments)
    ledger = TaskLedger(_ledger_target(environment))
    try:
        runtime = runtime_factory(ledger)
        result = runtime.call_agent(agent_id, tool_name, arguments)
        return {
            "ok": True,
            "runtime_version": __version__,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "result": result,
        }
    finally:
        ledger.conn.close()


def _safe_reason_code(exc: BaseException, message: str) -> str | None:
    if isinstance(exc, PermissionError):
        if "approval" in message:
            return "approval-required"
        if "delegation is not permitted" in message:
            return "delegator-not-authorized"
        if "registered direct child" in message or "delegation target" in message:
            return "recipient-not-delegable"
        if "canonical delegation depth exceeds" in message:
            return "delegation-depth-exceeded"
        if (
            "caller-supplied delegation depth" in message
            or "caller-supplied parent authority" in message
            or "caller-supplied ancestry" in message
            or "delegation parent task does not match" in message
        ):
            return "invalid-delegation-contract"
        if (
            "delegation owner must match" in message
            or "active owner" in message
            or "accountable owner mismatch" in message
        ):
            return "ownership-conflict"
        if (
            "cannot widen authority" in message
            or "delegation authority must match" in message
            or "authority exceeds" in message
        ):
            return "authority-exceeded"
        if "capability is not explicitly permitted" in message:
            return "capability-not-delegated"
    if isinstance(exc, ValueError) and "agent principal" in message:
        return "unsupported-capability-type"
    return None


def _safe_error(exc: BaseException) -> dict[str, Any]:
    details: list[dict[str, str]] | None = None
    message = str(exc).lower()
    reason_code = _safe_reason_code(exc, message)
    if isinstance(exc, RequestValidationError):
        category = "validation_failed"
        details = list(exc.details)
    elif isinstance(exc, PermissionError):
        if "approval" in message:
            category = "approval_required"
        elif "authenticated" in message or "principal" in message:
            category = "unauthorized"
        else:
            category = "forbidden"
    elif isinstance(exc, KeyError):
        category = "not_found"
    elif isinstance(exc, (json.JSONDecodeError, TypeError)):
        category = "invalid_request"
    elif isinstance(exc, ValueError):
        if (
            "mcp bridge request" in message
            or "tool_name" in message
            or "request body" in message
            or "maximum size" in message
            or "agent principal" in message
        ):
            category = "invalid_request"
        elif "current accountable owner" in message or "already decided" in message:
            category = "conflict"
        else:
            category = "invalid_state"
    elif isinstance(exc, RuntimeError):
        category = "dependency_unavailable" if "dependenc" in message or "unavailable" in message else "execution_failed"
    else:
        category = "execution_failed"
    payload: dict[str, Any] = {
        "ok": False,
        "runtime_version": __version__,
        "error": category,
    }
    if reason_code:
        payload["reason_code"] = reason_code
    if details:
        payload["details"] = details
    return payload

def _read_stdin() -> Any:
    raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    if len(raw) > MAX_REQUEST_BYTES:
        raise ValueError("MCP bridge request exceeds maximum size")
    if not raw:
        raise ValueError("MCP bridge request body is required")
    return json.loads(raw.decode("utf-8"))


def main() -> int:
    try:
        response = execute_request(_read_stdin())
    except BaseException as exc:  # noqa: BLE001 - bridge must always emit a structured fail-closed response
        response = _safe_error(exc)
    sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by MCP stdio smoke certification
    raise SystemExit(main())
