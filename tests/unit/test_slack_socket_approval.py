from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

CHANNEL_ID = "C0TESTAGENTOPS"
APPROVER_USER_ID = "U0TESTAPPROVER"
APP_ID = "A0TESTAPP"
FINGERPRINT = "d" * 64
ROOT_TS = "1787843216.789639"


def _pending(*, action: str | None = None) -> tuple[TaskLedger, str, str]:
    ledger = TaskLedger(); cos = ChiefOfStaffService(ledger)
    task = cos.intake(objective="Execute one exact approved communication", expected_outcome="Only a provider-authenticated human interaction can authorize action", requested_by="cos", executive_sponsor="michael", accountable_agent="cos", decision_owner="michael", authority_level=AuthorityLevel.L4, acceptance_test="canonical approval and Slack provider-interaction evidence reconcile", idempotency_key="TEST-SOCKET-HITL-001")
    for target in (TaskStatus.TRIAGED, TaskStatus.PLANNED, TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS): cos.advance(task.task_id, target)
    approval = ApprovalService(ledger).request(task.task_id, "cos", "michael", AuthorityLevel.L4, action or f"Execute exact payload_fingerprint={FINGERPRINT}")
    return ledger, task.task_id, approval.approval_id


def _config() -> SlackSocketApprovalConfig:
    return SlackSocketApprovalConfig(channel_id=CHANNEL_ID, approver_user_id=APPROVER_USER_ID, approver_principal="michael", app_id=APP_ID)


def _notifier(ledger: TaskLedger) -> SlackApprovalNotifier:
    def transport(method: str, payload: dict, token: str) -> dict:
        assert token == "xoxb-test"
        return {"ok": True, "channel": CHANNEL_ID, "ts": ROOT_TS if "thread_ts" not in payload else "1787843300.111111"}
    return SlackApprovalNotifier(ledger, SlackBotAPI("xoxb-test", transport), CHANNEL_ID)


def _bound(*, action: str | None = None) -> tuple[TaskLedger, str, str, SlackSocketApprovalService]:
    ledger, task_id, approval_id = _pending(action=action); notifier = _notifier(ledger); notifier.post_approval(approval_id)
    return ledger, task_id, approval_id, SlackSocketApprovalService(ledger, _config(), notifier=notifier)


def _reply(text: str, *, envelope_id: str = "env-reply", event_id: str = "Ev-reply", thread_ts: str = ROOT_TS, ts: str = "1787843300.046169") -> dict:
    return {"envelope_id": envelope_id, "type": "events_api", "payload": {"type": "event_callback", "api_app_id": APP_ID, "event_id": event_id, "event": {"type": "message", "channel": CHANNEL_ID, "user": APPROVER_USER_ID, "text": text, "thread_ts": thread_ts, "ts": ts, "event_ts": ts}}}


def test_root_or_unthreaded_message_is_non_authoritative() -> None:
    ledger, _, approval_id, service = _bound(); root = _reply("APPROVE"); root["payload"]["event"].pop("thread_ts")
    assert service.handle_envelope(root)["status"] == "IGNORED"; assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_manual_thread_approve_records_canonical_human_approval_idempotently() -> None:
    ledger, task_id, approval_id, service = _bound(); decision = service.handle_envelope(_reply("approve")); replay = service.handle_envelope(_reply("APPROVE"))
    assert replay == decision; assert decision["version"] == "mesh.cos.slack-human-decision.v5"; assert decision["source"] == "SLACK_SOCKET_MODE_HUMAN_INTERACTION"; assert decision["disposition"] == "APPROVE"; assert decision["canonical_principal"] == "michael"; assert decision["provider_identity_verified"] is True; assert decision["payload_fingerprint"] == FINGERPRINT; assert APPROVER_USER_ID not in str(decision); assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"; assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION


@pytest.mark.parametrize("reply", ["DENY", "reject"])
def test_deny_is_provider_authenticated_human_decision(reply: str) -> None:
    ledger, task_id, approval_id, service = _bound(); decision = service.handle_envelope(_reply(reply)); assert decision["disposition"] == "DENY"; assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"; assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS


def test_change_starts_session_without_direct_execution_authority() -> None:
    ledger, task_id, approval_id, service = _bound(); session = service.handle_envelope(_reply("CHANGE")); assert session["status"] == "AWAITING_CHANGE_INPUT"; assert ledger.get_record("approval", approval_id)["status"] == "PENDING"
    instruction = service.handle_envelope(_reply("remove recipient", envelope_id="env-change", event_id="Ev-change")); assert instruction["status"] == "PENDING_AGENT_REVISION"; assert instruction["change_instruction"] == "remove recipient"; assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"; assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS


def test_app_or_bot_authored_and_subtyped_replies_fail_closed() -> None:
    for field, value, error in (("app_id", "A0CHATGPT", "app-authored"), ("bot_id", "B0BOT", "app-authored"), ("bot_profile", {"id": "B0BOT"}, "app-authored"), ("subtype", "bot_message", "subtype")):
        ledger, _, approval_id, service = _bound(); envelope = _reply("APPROVE"); envelope["payload"]["event"][field] = value
        with pytest.raises(PermissionError, match=error): service.handle_envelope(envelope)
        assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_wrong_user_channel_unbound_thread_and_unknown_reply_fail_closed() -> None:
    ledger, _, _ = _pending(); service = SlackSocketApprovalService(ledger, _config())
    with pytest.raises(PermissionError, match="bound"): service.handle_envelope(_reply("APPROVE"))
    ledger, _, approval_id, service = _bound(); wrong_user = _reply("APPROVE"); wrong_user["payload"]["event"]["user"] = "U0OTHER"
    with pytest.raises(PermissionError, match="configured approver"): service.handle_envelope(wrong_user)
    wrong_channel = _reply("APPROVE"); wrong_channel["payload"]["event"]["channel"] = "C0OTHER"
    with pytest.raises(PermissionError, match="channel"): service.handle_envelope(wrong_channel)
    with pytest.raises(PermissionError, match="APPROVE, DENY, or CHANGE"): service.handle_envelope(_reply("looks good"))
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_second_distinct_provider_event_cannot_redecide_an_approval() -> None:
    _, _, _, service = _bound(); service.handle_envelope(_reply("APPROVE"))
    with pytest.raises(ValueError, match="different provider interaction"): service.handle_envelope(_reply("DENY", envelope_id="env-second", event_id="Ev-second"))


def test_config_reads_protected_approver_identity_file_without_slash_command(tmp_path: Path) -> None:
    approver_file = tmp_path / "approver-id"; approver_file.write_text(APPROVER_USER_ID + "\n", encoding="utf-8")
    assert SlackSocketApprovalConfig.from_env({"MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID, "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(approver_file), "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael", "MESH_COS_SLACK_APP_ID": APP_ID}) == _config()


@pytest.mark.parametrize(("kwargs", "error"), [({"channel_id": "", "approver_user_id": APPROVER_USER_ID}, "channel ID"), ({"channel_id": CHANNEL_ID, "approver_user_id": ""}, "user ID"), ({"channel_id": CHANNEL_ID, "approver_user_id": APPROVER_USER_ID, "approver_principal": "not-michael"}, "principal"), ({"channel_id": CHANNEL_ID, "approver_user_id": APPROVER_USER_ID, "app_id": "bad"}, "app ID")])
def test_socket_config_rejects_missing_or_widened_human_identity(kwargs: dict, error: str) -> None:
    with pytest.raises(RuntimeError, match=error): SlackSocketApprovalConfig(**kwargs)


def test_provider_envelope_validation_is_strict_and_bounded() -> None:
    _, _, _, service = _bound(); cases = []
    wrong_type = _reply("APPROVE"); wrong_type["type"] = "slash_commands"; cases.append((wrong_type, "events_api or interactive"))
    missing_envelope = _reply("APPROVE"); missing_envelope.pop("envelope_id"); cases.append((missing_envelope, "envelope_id"))
    invalid_payload = _reply("APPROVE"); invalid_payload["payload"] = "invalid"; cases.append((invalid_payload, "payload is invalid"))
    wrong_callback = _reply("APPROVE"); wrong_callback["payload"]["type"] = "url_verification"; cases.append((wrong_callback, "event_callback"))
    missing_event_id = _reply("APPROVE"); missing_event_id["payload"].pop("event_id"); cases.append((missing_event_id, "event_id"))
    invalid_event = _reply("APPROVE"); invalid_event["payload"]["event"] = "invalid"; cases.append((invalid_event, "event payload is invalid"))
    wrong_event_type = _reply("APPROVE"); wrong_event_type["payload"]["event"]["type"] = "reaction_added"; cases.append((wrong_event_type, "message events only"))
    missing_channel = _reply("APPROVE"); missing_channel["payload"]["event"].pop("channel"); cases.append((missing_channel, "channel"))
    for envelope, error in cases:
        with pytest.raises(PermissionError, match=error): service.handle_envelope(envelope)


def test_binding_revalidates_canonical_state() -> None:
    ledger, _, _, service = _bound(); binding = dict(ledger.get_record("approval_slack_thread_binding", ROOT_TS)); binding["approval_id"] = ""; ledger.save_record("approval_slack_thread_binding", ROOT_TS, binding)
    with pytest.raises(PermissionError, match="binding is invalid"): service.handle_envelope(_reply("APPROVE"))
    ledger2, _, approval_id2, service2 = _bound(); approval = dict(ledger2.get_record("approval", approval_id2)); approval["approval_owner"] = "other"; ledger2.save_record("approval", approval_id2, approval)
    with pytest.raises(PermissionError, match="owner"): service2.handle_envelope(_reply("APPROVE"))
    ledger3, _, _, service3 = _bound(); binding3 = dict(ledger3.get_record("approval_slack_thread_binding", ROOT_TS)); binding3["payload_fingerprint"] = "0" * 64; ledger3.save_record("approval_slack_thread_binding", ROOT_TS, binding3)
    with pytest.raises(PermissionError, match="fingerprint changed"): service3.handle_envelope(_reply("APPROVE"))


def test_bot_binding_requires_pending_michael_owned_fingerprinted_approval() -> None:
    ledger, _, approval_id = _pending(action="No immutable binding")
    with pytest.raises(PermissionError, match="payload_fingerprint"): _notifier(ledger).post_approval(approval_id)
    ledger2, _, approval_id2 = _pending(); approval2 = dict(ledger2.get_record("approval", approval_id2)); approval2["approval_owner"] = "other"; ledger2.save_record("approval", approval_id2, approval2)
    with pytest.raises(PermissionError, match="owner"): _notifier(ledger2).post_approval(approval_id2)
    ledger3, _, approval_id3 = _pending(); ApprovalService(ledger3).decide(approval_id3, actor="michael", approved=False, reason="prior decision")
    with pytest.raises(ValueError, match="not pending"): _notifier(ledger3).post_approval(approval_id3)
