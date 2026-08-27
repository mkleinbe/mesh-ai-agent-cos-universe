from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_socket_bridge import (
    _read_stdin,
    _safe_error,
    execute_socket_envelope,
    main,
)

CHANNEL_ID = "C0TESTAGENTOPS"
APPROVER_USER_ID = "U0TESTAPPROVER"
FINGERPRINT = "f" * 64


def _seed(path: Path) -> str:
    ledger = TaskLedger(path)
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Execute exact approved payload",
        expected_outcome="Provider interaction gates external authority",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="human-interaction evidence reconciles",
        idempotency_key="SOCKET-BRIDGE-TEST",
    )
    for target in (
        TaskStatus.TRIAGED,
        TaskStatus.PLANNED,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
    ):
        cos.advance(task.task_id, target)
    approval = ApprovalService(ledger).request(
        task.task_id,
        "cos",
        "michael",
        AuthorityLevel.L4,
        f"Execute payload_fingerprint={FINGERPRINT}",
    )
    ledger.conn.close()
    return approval.approval_id


def _env(path: Path) -> dict[str, str]:
    return {
        "MESH_COS_KILL_SWITCH": "false",
        "MESH_COS_LEDGER_PATH": str(path),
        "MESH_COS_REQUIRE_EXISTING_LEDGER": "true",
        "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
        "MESH_COS_SLACK_APPROVER_USER_ID": APPROVER_USER_ID,
        "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
        "MESH_COS_SLACK_APPROVAL_COMMAND": "/mesh-approval",
    }


def _envelope(approval_id: str) -> dict:
    return {
        "envelope_id": "env-bridge",
        "type": "slash_commands",
        "payload": {
            "channel_id": CHANNEL_ID,
            "user_id": APPROVER_USER_ID,
            "command": "/mesh-approval",
            "text": f"APPROVE {approval_id}",
            "trigger_id": "trigger-bridge",
        },
    }


def test_execute_socket_envelope_round_trips_canonical_state_without_notice_binding(
    tmp_path: Path,
) -> None:
    path = tmp_path / "ledger.sqlite3"
    approval_id = _seed(path)
    response = execute_socket_envelope(_envelope(approval_id), env=_env(path))
    assert response["ok"] is True
    assert response["source"] == "SLACK_SOCKET_MODE"
    result = response["result"]
    assert result["disposition"] == "APPROVE"
    assert result["provider_identity_verified"] is True
    assert result["payload_fingerprint"] == FINGERPRINT
    assert APPROVER_USER_ID not in str(result)
    ledger = TaskLedger(path)
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_record("approval_slack_binding", approval_id) is None
    ledger.conn.close()


def test_execute_socket_envelope_rejects_nonobject(tmp_path: Path) -> None:
    path = tmp_path / "ledger.sqlite3"
    _seed(path)
    with pytest.raises(TypeError, match="JSON object"):
        execute_socket_envelope([], env=_env(path))


@pytest.mark.parametrize(
    ("exc", "error"),
    [
        (PermissionError("denied"), "forbidden"),
        (KeyError("missing"), "not_found"),
        (TypeError("bad"), "invalid_request"),
        (ValueError("already decided"), "conflict"),
        (ValueError("bad state"), "invalid_state"),
        (RuntimeError("down"), "dependency_unavailable"),
        (Exception("boom"), "execution_failed"),
    ],
)
def test_bridge_errors_are_bounded(exc: BaseException, error: str) -> None:
    response = _safe_error(exc)
    assert response["ok"] is False
    assert response["error"] == error
    assert str(response).find(str(exc)) == -1


def test_read_stdin_rejects_empty_oversize_and_parses_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Stdin:
        def __init__(self, value: bytes):
            self.buffer = io.BytesIO(value)

    monkeypatch.setattr(
        "mesh_cos.slack_socket_bridge.sys.stdin",
        Stdin(b'{"type":"slash_commands"}'),
    )
    assert _read_stdin() == {"type": "slash_commands"}

    monkeypatch.setattr("mesh_cos.slack_socket_bridge.sys.stdin", Stdin(b""))
    with pytest.raises(ValueError, match="body is required"):
        _read_stdin()

    monkeypatch.setattr(
        "mesh_cos.slack_socket_bridge.sys.stdin",
        Stdin(b"x" * 1_000_001),
    )
    with pytest.raises(ValueError, match="maximum size"):
        _read_stdin()

    monkeypatch.setattr("mesh_cos.slack_socket_bridge.sys.stdin", Stdin(b"not-json"))
    with pytest.raises(json.JSONDecodeError):
        _read_stdin()


def test_main_writes_bounded_success_response(monkeypatch: pytest.MonkeyPatch) -> None:
    stdout = io.StringIO()
    monkeypatch.setattr(
        "mesh_cos.slack_socket_bridge._read_stdin",
        lambda: {"synthetic": True},
    )
    monkeypatch.setattr(
        "mesh_cos.slack_socket_bridge.execute_socket_envelope",
        lambda payload: {
            "ok": True,
            "runtime_version": "4.0.0",
            "source": "SLACK_SOCKET_MODE",
            "result": payload,
        },
    )
    monkeypatch.setattr("mesh_cos.slack_socket_bridge.sys.stdout", stdout)

    assert main() == 0
    assert json.loads(stdout.getvalue()) == {
        "ok": True,
        "runtime_version": "4.0.0",
        "source": "SLACK_SOCKET_MODE",
        "result": {"synthetic": True},
    }


def test_main_converts_bridge_failure_to_bounded_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = io.StringIO()

    def denied() -> dict:
        raise PermissionError("sensitive provider detail")

    monkeypatch.setattr("mesh_cos.slack_socket_bridge._read_stdin", denied)
    monkeypatch.setattr("mesh_cos.slack_socket_bridge.sys.stdout", stdout)

    assert main() == 0
    response = json.loads(stdout.getvalue())
    assert response["ok"] is False
    assert response["error"] == "forbidden"
    assert "sensitive provider detail" not in stdout.getvalue()
