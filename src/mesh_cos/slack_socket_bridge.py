from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from typing import Any

from . import __version__
from .ledger import TaskLedger
from .mcp_stdio_bridge import MAX_REQUEST_BYTES, _ledger_target
from .reliability import assert_runtime_enabled
from .slack_bot import SlackApprovalNotifier
from .slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService


def execute_socket_envelope(
    payload: Any,
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    environment = env if env is not None else os.environ
    assert_runtime_enabled(environment)
    if not isinstance(payload, dict):
        raise TypeError("Slack Socket Mode bridge request must be a JSON object")
    ledger = TaskLedger(_ledger_target(environment))
    try:
        config = SlackSocketApprovalConfig.from_env(environment)
        notifier = SlackApprovalNotifier.from_env(ledger, environment)
        result = SlackSocketApprovalService(
            ledger,
            config,
            notifier=notifier,
        ).handle_envelope(payload)
        return {
            "ok": True,
            "runtime_version": __version__,
            "source": "SLACK_SOCKET_MODE",
            "result": result,
        }
    finally:
        ledger.conn.close()


def _safe_error(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, PermissionError):
        category = "forbidden"
    elif isinstance(exc, KeyError):
        category = "not_found"
    elif isinstance(exc, (json.JSONDecodeError, TypeError)):
        category = "invalid_request"
    elif isinstance(exc, ValueError):
        category = "conflict" if "already decided" in str(exc).lower() else "invalid_state"
    elif isinstance(exc, RuntimeError):
        category = "dependency_unavailable"
    else:
        category = "execution_failed"
    return {
        "ok": False,
        "runtime_version": __version__,
        "source": "SLACK_SOCKET_MODE",
        "error": category,
    }


def _read_stdin() -> Any:
    raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    if len(raw) > MAX_REQUEST_BYTES:
        raise ValueError("Slack Socket Mode bridge request exceeds maximum size")
    if not raw:
        raise ValueError("Slack Socket Mode bridge request body is required")
    return json.loads(raw.decode("utf-8"))


def main() -> int:
    try:
        response = execute_socket_envelope(_read_stdin())
    except BaseException as exc:  # noqa: BLE001 - trusted bridge returns only bounded errors
        response = _safe_error(exc)
    sys.stdout.write(json.dumps(response, separators=(",", ":"), sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by container/runtime acceptance
    raise SystemExit(main())
