#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import shutil
import sqlite3
import sys
import time
from pathlib import Path

from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime


def check(condition: bool, code: str, detail: str, failures: list[dict[str, str]]) -> None:
    if not condition:
        failures.append({"code": code, "detail": detail})


def main() -> int:
    failures: list[dict[str, str]] = []
    agent_id = os.environ.get("MESH_COS_AGENT_ID", "").strip()
    ledger_value = os.environ.get("MESH_COS_LEDGER_PATH", "").strip()
    expected_arch = os.environ.get("MESH_EXPECTED_ARCH", "amd64").strip()
    auth_mode = os.environ.get("MCP_AUTH_MODE", "").strip()
    min_free = int(os.environ.get("MESH_MIN_FREE_BYTES", str(1_073_741_824)))

    detected = platform.machine().lower()
    normalized = "amd64" if detected in {"x86_64", "amd64"} else "arm64" if detected in {"aarch64", "arm64"} else detected
    check(normalized == expected_arch, "architecture_mismatch", f"expected {expected_arch}, detected {normalized}", failures)
    check(os.geteuid() != 0, "root_runtime", "production process must not run as root", failures)
    check(agent_id == "cos", "identity_mismatch", "MESH_COS_AGENT_ID must be cos", failures)
    check(auth_mode == "tunnel", "auth_mode_invalid", "QNAP candidate permits MCP_AUTH_MODE=tunnel only", failures)
    check(time.time() > 1_735_689_600, "system_time_invalid", "system clock is not sane", failures)
    check(not Path("/var/run/docker.sock").exists(), "docker_socket_visible", "Docker socket must not be mounted", failures)

    if ledger_value:
        ledger_path = Path(ledger_value)
        check(ledger_path.is_file(), "ledger_missing", "canonical SQLite ledger must pre-exist", failures)
        if ledger_path.is_file():
            check(os.access(ledger_path, os.R_OK | os.W_OK), "ledger_permissions", "ledger must be readable and writable by runtime UID/GID", failures)
            try:
                free = shutil.disk_usage(ledger_path.parent).free
                check(free >= min_free, "disk_space_low", f"free bytes {free} below threshold {min_free}", failures)
            except OSError:
                failures.append({"code": "disk_space_unavailable", "detail": "unable to inspect ledger filesystem"})
            try:
                conn = sqlite3.connect(f"file:{ledger_path}?mode=rw", uri=True)
                integrity = conn.execute("PRAGMA integrity_check").fetchone()
                conn.close()
                check(bool(integrity) and integrity[0] == "ok", "sqlite_integrity", "SQLite integrity_check did not return ok", failures)
            except sqlite3.Error:
                failures.append({"code": "sqlite_open_failed", "detail": "canonical ledger could not be opened read/write"})
            if not failures:
                ledger = TaskLedger(str(ledger_path))
                try:
                    runtime = MCPRuntime(ledger)
                    record = runtime.call_agent("cos", "registry.get_agent", {"agent_id": "cos"})
                    check(record.get("status") == "ACTIVE", "registry_identity", "canonical registry does not show cos ACTIVE", failures)
                    runtime.call_agent("cos", "governance.verify_audit_chain", {})
                except Exception as exc:  # noqa: BLE001 - output deliberately suppresses raw exception details
                    failures.append({"code": "canonical_runtime_failed", "detail": type(exc).__name__})
                finally:
                    ledger.conn.close()
    else:
        failures.append({"code": "ledger_path_missing", "detail": "MESH_COS_LEDGER_PATH is required"})

    result = {"ok": not failures, "agent_id": agent_id or None, "architecture": normalized, "auth_mode": auth_mode or None, "failures": failures}
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
