from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from mesh_cos import mcp_stdio_bridge as bridge
from mesh_cos.mcp_runtime import MCPRuntime


def env(tmp_path: Path, *, agent_id: str = "cos") -> dict[str, str]:
    return {
        "MESH_COS_KILL_SWITCH": "false",
        "MESH_COS_AGENT_ID": agent_id,
        "MESH_COS_LEDGER_PATH": str(tmp_path / "state" / "ledger.sqlite3"),
    }


def test_bridge_requires_bound_agent_and_canonical_ledger(tmp_path: Path) -> None:
    with pytest.raises(PermissionError, match="MESH_COS_AGENT_ID"):
        bridge.execute_request({"tool_name": "task.list"}, env={"MESH_COS_LEDGER_PATH": str(tmp_path / "x.db")})
    with pytest.raises(RuntimeError, match="MESH_COS_LEDGER_PATH"):
        bridge.execute_request({"tool_name": "task.list"}, env={"MESH_COS_AGENT_ID": "cos"})


def test_production_bridge_requires_preexisting_disk_ledger(tmp_path: Path) -> None:
    values = env(tmp_path)
    values["MESH_COS_REQUIRE_EXISTING_LEDGER"] = "true"
    with pytest.raises(RuntimeError, match="missing"):
        bridge.execute_request({"tool_name": "task.list"}, env=values)
    assert not Path(values["MESH_COS_LEDGER_PATH"]).exists()

    values["MESH_COS_LEDGER_PATH"] = ":memory:"
    with pytest.raises(RuntimeError, match="in-memory"):
        bridge.execute_request({"tool_name": "task.list"}, env=values)


def test_production_bridge_accepts_existing_canonical_ledger(tmp_path: Path) -> None:
    values = env(tmp_path)
    bridge.execute_request({"tool_name": "task.list"}, env=values)
    values["MESH_COS_REQUIRE_EXISTING_LEDGER"] = "yes"
    response = bridge.execute_request({"tool_name": "task.list"}, env=values)
    assert response["ok"] is True


def test_bridge_validates_request_shape_and_blocks_human_tools(tmp_path: Path) -> None:
    values = env(tmp_path)
    with pytest.raises(TypeError, match="JSON object"):
        bridge.execute_request([], env=values)
    with pytest.raises(ValueError, match="tool_name"):
        bridge.execute_request({}, env=values)
    with pytest.raises(TypeError, match="arguments"):
        bridge.execute_request({"tool_name": "task.list", "arguments": []}, env=values)
    with pytest.raises(PermissionError, match="Human-only"):
        bridge.execute_request({"tool_name": "approval.record_decision"}, env=values)


def test_bridge_kill_switch_fails_closed_before_execution(tmp_path: Path) -> None:
    values = env(tmp_path)
    values["MESH_COS_KILL_SWITCH"] = "true"
    with pytest.raises(RuntimeError, match="kill switch"):
        bridge.execute_request({"tool_name": "task.list"}, env=values)


def test_bridge_executes_with_bound_identity_and_creates_parent_directory(tmp_path: Path) -> None:
    captured = {}

    class Runtime:
        def __init__(self, ledger):
            captured["ledger"] = ledger

        def call_agent(self, agent_id, tool_name, arguments):
            captured.update(agent_id=agent_id, tool_name=tool_name, arguments=arguments)
            return {"done": True}

    values = env(tmp_path, agent_id="cro")
    response = bridge.execute_request(
        {"tool_name": "task.list", "arguments": {"x": 1}},
        env=values,
        runtime_factory=Runtime,
    )
    assert response["ok"] is True
    assert response["agent_id"] == "cro"
    assert response["result"] == {"done": True}
    assert captured["arguments"] == {"x": 1}
    assert (tmp_path / "state").is_dir()


def test_bridge_supports_in_memory_target_for_tests() -> None:
    class Runtime:
        def __init__(self, ledger):
            self.ledger = ledger

        def call_agent(self, agent_id, tool_name, arguments):
            return len(self.ledger.list_tasks())

    response = bridge.execute_request(
        {"tool_name": "task.list"},
        env={
            "MESH_COS_KILL_SWITCH": "false",
            "MESH_COS_AGENT_ID": "cos",
            "MESH_COS_LEDGER_PATH": ":memory:",
        },
        runtime_factory=Runtime,
    )
    assert response["result"] == 0


def test_bridge_calls_real_mcp_runtime_with_canonical_policy(tmp_path: Path) -> None:
    result = bridge.execute_request(
        {"tool_name": "registry.list_agents", "arguments": {}},
        env=env(tmp_path),
        runtime_factory=MCPRuntime,
    )
    assert result["ok"] is True
    assert len(result["result"]) == 10
    assert all(record["agent_id"] != "devils-advocate" for record in result["result"])
    assert any(record["agent_id"] == "message-ops" for record in result["result"])


@pytest.mark.parametrize("removed_agent", ["devils-advocate"])
def test_bridge_rejects_removed_shared_capability_agent_identities(tmp_path: Path, removed_agent: str) -> None:
    with pytest.raises(PermissionError, match=f"Unknown or unconfigured Workspace Agent: {removed_agent}"):
        bridge.execute_request(
            {"tool_name": "registry.list_agents", "arguments": {}},
            env=env(tmp_path, agent_id=removed_agent),
            runtime_factory=MCPRuntime,
        )


@pytest.mark.parametrize(
    ("exc", "category"),
    [
        (PermissionError("secret"), "permission_denied"),
        (KeyError("secret"), "not_found"),
        (TypeError("secret"), "invalid_request"),
        (ValueError("secret"), "invalid_request"),
        (RuntimeError("secret"), "runtime_blocked"),
        (OSError("secret"), "runtime_error"),
    ],
)
def test_safe_errors_expose_category_not_exception_message(exc: BaseException, category: str) -> None:
    payload = bridge._safe_error(exc)
    assert payload["error"] == category
    assert "secret" not in json.dumps(payload)


def test_read_stdin_validates_empty_invalid_and_oversize(monkeypatch: pytest.MonkeyPatch) -> None:
    class Input:
        def __init__(self, value: bytes):
            self.buffer = io.BytesIO(value)

    monkeypatch.setattr(bridge.sys, "stdin", Input(b""))
    with pytest.raises(ValueError, match="required"):
        bridge._read_stdin()

    monkeypatch.setattr(bridge.sys, "stdin", Input(b"{"))
    with pytest.raises(json.JSONDecodeError):
        bridge._read_stdin()

    monkeypatch.setattr(bridge.sys, "stdin", Input(b"x" * (bridge.MAX_REQUEST_BYTES + 1)))
    with pytest.raises(ValueError, match="maximum size"):
        bridge._read_stdin()


def test_main_serializes_success_and_safe_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    out = io.StringIO()
    monkeypatch.setattr(bridge.sys, "stdout", out)
    monkeypatch.setattr(bridge, "_read_stdin", lambda: {"tool_name": "task.list"})
    monkeypatch.setattr(bridge, "execute_request", lambda payload: {"ok": True, "result": []})
    assert bridge.main() == 0
    assert json.loads(out.getvalue())["ok"] is True

    out = io.StringIO()
    monkeypatch.setattr(bridge.sys, "stdout", out)
    monkeypatch.setattr(bridge, "_read_stdin", lambda: (_ for _ in ()).throw(ValueError("do-not-leak")))
    assert bridge.main() == 0
    value = json.loads(out.getvalue())
    assert value["error"] == "invalid_request"
    assert "do-not-leak" not in out.getvalue()
