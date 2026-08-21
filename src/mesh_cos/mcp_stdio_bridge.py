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
from .reliability import assert_runtime_enabled

MAX_REQUEST_BYTES = 1_000_000


def _environment(env: Mapping[str, str] | None) -> Mapping[str, str]:
    return env if env is not None else os.environ


def _bound_agent_id(env: Mapping[str, str]) -> str:
    agent_id = str(env.get("MESH_COS_AGENT_ID", "")).strip()
    if not agent_id:
        raise PermissionError("MESH_COS_AGENT_ID is required for local MCP execution")
    return agent_id


def _ledger_target(env: Mapping[str, str]) -> str:
    value = str(env.get("MESH_COS_LEDGER_PATH", "")).strip()
    if not value:
        raise RuntimeError("MESH_COS_LEDGER_PATH is required for canonical local persistence")
    if value == ":memory:":
        return value
    path = Path(value).expanduser()
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


def _safe_error(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, PermissionError):
        category = "permission_denied"
    elif isinstance(exc, KeyError):
        category = "not_found"
    elif isinstance(exc, (TypeError, ValueError)):
        category = "invalid_request"
    elif isinstance(exc, RuntimeError):
        category = "runtime_blocked"
    else:
        category = "runtime_error"
    return {
        "ok": False,
        "runtime_version": __version__,
        "error": category,
        "error_type": type(exc).__name__,
    }


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
    except BaseException as exc:  # noqa: BLE001 - bridge must emit structured fail-closed errors
        response = _safe_error(exc)
    sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by MCP stdio smoke certification
    raise SystemExit(main())
