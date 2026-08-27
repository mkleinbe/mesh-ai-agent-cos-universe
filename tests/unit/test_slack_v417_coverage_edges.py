from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

import mesh_cos.slack_bot as slack_bot
import mesh_cos.slack_socket_approval as socket_approval
from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.approval import ApprovalService
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.slack_bot import (
    CHANGE_REQUEST_KIND,
    THREAD_BINDING_KIND,
    SlackApprovalNotifier,
    SlackBotAPI,
)
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
APP_ID = "A0TESTAPP"
FINGERPRINT = "d" * 64
ROOT_TS = "1787843216.789639"


def _pending(*, action: str | None = None) -> tuple[TaskLedger, str, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Execute one exact approved communication",
        expected_outcome="Only a provider-authenticated human interaction can authorize action",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="canonical approval and Slack provider-interaction evidence reconcile",
        idempotency_key="TEST-SOCKET-COVERAGE-001",
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
        action or f"Execute exact payload_fingerprint={FINGERPRINT}",
    )
    return ledger, task.task_id, approval.approval_id


def _config(*, app_id: str = APP_ID) -> SlackSocketApprovalConfig:
    return SlackSocketApprovalConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
        app_id=app_id,
    )


def _notifier(ledger: TaskLedger, transport: Any | None = None) -> SlackApprovalNotifier:
    if transport is None:
        def transport(method: str, payload: dict, token: str) -> dict:
            assert token == "xoxb-test"
            if method == "chat.update":
                return {"ok": True}
            return {
                "ok": True,
                "channel": CHANNEL_ID,
                "ts": ROOT_TS if "thread_ts" not in payload else "1787843300.111111",
            }
    return SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", transport), CHANNEL_ID)


def _bound(*, notifier: Any = True) -> tuple[TaskLedger, str, str, dict[str, Any], SlackSocketApprovalService]:
    ledger, task_id, approval_id = _pending()
    binding_notifier = _notifier(ledger)
    binding_notifier.post_approval(approval_id)
    binding = dict(ledger.get_record(THREAD_BINDING_KIND, ROOT_TS))
    service_notifier = binding_notifier if notifier is True else notifier
    return ledger, task_id, approval_id, binding, SlackSocketApprovalService(
        ledger,
        _config(),
        notifier=service_notifier,
    )


def _interactive(approval_id: str) -> dict[str, Any]:
    return {
        "envelope_id": "env-action",
        "type": "interactive",
        "payload": {
            "type": "block_actions",
            "api_app_id": APP_ID,
            "user": {"id": APPROVER_USER_ID},
            "channel": {"id": CHANNEL_ID},
            "container": {"channel_id": CHANNEL_ID, "message_ts": ROOT_TS},
            "actions": [
                {
                    "action_id": "mesh_approval_approve",
                    "value": approval_id,
                }
            ],
        },
    }


class _Response:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> _Response:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False

    def read(self, limit: int) -> bytes:
        assert limit == 1_000_001
        return self.body


class _FailingReplyNotifier:
    def __init__(self) -> None:
        self.marked: list[tuple[str, str]] = []

    def post_thread_reply(self, thread_ts: str, text: str) -> dict[str, Any]:
        raise RuntimeError("simulated Slack reply outage")

    def mark_resolved(self, approval_id: str, disposition: str) -> None:
        self.marked.append((approval_id, disposition))


def test_default_slack_transport_success(monkeypatch: pytest.MonkeyPatch) -> None:
    body = json.dumps({"ok": True, "ts": "1.2"}).encode()
    monkeypatch.setattr(slack_bot.urllib.request, "urlopen", lambda request, timeout: _Response(body))
    result = slack_bot._default_transport("chat.postMessage", {"channel": CHANNEL_ID}, "xoxb-test")
    assert result == {"ok": True, "ts": "1.2"}


def test_default_slack_transport_network_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(request: Any, timeout: int) -> Any:
        raise OSError("network down")

    monkeypatch.setattr(slack_bot.urllib.request, "urlopen", fail)
    with pytest.raises(RuntimeError, match="Slack Web API request failed"):
        slack_bot._default_transport("chat.postMessage", {"channel": CHANNEL_ID}, "xoxb-test")


@pytest.mark.parametrize(
    ("body", "error"),
    [
        (b"x" * 1_000_001, "response exceeded maximum size"),
        (b"{", "returned invalid JSON"),
        (json.dumps([]).encode(), "rejected the request"),
        (json.dumps({"ok": False}).encode(), "rejected the request"),
    ],
)
def test_default_slack_transport_rejects_bad_responses(
    monkeypatch: pytest.MonkeyPatch,
    body: bytes,
    error: str,
) -> None:
    monkeypatch.setattr(slack_bot.urllib.request, "urlopen", lambda request, timeout: _Response(body))
    with pytest.raises(RuntimeError, match=error):
        slack_bot._default_transport("chat.postMessage", {"channel": CHANNEL_ID}, "xoxb-test")


def test_adapter_runtime_notifier_requires_ledger_then_bootstraps_from_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    without_ledger = GovernedAdapterRegistry(load_registry(), None)
    with pytest.raises(RuntimeError, match="requires the canonical TaskLedger"):
        without_ledger.execute(
            "cos",
            "slack-adapter",
            {"operation": "list_change_requests", "channel_id": CHANNEL_ID, "payload": {}},
        )

    token_file = tmp_path / "slack-bot-token"
    token_file.write_text("xoxb-test\n", encoding="utf-8")
    monkeypatch.setenv("MESH_COS_SLACK_BOT_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    ledger = TaskLedger()
    governed = GovernedAdapterRegistry(load_registry(), GovernanceJournal(ledger))
    result = governed.execute(
        "cos",
        "slack-adapter",
        {"operation": "list_change_requests", "channel_id": CHANNEL_ID, "payload": {}},
    )
    assert result["status"] == "OK"
    assert governed.slack_notifier is not None


def test_adapter_post_message_validation_and_missing_timestamp() -> None:
    ledger = TaskLedger()
    notifier = _notifier(ledger, lambda method, payload, token: {"ok": True, "channel": CHANNEL_ID})
    registry = GovernedAdapterRegistry(
        load_registry(),
        GovernanceJournal(ledger),
        slack_notifier=notifier,
    )
    with pytest.raises(ValueError, match="Unexpected Slack collaboration payload fields: extra"):
        registry.execute(
            "cos",
            "slack-adapter",
            {
                "operation": "post_message",
                "channel_id": CHANNEL_ID,
                "payload": {"text": "hello", "extra": True},
            },
        )
    with pytest.raises(ValueError, match="message text is required"):
        registry.execute(
            "cos",
            "slack-adapter",
            {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "  "}},
        )
    with pytest.raises(RuntimeError, match="message timestamp"):
        registry.execute(
            "cos",
            "slack-adapter",
            {"operation": "post_message", "channel_id": CHANNEL_ID, "payload": {"text": "hello"}},
        )


def test_adapter_lists_and_marks_change_request_revised() -> None:
    ledger = TaskLedger()
    registry = GovernedAdapterRegistry(
        load_registry(),
        GovernanceJournal(ledger),
        slack_notifier=_notifier(ledger),
    )
    ledger.save_record(
        CHANGE_REQUEST_KIND,
        "change-1",
        {
            "change_request_id": "change-1",
            "status": "PENDING_AGENT_REVISION",
            "task_id": "task-1",
            "channel_id": CHANNEL_ID,
            "payload_fingerprint": "a" * 64,
        },
    )
    ledger.save_record(
        "approval",
        "approval-new",
        {
            "approval_id": "approval-new",
            "status": "PENDING",
            "task_id": "task-1",
            "action": f"Execute payload_fingerprint={'b' * 64}",
        },
    )
    listed = registry.execute(
        "cos",
        "slack-adapter",
        {"operation": "list_change_requests", "channel_id": CHANNEL_ID, "payload": {}},
    )
    assert [item["change_request_id"] for item in listed["change_requests"]] == ["change-1"]
    revised = registry.execute(
        "cos",
        "slack-adapter",
        {
            "operation": "mark_change_request_revised",
            "channel_id": CHANNEL_ID,
            "payload": {"change_request_id": "change-1", "new_approval_id": "approval-new"},
        },
    )
    assert revised["status"] == "REVISED"
    assert revised["new_payload_fingerprint"] == "b" * 64


def test_socket_direct_fail_closed_state_edges() -> None:
    service = SlackSocketApprovalService(TaskLedger(), _config(app_id=""))
    service._validate_app({})
    with pytest.raises(PermissionError, match="payload_fingerprint"):
        service._canonical_fingerprint({"action": "no immutable binding"})

    ledger = TaskLedger()
    ledger.save_record(
        THREAD_BINDING_KIND,
        ROOT_TS,
        {
            "thread_ts": ROOT_TS,
            "channel_id": "C0OTHER",
            "approval_id": "approval-x",
            "payload_fingerprint": FINGERPRINT,
        },
    )
    service = SlackSocketApprovalService(ledger, _config())
    with pytest.raises(PermissionError, match="binding channel mismatch"):
        service._binding(ROOT_TS)
    with pytest.raises(KeyError):
        service._require_pending_bound_approval(
            {"approval_id": "approval-missing", "payload_fingerprint": FINGERPRINT}
        )


def test_socket_rejects_decided_or_nonfinal_disposition() -> None:
    ledger, _, approval_id, binding, service = _bound(notifier=None)
    ApprovalService(ledger).decide(
        approval_id,
        actor="michael",
        approved=False,
        reason="prior decision",
    )
    with pytest.raises(ValueError, match="already decided"):
        service._require_pending_bound_approval(binding)

    _, _, _, binding2, service2 = _bound(notifier=None)
    with pytest.raises(PermissionError, match="Only APPROVE or DENY"):
        service2._finalize_decision(
            binding=binding2,
            disposition="CHANGE",
            envelope_id="env-invalid",
            provider_event_id="Ev-invalid",
        )


def test_socket_finalize_and_begin_change_without_notifier() -> None:
    ledger, _, approval_id, binding, service = _bound(notifier=None)
    decision = service._finalize_decision(
        binding=binding,
        disposition="APPROVE",
        envelope_id="env-approve",
        provider_event_id="Ev-approve",
    )
    assert decision["approval_id"] == approval_id
    assert "message_ts" not in decision
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"

    _, _, approval_id2, binding2, service2 = _bound(notifier=None)
    session = service2._begin_change(
        binding=binding2,
        envelope_id="env-change",
        provider_event_id="Ev-change",
    )
    assert session["approval_id"] == approval_id2
    assert session["prompt_delivery"] == "NOT_ATTEMPTED"


def test_begin_change_replay_and_completed_session_guards() -> None:
    ledger, _, approval_id, binding, service = _bound(notifier=None)
    awaiting = {
        "status": "AWAITING_CHANGE_INPUT",
        "approval_id": approval_id,
        "provider_event_id": "Ev-original",
    }
    ledger.save_record(socket_approval._CHANGE_SESSION_KIND, approval_id, awaiting)
    assert service._begin_change(
        binding=binding,
        envelope_id="env-repeat",
        provider_event_id="Ev-repeat",
    )["status"] == "AWAITING_CHANGE_INPUT"

    ledger2, _, approval_id2, binding2, service2 = _bound(notifier=None)
    captured = {
        "status": "CAPTURED",
        "approval_id": approval_id2,
        "provider_event_id": "Ev-captured",
    }
    ledger2.save_record(socket_approval._CHANGE_SESSION_KIND, approval_id2, captured)
    assert service2._begin_change(
        binding=binding2,
        envelope_id="env-captured",
        provider_event_id="Ev-captured",
    )["status"] == "CAPTURED"
    with pytest.raises(ValueError, match="session already completed"):
        service2._begin_change(
            binding=binding2,
            envelope_id="env-conflict",
            provider_event_id="Ev-other",
        )


def test_change_prompt_and_confirmation_failures_do_not_widen_authority() -> None:
    failing = _FailingReplyNotifier()
    ledger, _, approval_id, binding, _ = _bound(notifier=None)
    service = SlackSocketApprovalService(ledger, _config(), notifier=failing)
    session = service._begin_change(
        binding=binding,
        envelope_id="env-change",
        provider_event_id="Ev-change",
    )
    assert session["prompt_delivery"] == "FAILED"
    captured = service._capture_change_instruction(
        binding=binding,
        envelope_id="env-input",
        provider_event_id="Ev-input",
        message_ts="1787843300.222222",
        instruction="remove recipient",
    )
    assert captured["status"] == "PENDING_AGENT_REVISION"
    assert failing.marked == [(approval_id, "CHANGE REQUESTED")]


def test_capture_change_instruction_guard_edges() -> None:
    _, _, _, binding, service = _bound(notifier=None)
    with pytest.raises(PermissionError, match="not awaiting change input"):
        service._capture_change_instruction(
            binding=binding,
            envelope_id="env-input",
            provider_event_id="Ev-input",
            message_ts="1.1",
            instruction="change it",
        )

    ledger2, _, approval_id2, binding2, service2 = _bound(notifier=None)
    ledger2.save_record(
        socket_approval._CHANGE_SESSION_KIND,
        approval_id2,
        {"status": "CAPTURED", "change_request_id": "change-2"},
    )
    ledger2.save_record(
        CHANGE_REQUEST_KIND,
        "change-2",
        {"change_request_id": "change-2", "provider_event_id": "Ev-replay"},
    )
    replay = service2._capture_change_instruction(
        binding=binding2,
        envelope_id="env-replay",
        provider_event_id="Ev-replay",
        message_ts="1.2",
        instruction="ignored replay",
    )
    assert replay["change_request_id"] == "change-2"

    ledger3, _, approval_id3, binding3, service3 = _bound(notifier=None)
    ledger3.save_record(socket_approval._CHANGE_SESSION_KIND, approval_id3, {"status": "CAPTURED"})
    with pytest.raises(ValueError, match="already captured"):
        service3._capture_change_instruction(
            binding=binding3,
            envelope_id="env-missing-request",
            provider_event_id="Ev-missing-request",
            message_ts="1.3",
            instruction="change",
        )

    ledger4, _, approval_id4, binding4, service4 = _bound(notifier=None)
    ledger4.save_record(
        socket_approval._CHANGE_SESSION_KIND,
        approval_id4,
        {"status": "CAPTURED", "change_request_id": "change-4"},
    )
    ledger4.save_record(
        CHANGE_REQUEST_KIND,
        "change-4",
        {"change_request_id": "change-4", "provider_event_id": "Ev-original"},
    )
    with pytest.raises(ValueError, match="already captured"):
        service4._capture_change_instruction(
            binding=binding4,
            envelope_id="env-conflict",
            provider_event_id="Ev-other",
            message_ts="1.4",
            instruction="change",
        )

    ledger5, _, approval_id5, binding5, service5 = _bound(notifier=None)
    ledger5.save_record(socket_approval._CHANGE_SESSION_KIND, approval_id5, {"status": "INVALID"})
    with pytest.raises(ValueError, match="not accepting input"):
        service5._capture_change_instruction(
            binding=binding5,
            envelope_id="env-invalid-session",
            provider_event_id="Ev-invalid-session",
            message_ts="1.5",
            instruction="change",
        )

    ledger6, _, approval_id6, binding6, service6 = _bound(notifier=None)
    ledger6.save_record(
        socket_approval._CHANGE_SESSION_KIND,
        approval_id6,
        {"status": "AWAITING_CHANGE_INPUT"},
    )
    with pytest.raises(PermissionError, match="cannot be empty"):
        service6._capture_change_instruction(
            binding=binding6,
            envelope_id="env-empty",
            provider_event_id="Ev-empty",
            message_ts="1.6",
            instruction="   ",
        )


def test_capture_change_instruction_without_notifier() -> None:
    ledger, _, approval_id, binding, service = _bound(notifier=None)
    ledger.save_record(
        socket_approval._CHANGE_SESSION_KIND,
        approval_id,
        {"status": "AWAITING_CHANGE_INPUT"},
    )
    record = service._capture_change_instruction(
        binding=binding,
        envelope_id="env-input",
        provider_event_id="Ev-input",
        message_ts="1.7",
        instruction="change recipient",
    )
    assert record["status"] == "PENDING_AGENT_REVISION"


def test_block_action_validation_edges() -> None:
    _, _, approval_id, _, service = _bound()
    base = _interactive(approval_id)
    cases: list[tuple[dict[str, Any], str]] = []

    invalid_payload = deepcopy(base)
    invalid_payload["payload"] = "invalid"
    cases.append((invalid_payload, "interactive payload is invalid"))

    wrong_type = deepcopy(base)
    wrong_type["payload"]["type"] = "view_submission"
    cases.append((wrong_type, "not block_actions"))

    missing_user = deepcopy(base)
    missing_user["payload"]["user"] = "invalid"
    cases.append((missing_user, "user identity is missing"))

    missing_channel = deepcopy(base)
    missing_channel["payload"]["channel"] = "invalid"
    cases.append((missing_channel, "channel identity is missing"))

    wrong_channel = deepcopy(base)
    wrong_channel["payload"]["channel"]["id"] = "C0OTHER"
    cases.append((wrong_channel, "approval channel mismatch"))

    missing_container = deepcopy(base)
    missing_container["payload"]["container"] = "invalid"
    cases.append((missing_container, "container is missing"))

    wrong_container_channel = deepcopy(base)
    wrong_container_channel["payload"]["container"]["channel_id"] = "C0OTHER"
    cases.append((wrong_container_channel, "container channel mismatch"))

    actions_not_list = deepcopy(base)
    actions_not_list["payload"]["actions"] = "invalid"
    cases.append((actions_not_list, "exactly one Block Kit action"))

    actions_empty = deepcopy(base)
    actions_empty["payload"]["actions"] = []
    cases.append((actions_empty, "exactly one Block Kit action"))

    action_not_mapping = deepcopy(base)
    action_not_mapping["payload"]["actions"] = ["invalid"]
    cases.append((action_not_mapping, "exactly one Block Kit action"))

    unknown_action = deepcopy(base)
    unknown_action["payload"]["actions"][0]["action_id"] = "mesh_approval_unknown"
    cases.append((unknown_action, "not an approval control"))

    for envelope, error in cases:
        with pytest.raises(PermissionError, match=error):
            service.handle_envelope(envelope)
