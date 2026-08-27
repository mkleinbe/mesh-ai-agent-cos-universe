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
ROOT_TS = "1787843216.789639"


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
    }


def _root_envelope(approval_id: str) -> dict:
    return {
        "envelope_id": "env-root-bridge",
        "type": "events_api",
        "payload": {
            "type": "event_callback",
            "event_id": "Ev-root-bridge",
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "app_id": "A0CHATGPT",
                "text": f"Approval ID: `{approval_id}`",
                "ts": ROOT_TS,
                "event_ts": ROOT_TS,
            },
        },
    }


def _reply_envelope() -> dict:
    return {
        "envelope_id": "env-reply-bridge",
        "type": "events_api",
        "payload": {
            "type": "event_callback",
            "event_id": "Ev-reply-bridge",
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "text": "APPROVE",
                "thread_ts": ROOT_TS,
                "ts": "1787843300.046169",
                "event_ts": "1787843300.046169",
            },
        },
    }


def test_execute_socket_envelope_round_trips_bound_thread_and_canonical_state(
    tmp_path: Path,
) -> None:
    path = tmp_path / "ledger.sqlite3"
    approval_id = _seed(path)

    binding_response = execute_socket_envelope(_root_envelope(approval_id), env=_env(path))
    assert binding_response["ok"] is True
    assert binding_response["source"] == "SLACK_SOCKET_MODE"
    binding = binding_response["result"]
    assert binding["source"] == "SLACK_SOCKET_MODE_THREAD_BINDING"
    assert binding["payload_fingerprint"] == FINGERPRINT

    response = execute_socket_envelope(_reply_envelope(), env=_env(path))
    assert response["ok"] is True
    assert response["source"] == "SLACK_SOCKET_MODE"
    result = response["result"]
    assert result["disposition"] == "APPROVE"
    assert result["source"] == "SLACK_SOCKET_MODE_THREAD_REPLY"
    assert result["provider_identity_verified"] is True
    assert result["payload_fingerprint"] == FINGERPRINT
    assert APPROVER_USER_ID not in str(result)
    ledger = TaskLedger(path)
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_record("approval_slack_thread_binding", ROOT_TS) is not None
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
        Stdin(b'{"type":"events_api"}'),
    )
    assert _read_stdin() == {"type": "events_api"}

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
