from __future__ import annotations

from pathlib import Path

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_hitl import CHATGPT_AGENTS_SLACK_USER_ID
from mesh_cos.slack_socket_approval import (
    SlackSocketApprovalConfig,
    SlackSocketApprovalService,
)

CHANNEL_ID = "C0TESTAGENTOPS"
APPROVER_USER_ID = "U0TESTAPPROVER"
THREAD_TS = "1788000000.000001"
FINGERPRINT = "d" * 64


def _pending() -> tuple[TaskLedger, str, str]:
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
        f"Execute exact payload_fingerprint={FINGERPRINT}",
    )
    ledger.save_record(
        "approval_slack_binding",
        approval.approval_id,
        {
            "version": "mesh.cos.approval-slack-binding.v1",
            "approval_id": approval.approval_id,
            "task_id": task.task_id,
            "channel_id": CHANNEL_ID,
            "thread_ts": THREAD_TS,
            "notice_author_user_id": CHATGPT_AGENTS_SLACK_USER_ID,
            "approver_user_id": APPROVER_USER_ID,
            "approver_principal": "michael",
            "payload_fingerprint": FINGERPRINT,
            "bound_at": "2026-08-26T15:00:00+00:00",
        },
    )
    return ledger, task.task_id, approval.approval_id


def _config() -> SlackSocketApprovalConfig:
    return SlackSocketApprovalConfig(
        channel_id=CHANNEL_ID,
        approver_user_id=APPROVER_USER_ID,
        approver_principal="michael",
        command="/mesh-approval",
    )


def _envelope(approval_id: str, *, text: str | None = None) -> dict:
    return {
        "envelope_id": "env-001",
        "type": "slash_commands",
        "accepts_response_payload": True,
        "payload": {
            "team_id": "T0TEST",
            "channel_id": CHANNEL_ID,
            "channel_name": "mesh-agent-ops",
            "user_id": APPROVER_USER_ID,
            "user_name": "human-approver",
            "command": "/mesh-approval",
            "text": text or f"APPROVE {approval_id}",
            "trigger_id": "trigger-001",
        },
    }


def test_socket_slash_command_can_record_canonical_human_approval_idempotently() -> None:
    ledger, task_id, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    decision = service.handle_envelope(_envelope(approval_id))
    replay = service.handle_envelope(_envelope(approval_id))

    assert replay == decision
    assert decision["version"] == "mesh.cos.slack-human-decision.v2"
    assert decision["source"] == "SLACK_SOCKET_MODE_SLASH_COMMAND"
    assert decision["envelope_id"] == "env-001"
    assert decision["trigger_id"] == "trigger-001"
    assert decision["disposition"] == "APPROVE"
    assert decision["canonical_principal"] == "michael"
    assert ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert ledger.get_record("approval", approval_id)["decided_by"] == "michael"
    assert ledger.get_task(task_id).status == TaskStatus.READY_FOR_ACTION


def test_ordinary_message_envelope_cannot_become_human_approval() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    fabricated = {
        "envelope_id": "env-chat-message",
        "type": "events_api",
        "payload": {
            "event": {
                "type": "message",
                "channel": CHANNEL_ID,
                "user": APPROVER_USER_ID,
                "text": f"APPROVE {approval_id}",
            }
        },
    }

    with pytest.raises(PermissionError, match="slash_commands"):
        service.handle_envelope(fabricated)
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("user_id", "U0NOTAPPROVER", "approver"),
        ("channel_id", "C0OTHER", "channel"),
        ("command", "/not-mesh-approval", "command"),
    ],
)
def test_wrong_provider_interaction_identity_or_route_fails_closed(
    field: str,
    value: str,
    error: str,
) -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    envelope = _envelope(approval_id)
    envelope["payload"][field] = value

    with pytest.raises(PermissionError, match=error):
        service.handle_envelope(envelope)
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_unbound_or_non_openai_notice_cannot_be_decided() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    ledger.delete_record("approval_slack_binding", approval_id)
    with pytest.raises(PermissionError, match="provider-verified Slack notice"):
        service.handle_envelope(_envelope(approval_id))

    ledger2, _, approval_id2 = _pending()
    binding = dict(ledger2.get_record("approval_slack_binding", approval_id2))
    binding["notice_author_user_id"] = "U0FAKEBOT"
    ledger2.save_record("approval_slack_binding", approval_id2, binding)
    service2 = SlackSocketApprovalService(ledger2, _config())
    with pytest.raises(PermissionError, match="OpenAI"):
        service2.handle_envelope(_envelope(approval_id2))


def test_binding_and_canonical_payload_must_still_reconcile() -> None:
    ledger, _, approval_id = _pending()
    binding = dict(ledger.get_record("approval_slack_binding", approval_id))
    binding["payload_fingerprint"] = "e" * 64
    ledger.save_record("approval_slack_binding", approval_id, binding)
    service = SlackSocketApprovalService(ledger, _config())

    with pytest.raises(PermissionError, match="fingerprint"):
        service.handle_envelope(_envelope(approval_id))
    assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_reject_and_changes_are_exact_provider_authenticated_human_decisions() -> None:
    ledger, task_id, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    rejected = service.handle_envelope(
        _envelope(approval_id, text=f"REJECT {approval_id}")
    )
    assert rejected["disposition"] == "REJECT"
    assert ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    assert ledger.get_task(task_id).status == TaskStatus.IN_PROGRESS

    ledger2, task_id2, approval_id2 = _pending()
    service2 = SlackSocketApprovalService(ledger2, _config())
    changed = service2.handle_envelope(
        _envelope(approval_id2, text=f"CHANGES {approval_id2}: remove recipient")
        | {"envelope_id": "env-002"}
    )
    assert changed["disposition"] == "CHANGES"
    assert changed["requested_change"] == "remove recipient"
    assert ledger2.get_record("approval", approval_id2)["status"] == "REJECTED"
    assert ledger2.get_task(task_id2).status == TaskStatus.IN_PROGRESS


def test_second_distinct_interaction_cannot_redecide_an_approval() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())
    service.handle_envelope(_envelope(approval_id))
    second = _envelope(approval_id, text=f"REJECT {approval_id}") | {
        "envelope_id": "env-distinct",
    }

    with pytest.raises(ValueError, match="already decided"):
        service.handle_envelope(second)


def test_config_can_read_protected_approver_identity_file(tmp_path: Path) -> None:
    approver_file = tmp_path / "approver-id"
    approver_file.write_text(APPROVER_USER_ID + "\n", encoding="utf-8")
    config = SlackSocketApprovalConfig.from_env(
        {
            "MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID": CHANNEL_ID,
            "MESH_COS_SLACK_APPROVER_USER_ID_FILE": str(approver_file),
            "MESH_COS_SLACK_APPROVER_PRINCIPAL": "michael",
            "MESH_COS_SLACK_APPROVAL_COMMAND": "/mesh-approval",
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
        (
            {
                "channel_id": CHANNEL_ID,
                "approver_user_id": APPROVER_USER_ID,
                "command": "/other",
            },
            "command",
        ),
    ],
)
def test_socket_config_rejects_authority_widening_or_missing_identity(
    kwargs: dict,
    error: str,
) -> None:
    with pytest.raises(RuntimeError, match=error):
        SlackSocketApprovalConfig(**kwargs)


def test_socket_envelope_requires_provider_fields_and_mapping_payload() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    missing_envelope_id = _envelope(approval_id)
    missing_envelope_id.pop("envelope_id")
    with pytest.raises(PermissionError, match="missing envelope_id"):
        service.handle_envelope(missing_envelope_id)

    invalid_payload = _envelope(approval_id)
    invalid_payload["payload"] = "not-a-mapping"
    with pytest.raises(PermissionError, match="payload is invalid"):
        service.handle_envelope(invalid_payload)


def test_socket_binding_must_match_governed_channel_approver_and_principal() -> None:
    for field, value, error in (
        ("channel_id", "C0OTHER", "channel mismatch"),
        ("approver_user_id", "U0OTHER", "approver mismatch"),
        ("approver_principal", "other", "principal mismatch"),
    ):
        ledger, _, approval_id = _pending()
        binding = dict(ledger.get_record("approval_slack_binding", approval_id))
        binding[field] = value
        ledger.save_record("approval_slack_binding", approval_id, binding)
        service = SlackSocketApprovalService(ledger, _config())
        with pytest.raises(PermissionError, match=error):
            service.handle_envelope(_envelope(approval_id))
        assert ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_socket_command_requires_exact_approval_id() -> None:
    ledger, _, approval_id = _pending()
    service = SlackSocketApprovalService(ledger, _config())

    with pytest.raises(PermissionError, match="missing an Approval ID"):
        service.handle_envelope(_envelope(approval_id, text="APPROVE"))

    with pytest.raises(KeyError):
        service.handle_envelope(_envelope("approval-unknown"))


def test_socket_cannot_mutate_nonpending_or_wrong_owner_approval() -> None:
    ledger, _, approval_id = _pending()
    ApprovalService(ledger).decide(
        approval_id,
        actor="michael",
        approved=False,
        reason="synthetic prior human decision",
    )
    service = SlackSocketApprovalService(ledger, _config())
    with pytest.raises(ValueError, match="already decided"):
        service.handle_envelope(_envelope(approval_id) | {"envelope_id": "env-late"})

    ledger2, _, approval_id2 = _pending()
    approval = dict(ledger2.get_record("approval", approval_id2))
    approval["approval_owner"] = "other-principal"
    ledger2.save_record("approval", approval_id2, approval)
    service2 = SlackSocketApprovalService(ledger2, _config())
    with pytest.raises(PermissionError, match="approval owner"):
        service2.handle_envelope(_envelope(approval_id2))
