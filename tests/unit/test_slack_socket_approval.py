from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_socket_approval import (
    SlackSocketApprovalConfig,
    SlackSocketApprovalService,
)

CHANNEL_ID = "C0TESTAGENTOPS"
APPROVER_USER_ID = "U0TESTAPPROVER"
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
        idempotency_key="TEST-SOCKET-HITL-001",
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


def _config() -> SlackSocketApprovalConfig:
    return SlackSocketApprovalConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
    )


def _root(
    approval_id: str,
    *,
    envelope_id: str = "env-root",
    event_id: str = "Ev-root",
    ts: str = ROOT_TS,
    text: str | None = None,
) -> dict:
    return {
        "envelope_id": envelope_id,
        "type": "events_api",
        "payload": {
            "type": "event_callback",
            "event_id": event_id,
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "app_id": "A0CHATGPT",
                "text": text or f"Synthetic approval\nApproval ID: `{approval_id}`",
                "ts": ts,
                "event_ts": ts,
            },
        },
    }


def _reply(
    text: str,
    *,
    envelope_id: str = "env-reply",
    event_id: str = "Ev-reply",
    thread_ts: str = ROOT_TS,
    ts: str = "1787843300.046169",
) -> dict:
    return {
        "envelope_id": envelope_id,
        "type": "events_api",
        "payload": {
            "type": "event_callback",
            "event_id": event_id,
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "text": text,
                "thread_ts": thread_ts,
                "ts": ts,
                "event_ts": ts,
            },
        },
    }


def test_root_notice_binds_thread_without_deciding_and_is_idempotent() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    binding = service.handle_envelope(_root(approval_id))
    replay = service.handle_envelope(_root(approval_id, envelope_id="env-root-2"))

    assert replay == binding
    assert binding["version"] == "mesh.cos.slack-thread-binding.v1"
    assert binding["source"] == "SLACK_SOCKET_MODE_THREAD_BINDING"
    assert binding["approval_id"] == approval_id
    assert binding["thread_ts"] == ROOT_TS
    assert binding["payload_fingerprint"] == FINGERPRINT
    assert APPROVER_USER_ID not in str(binding)
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_non_approval_root_message_is_ignored_without_state_change() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    result = service.handle_envelope(_root(approval_id, text="ordinary collaboration"))

    assert result["status"] == "IGNORED"
    assert ledger.list_records("approval_slack_thread_binding") == []
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_manual_thread_approve_records_canonical_human_approval_idempotently() -> None:
    ledger, task_id, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))

    decision = service.handle_envelope(_reply("approve"))
    replay = service.handle_envelope(_reply("APPROVE"))

    assert replay == decision
    assert decision["version"] == "mesh.cos.slack-human-decision.v4"
    assert decision["source"] == "SLACK_SOCKET_MODE_THREAD_REPLY"
    assert decision["disposition"] == "APPROVE"
    assert decision["canonical_principal"] == "michael"
    assert decision["provider_identity_verified"] is True
    assert decision["payload_fingerprint"] == FINGERPRINT
    assert decision["thread_ts"] == ROOT_TS
    assert APPROVER_USER_ID not in str(decision)
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_record("approval", approval_id)["decided_by"] == "michael"
    assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION


@pytest.mark.parametrize(
    ("reply", "disposition", "change"),
    [
        ("DENY", "DENY", None),
        ("reject", "DENY", None),
        ("CHANGE", "CHANGE", None),
        ("changes: remove recipient", "CHANGE", "remove recipient"),
    ],
)
def test_deny_and_change_are_provider_authenticated_human_decisions(
    reply: str,
    disposition: str,
    change: str | None,
) -> None:
    ledger, task_id, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))

    decision = service.handle_envelope(_reply(reply))

    assert decision["disposition"] == disposition
    assert decision["requested_change"] == change
    assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS
    if change:
        assert change in ledger.get_record("approval", approval_id)["decision_reason"]


def test_app_or_bot_authored_and_subtyped_replies_fail_closed() -> None:
    for field, value, error in (
        ("app_id", "A0CHATGPT", "app-authored"),
        ("bot_id", "B0BOT", "app-authored"),
        ("bot_profile", {"id": "B0BOT"}, "app-authored"),
        ("subtype", "bot_message", "subtype"),
    ):
        ledger, _, approval_id = _pending()
        service = SlackSocketApprovalService(ledger, _config())
        service.handle_envelope(_root(approval_id))
        envelope = _reply("APPROVE")
        envelope["payload"]["event"][field] = value
        with pytest.raises(PermissionError, match=error):
            service.handle_envelope(envelope)
        assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_wrong_user_channel_unbound_thread_and_unknown_reply_fail_closed() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    with pytest.raises(PermissionError, match="bound"):
        service.handle_envelope(_reply("APPROVE"))

    service.handle_envelope(_root(approval_id))
    wrong_user = _reply("APPROVE")
    wrong_user["payload"]["event"]["user"] = "U0OTHER"
    with pytest.raises(PermissionError, match="configured approver"):
        service.handle_envelope(wrong_user)

    wrong_channel = _reply("APPROVE")
    wrong_channel["payload"]["event"]["channel"] = "C0OTHER"
    with pytest.raises(PermissionError, match="channel"):
        service.handle_envelope(wrong_channel)

    with pytest.raises(PermissionError, match="APPROVE, DENY, or CHANGE"):
        service.handle_envelope(_reply("looks good"))


def test_second_distinct_provider_event_cannot_redecide_an_approval() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))
    service.handle_envelope(_reply("APPROVE"))

    with pytest.raises(ValueError, match="different provider interaction"):
        service.handle_envelope(
            _reply("DENY", envelope_id="env-second", event_id="Ev-second")
        )


def test_config_reads_protected_approver_identity_file_without_slash_command(tmp_path: Path) -> None:
    approver_file = tmp_path / "approver-id"
    approver_file.write_text(APPROVER_USER_ID + "\n", encoding="utf-8")
    config = SlackSocketApprovalConfig.from_env(
        {
            "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
            "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(approver_file),
            "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
        }
    )
    assert config == _config()


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"channel_id": "", "approver_user_id": APPROVER_USER_ID}, "channel ID"),
        ({"channel_id": CHANNEL_ID, "approver_user_id": ""}, "user ID"),
        (
            {
                "channel_id": CHANNEL_ID,
                "approver_user_id": APPROVER_USER_ID,
                "approver_principal": "not-michael",
            },
            "principal",
        ),
    ],
)
def test_socket_config_rejects_missing_or_widened_human_identity(kwargs: dict, error: str) -> None:
    with pytest.raises(RuntimeError, match=error):
        SlackSocketApprovalConfig(**kwargs)


def test_provider_envelope_validation_is_strict_and_bounded() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    cases = []
    wrong_type = _root(approval_id)
    wrong_type["type"] = "slash_commands"
    cases.append((wrong_type, "events_api"))

    missing_envelope = _root(approval_id)
    missing_envelope.pop("envelope_id")
    cases.append((missing_envelope, "envelope_id"))

    invalid_payload = _root(approval_id)
    invalid_payload["payload"] = "invalid"
    cases.append((invalid_payload, "payload is invalid"))

    wrong_callback = _root(approval_id)
    wrong_callback["payload"]["type"] = "url_verification"
    cases.append((wrong_callback, "event_callback"))

    missing_event_id = _root(approval_id)
    missing_event_id["payload"].pop("event_id")
    cases.append((missing_event_id, "event_id"))

    invalid_event = _root(approval_id)
    invalid_event["payload"]["event"] = "invalid"
    cases.append((invalid_event, "event payload is invalid"))

    wrong_event_type = _root(approval_id)
    wrong_event_type["payload"]["event"]["type"] = "reaction_added"
    cases.append((wrong_event_type, "message events only"))

    missing_channel = _root(approval_id)
    missing_channel["payload"]["event"].pop("channel")
    cases.append((missing_channel, "channel"))

    for envelope, error in cases:
        with pytest.raises(PermissionError, match=error):
            service.handle_envelope(envelope)


def test_root_binding_rejects_ambiguity_conflicts_and_invalid_canonical_state() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    with pytest.raises(PermissionError, match="ambiguous"):
        service.handle_envelope(
            _root(
                approval_id,
                text=f"Approval ID: {approval_id} Approval ID: approval-other",
            )
        )

    with pytest.raises(KeyError):
        service.handle_envelope(_root("approval-unknown"))

    binding = service.handle_envelope(_root(approval_id))
    assert binding["approval_id"] == approval_id

    ledger2, _, approval_id2 = _pending()
    service2 = SlackSocketApprovalService(ledger2, _config())
    ledger2.save_record(
        "approval_slack_thread_binding",
        ROOT_TS,
        {"approval_id": "approval-other", "thread_ts": ROOT_TS},
    )
    with pytest.raises(ValueError, match="another approval"):
        service2.handle_envelope(_root(approval_id2))

    ledger3, _, approval_id3 = _pending()
    service3 = SlackSocketApprovalService(ledger3, _config())
    ledger3.save_record(
        "approval_slack_thread_binding",
        "different-thread",
        {"approval_id": approval_id3, "thread_ts": "different-thread"},
    )
    with pytest.raises(ValueError, match="another Slack thread"):
        service3.handle_envelope(_root(approval_id3))


def test_root_binding_requires_pending_michael_owned_fingerprinted_approval() -> None:
    ledger, _, approval_id = _pending(action="No immutable binding")
    service = SlackSocketApprovalService(ledger, _config())
    with pytest.raises(PermissionError, match="payload_fingerprint"):
        service.handle_envelope(_root(approval_id))

    ledger2, _, approval_id2 = _pending()
    approval2 = dict(ledger2.get_record("approval", approval_id2))
    approval2["approval_owner"] = "other"
    ledger2.save_record("approval", approval_id2, approval2)
    with pytest.raises(PermissionError, match="owner"):
        SlackSocketApprovalService(ledger2, _config()).handle_envelope(_root(approval_id2))

    ledger3, _, approval_id3 = _pending()
    ApprovalService(ledger3).decide(
        approval_id3,
        actor="michael",
        approved=False,
        reason="prior decision",
    )
    with pytest.raises(ValueError, match="not pending"):
        SlackSocketApprovalService(ledger3, _config()).handle_envelope(_root(approval_id3))


def test_reply_revalidates_binding_canonical_owner_fingerprint_and_message_fields() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_root(approval_id))

    binding = dict(ledger.get_record("approval_slack_thread_binding", ROOT_TS))
    binding["approval_id"] = ""
    ledger.save_record("approval_slack_thread_binding", ROOT_TS, binding)
    with pytest.raises(PermissionError, match="binding is invalid"):
        service.handle_envelope(_reply("APPROVE"))

    ledger2, _, approval_id2 = _pending()
    service2 = SlackSocketApprovalService(ledger2, _config())
    service2.handle_envelope(_root(approval_id2))
    ledger2.delete_record("approval", approval_id2)
    with pytest.raises(KeyError):
        service2.handle_envelope(_reply("APPROVE"))

    ledger3, _, approval_id3 = _pending()
    service3 = SlackSocketApprovalService(ledger3, _config())
    service3.handle_envelope(_root(approval_id3))
    approval3 = dict(ledger3.get_record("approval", approval_id3))
    approval3["approval_owner"] = "other"
    ledger3.save_record("approval", approval_id3, approval3)
    with pytest.raises(PermissionError, match="owner"):
        service3.handle_envelope(_reply("APPROVE"))

    ledger4, _, approval_id4 = _pending()
    service4 = SlackSocketApprovalService(ledger4, _config())
    service4.handle_envelope(_root(approval_id4))
    binding4 = dict(ledger4.get_record("approval_slack_thread_binding", ROOT_TS))
    binding4["payload_fingerprint"] = "0" * 64
    ledger4.save_record("approval_slack_thread_binding", ROOT_TS, binding4)
    with pytest.raises(PermissionError, match="fingerprint changed"):
        service4.handle_envelope(_reply("APPROVE"))

    ledger5, _, approval_id5 = _pending()
    service5 = SlackSocketApprovalService(ledger5, _config())
    service5.handle_envelope(_root(approval_id5))
    approval5 = dict(ledger5.get_record("approval", approval_id5))
    approval5["status"] = "REJECTED"
    ledger5.save_record("approval", approval_id5, approval5)
    with pytest.raises(ValueError, match="already decided"):
        service5.handle_envelope(_reply("APPROVE"))

    ledger6, _, approval_id6 = _pending()
    service6 = SlackSocketApprovalService(ledger6, _config())
    service6.handle_envelope(_root(approval_id6))
    missing_user = _reply("APPROVE")
    missing_user["payload"]["event"].pop("user")
    with pytest.raises(PermissionError, match="user"):
        service6.handle_envelope(missing_user)

    missing_ts = _reply("APPROVE")
    missing_ts["payload"]["event"].pop("ts")
    with pytest.raises(PermissionError, match="ts"):
        service6.handle_envelope(missing_ts)
