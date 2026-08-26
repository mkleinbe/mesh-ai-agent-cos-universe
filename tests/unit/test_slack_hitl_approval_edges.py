from __future__ import annotations

from collections.abc import Callable

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack import SlackWebClient
from mesh_cos.slack_hitl import (
    CHATGPT_AGENTS_SLACK_USER_ID,
    CHATGPT_SLACK_USER_ID,
    SlackApprovalHITLService,
    SlackHITLConfig,
    _parse_decision,
)

CHANNEL_ID = "C0BRL4GCL3A"
APPROVER_USER_ID = "U0TESTAPPROVER"
THREAD_TS = "1788000000.000001"
FINGERPRINT = "a" * 64


def _pending_approval() -> tuple[TaskLedger, str]:
    ledger = TaskLedger()
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Send one governed Gmail draft after human approval",
        expected_outcome="One exact approved payload may be sent",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L4,
        acceptance_test="provider receipts and approval evidence reconcile",
        idempotency_key="TEST-SLACK-HITL-EDGES",
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
        f"Send Gmail draft with payload_fingerprint={FINGERPRINT}",
    )
    return ledger, approval.approval_id


def _config() -> SlackHITLConfig:
    return SlackHITLConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
        allowed_notice_author_ids=frozenset(
            {CHATGPT_SLACK_USER_ID, CHATGPT_AGENTS_SLACK_USER_ID}
        ),
    )


def _parent(approval_id: str) -> dict:
    return {
        "type": "message",
        "user": CHATGPT_AGENTS_SLACK_USER_ID,
        "ts": THREAD_TS,
        "text": (
            f"HITL APPROVAL REQUIRED\n<@{APPROVER_USER_ID}>\n"
            f"Approval ID: {approval_id}\n"
            f"Payload fingerprint: {FINGERPRINT}\n"
            "Approval owner: MK / Michael"
        ),
    }


def _client(
    messages: list[object],
    callback: Callable[[str, dict, str], dict] | None = None,
) -> SlackWebClient:
    def transport(method: str, payload: dict, token: str) -> dict:
        if callback is not None:
            return callback(method, payload, token)
        return {"ok": True, "messages": messages}

    return SlackWebClient("xoxb-provider-verifier", transport=transport)


def _bind(service: SlackApprovalHITLService, approval_id: str) -> dict:
    return service.bind_notice(
        approval_id,
        channel_id=CHANNEL_ID,
        thread_ts=THREAD_TS,
        payload_fingerprint=FINGERPRINT,
    )


def test_config_rejects_missing_or_noncanonical_identity_values() -> None:
    with pytest.raises(RuntimeError, match="channel ID"):
        SlackHITLConfig(channel_id="", approver_user_id=APPROVER_USER_ID)
    with pytest.raises(RuntimeError, match="approver user ID"):
        SlackHITLConfig(channel_id=CHANNEL_ID, approver_user_id="")
    with pytest.raises(RuntimeError, match="principal michael"):
        SlackHITLConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
            approver_principal="mk",
        )
    with pytest.raises(RuntimeError, match="At least one"):
        SlackHITLConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
            allowed_notice_author_ids=frozenset(),
        )
    with pytest.raises(RuntimeError, match="official OpenAI"):
        SlackHITLConfig(
            channel_id=CHANNEL_ID,
            approver_user_id=APPROVER_USER_ID,
            allowed_notice_author_ids=frozenset({"U0FAKECHATGPT"}),
        )


def test_config_from_process_environment_uses_safe_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", CHANNEL_ID)
    monkeypatch.setenv("MESH_COS_SLACK_APPROVER_USER_ID", APPROVER_USER_ID)
    monkeypatch.delenv("MESH_COS_SLACK_APPROVER_PRINCIPAL", raising=False)
    monkeypatch.delenv("MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS", raising=False)
    config = SlackHITLConfig.from_env()
    assert config.approver_principal == "michael"
    assert config.allowed_notice_author_ids == frozenset(
        {CHATGPT_SLACK_USER_ID, CHATGPT_AGENTS_SLACK_USER_ID}
    )


def test_parse_decision_rejects_wrong_ids_and_nonexact_commands() -> None:
    with pytest.raises(PermissionError, match="Approval ID mismatch"):
        _parse_decision("APPROVE approval-wrong", "approval-right")
    with pytest.raises(PermissionError, match="Approval ID mismatch"):
        _parse_decision("CHANGES approval-wrong: revise", "approval-right")
    with pytest.raises(PermissionError, match="not exact"):
        _parse_decision("please APPROVE approval-right", "approval-right")


def test_provider_thread_and_canonical_approval_must_exist() -> None:
    ledger, approval_id = _pending_approval()
    failed_provider = SlackApprovalHITLService(
        ledger,
        _client([], callback=lambda method, payload, token: {"ok": False, "error": "down"}),
        _config(),
    )
    with pytest.raises(RuntimeError, match="thread read failed"):
        _bind(failed_provider, approval_id)

    empty = SlackApprovalHITLService(
        ledger,
        _client([], callback=lambda method, payload, token: {"ok": True, "messages": []}),
        _config(),
    )
    with pytest.raises(PermissionError, match="did not return"):
        _bind(empty, approval_id)

    nonlist = SlackApprovalHITLService(
        ledger,
        _client([], callback=lambda method, payload, token: {"ok": True, "messages": {}}),
        _config(),
    )
    with pytest.raises(PermissionError, match="did not return"):
        _bind(nonlist, approval_id)

    unknown = SlackApprovalHITLService(ledger, _client([]), _config())
    with pytest.raises(KeyError):
        unknown.bind_notice(
            "approval-doesnotexist",
            channel_id=CHANNEL_ID,
            thread_ts=THREAD_TS,
            payload_fingerprint=FINGERPRINT,
        )


def test_bind_notice_rejects_channel_empty_fingerprint_and_wrong_owner() -> None:
    ledger, approval_id = _pending_approval()
    service = SlackApprovalHITLService(ledger, _client([_parent(approval_id)]), _config())
    with pytest.raises(PermissionError, match="channel mismatch"):
        service.bind_notice(
            approval_id,
            channel_id="C0WRONG",
            thread_ts=THREAD_TS,
            payload_fingerprint=FINGERPRINT,
        )
    with pytest.raises(PermissionError, match="fingerprint is required"):
        service.bind_notice(
            approval_id,
            channel_id=CHANNEL_ID,
            thread_ts=THREAD_TS,
            payload_fingerprint=" ",
        )

    approval = dict(ledger.get_record("approval", approval_id))
    approval["approval_owner"] = "someone-else"
    ledger.save_record("approval", approval_id, approval)
    with pytest.raises(PermissionError, match="owner is not Michael"):
        _bind(service, approval_id)


def test_bind_notice_rejects_bad_provider_parent_and_filters_nonmessages() -> None:
    ledger, approval_id = _pending_approval()
    wrong_ts = _parent(approval_id)
    wrong_ts["ts"] = "1788000000.999999"
    with pytest.raises(PermissionError, match="timestamp mismatch"):
        _bind(SlackApprovalHITLService(ledger, _client([wrong_ts]), _config()), approval_id)

    missing_user = _parent(approval_id)
    del missing_user["user"]
    with pytest.raises(PermissionError, match="missing user"):
        _bind(SlackApprovalHITLService(ledger, _client([missing_user]), _config()), approval_id)

    missing_text = _parent(approval_id)
    del missing_text["text"]
    with pytest.raises(PermissionError, match="missing text"):
        _bind(SlackApprovalHITLService(ledger, _client([missing_text]), _config()), approval_id)

    missing_binding = _parent(approval_id)
    missing_binding["text"] = f"Approval owner: MK\nApproval ID: {approval_id}"
    with pytest.raises(PermissionError, match="missing canonical approval binding"):
        _bind(SlackApprovalHITLService(ledger, _client([missing_binding]), _config()), approval_id)

    missing_owner = _parent(approval_id)
    missing_owner["text"] = (
        f"<@{APPROVER_USER_ID}>\nApproval ID: {approval_id}\n"
        f"Payload fingerprint: {FINGERPRINT}"
    )
    with pytest.raises(PermissionError, match="identify MK"):
        _bind(SlackApprovalHITLService(ledger, _client([missing_owner]), _config()), approval_id)

    good = SlackApprovalHITLService(
        ledger,
        _client([_parent(approval_id), "untrusted non-message payload"]),
        _config(),
    )
    assert _bind(good, approval_id)["approval_id"] == approval_id


def test_existing_binding_is_idempotent_but_conflicting_binding_fails() -> None:
    ledger, approval_id = _pending_approval()
    service = SlackApprovalHITLService(ledger, _client([_parent(approval_id)]), _config())
    first = _bind(service, approval_id)
    assert _bind(service, approval_id) == first

    conflict = dict(first)
    conflict["payload_fingerprint"] = "b" * 64
    ledger.save_record("approval_slack_binding", approval_id, conflict)
    with pytest.raises(RuntimeError, match="different Slack evidence"):
        _bind(service, approval_id)
