from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import (
    INTERACTION_STATE_KIND,
    SlackApprovalNotifier,
    SlackBotAPI,
)
from mesh_cos.slack_native_trigger import SlackNativeTriggerApprovalService
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig

CHANNEL = "C0BRL4GCL3A"
USER = "U01KG3CNYHK"
APP = "A0B49RNE4K0"
ROOT = "1789919000.100001"
REPLY = "1789919001.100002"
FINGERPRINT = "f" * 64


def _task(ledger: TaskLedger, authority: AuthorityLevel = AuthorityLevel.L2) -> str:
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Exercise Slack peer HITL",
        expected_outcome="Human receives clear bidirectional feedback",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=authority,
        acceptance_test="Slack provider state and canonical state agree",
        idempotency_key=f"HITL-PEER-{int(authority)}",
    )
    for target in (
        TaskStatus.TRIAGED,
        TaskStatus.PLANNED,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
    ):
        cos.advance(task.task_id, target)
    return task.task_id


class Harness:
    def __init__(self, *, authority: AuthorityLevel = AuthorityLevel.L2) -> None:
        self.ledger = TaskLedger()
        self.task_id = _task(self.ledger, authority)
        self.reply_text = "confirmed"
        self.reply_user = USER
        self.reply_fields: dict[str, object] = {}
        self.calls: list[tuple[str, dict, str]] = []
        self.next_ts = 0

        def transport(method: str, payload: dict, token: str) -> dict:
            self.calls.append((method, dict(payload), token))
            if method == "conversations.replies":
                return {
                    "ok": True,
                    "messages": [
                        {
                            "type": "message",
                            "channel": CHANNEL,
                            "thread_ts": ROOT,
                            "ts": REPLY,
                            "user": self.reply_user,
                            "text": self.reply_text,
                            **self.reply_fields,
                        }
                    ],
                }
            if method == "chat.update":
                return {"ok": True, "channel": CHANNEL, "ts": payload["ts"]}
            if method == "chat.postMessage":
                self.next_ts += 1
                ts = ROOT if not payload.get("thread_ts") else f"1789919010.{self.next_ts:06d}"
                return {"ok": True, "channel": CHANNEL, "ts": ts}
            raise AssertionError(method)

        self.notifier = SlackApprovalNotifier(
            self.ledger,
            SlackBotAPI("xoxb-test", transport),
            CHANNEL,
        )
        self.service = SlackNativeTriggerApprovalService(
            self.ledger,
            SlackSocketApprovalConfig(CHANNEL, USER, "michael", APP),
            self.notifier,
        )

    def reconcile(self) -> dict:
        return self.service.reconcile(thread_ts=ROOT, message_ts=REPLY)

    def thread_posts(self) -> list[dict]:
        return [
            payload
            for method, payload, _ in self.calls
            if method == "chat.postMessage" and payload.get("thread_ts") == ROOT
        ]


def test_hitl_chat_001_information_is_bot_contract_and_reply_has_no_authority() -> None:
    h = Harness()
    posted = h.notifier.post_interaction(
        thread_type="INFO",
        task_id=h.task_id,
        summary="Runtime health is green.",
        requested_human_action="",
        completion_condition="No action required.",
    )
    assert posted["thread_type"] == "INFO"
    root_payload = next(
        payload
        for method, payload, _ in h.calls
        if method == "chat.postMessage" and not payload.get("thread_ts")
    )
    assert root_payload["text"].startswith("### INFORMATION")
    assert "No response is required." in root_payload["text"]
    result = h.reconcile()
    assert result["authority_mutated"] is False
    assert result["reply_class"] == "INFORMATION_ACKNOWLEDGED"
    assert "required no action or approval" in h.thread_posts()[-1]["text"]


def test_hitl_chat_002_manual_action_done_is_acknowledged_without_false_approval() -> None:
    h = Harness()
    h.notifier.post_interaction(
        thread_type="MANUAL_ACTION",
        task_id=h.task_id,
        summary="Two mirror cells need repair.",
        requested_human_action="Repair only O145 and R145.",
        completion_condition="O145 and R145 match canonical TaskLedger state.",
    )
    state = h.ledger.get_record(INTERACTION_STATE_KIND, ROOT)
    assert state["explicit_approval_required"] is False
    assert state["valid_response_classes"] == ["DONE", "NATURAL_LANGUAGE"]
    h.reply_text = "DONE"
    result = h.reconcile()
    assert result["reply_class"] == "MANUAL_ACTION_DONE"
    assert result["authority_mutated"] is False
    assert "Verification remains separate" in h.thread_posts()[-1]["text"]


def test_hitl_chat_003_conversational_confirmation_gets_contextual_feedback() -> None:
    h = Harness()
    h.notifier.post_interaction(
        thread_type="MANUAL_ACTION",
        task_id=h.task_id,
        summary="Manual repair is outstanding.",
        requested_human_action="Repair only O145 and R145.",
        completion_condition="Mirror agrees with TaskLedger.",
    )
    h.reply_text = "confirmed"
    result = h.reconcile()
    assert result["reply_class"] == "CONVERSATIONAL_CONFIRMATION"
    assert "outstanding action is still" in h.thread_posts()[-1]["text"]


def test_hitl_chat_006_approve_on_nonapproval_thread_never_mutates_authority() -> None:
    h = Harness()
    h.notifier.post_interaction(
        thread_type="MANUAL_ACTION",
        task_id=h.task_id,
        summary="Manual repair is outstanding.",
        requested_human_action="Repair only O145 and R145.",
        completion_condition="Mirror agrees with TaskLedger.",
    )
    h.reply_text = "APPROVE"
    result = h.reconcile()
    assert result["reply_class"] == "INVALID_AUTHORITY_COMMAND"
    assert result["authority_mutated"] is False
    assert "not awaiting approval" in h.thread_posts()[-1]["text"]


def _approval_harness() -> tuple[Harness, str]:
    h = Harness(authority=AuthorityLevel.L4)
    approval = ApprovalService(h.ledger).request(
        h.task_id,
        "cos",
        "michael",
        AuthorityLevel.L4,
        f"Execute synthetic action payload_fingerprint={FINGERPRINT}",
    )
    h.notifier.post_approval(approval.approval_id)
    return h, approval.approval_id


@pytest.mark.parametrize("reply", ["looks good", "confirmed", "yes", "👍"])
def test_hitl_chat_005_ambiguous_approval_language_is_never_authority(reply: str) -> None:
    h, approval_id = _approval_harness()
    h.reply_text = reply
    result = h.reconcile()
    assert result["reply_class"] == "APPROVAL_AMBIGUOUS"
    assert result["authority_mutated"] is False
    assert h.ledger.get_record("approval", approval_id)["status"] == "PENDING"
    assert "requires explicit approval" in h.thread_posts()[-1]["text"]


def test_hitl_chat_004_inline_code_approve_is_provider_verified_and_acknowledged() -> None:
    h, approval_id = _approval_harness()
    h.reply_text = "`APPROVE`"
    result = h.reconcile()
    assert result["reply_class"] == "APPROVAL_APPROVED"
    assert result["authority_mutated"] is True
    assert result["provider_identity_verified"] is True
    assert h.ledger.get_record("approval", approval_id)["status"] == "APPROVED"
    assert "Approved. Approval" in h.thread_posts()[-1]["text"]


def test_mentioned_approve_is_not_silently_normalized_into_authority() -> None:
    h, approval_id = _approval_harness()
    h.reply_text = "<@U0BKV7Z8M96> APPROVE"
    result = h.reconcile()
    assert result["reply_class"] == "APPROVAL_AMBIGUOUS"
    assert h.ledger.get_record("approval", approval_id)["status"] == "PENDING"


def test_hitl_chat_007_deny_is_canonical_and_acknowledged() -> None:
    h, approval_id = _approval_harness()
    h.reply_text = "DENY"
    result = h.reconcile()
    assert result["reply_class"] == "APPROVAL_DENIED"
    assert result["authority_mutated"] is True
    assert h.ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    assert "No action is authorized" in h.thread_posts()[-1]["text"]


def test_hitl_chat_008_changes_detail_supersedes_approval_and_is_acknowledged() -> None:
    h, approval_id = _approval_harness()
    h.reply_text = "CHANGES: remove the second recipient"
    result = h.reconcile()
    assert result["reply_class"] == "APPROVAL_CHANGES_REQUESTED"
    assert result["authority_mutated"] is True
    assert h.ledger.get_record("approval", approval_id)["status"] == "REJECTED"
    changes = h.ledger.list_records("approval_change_request")
    assert changes[-1]["change_instruction"] == "remove the second recipient"
    assert "prior approval is superseded" in h.thread_posts()[-1]["text"]


def test_hitl_chat_009_duplicate_delivery_is_idempotent_without_duplicate_ack() -> None:
    h = Harness()
    h.notifier.post_interaction(
        thread_type="INFO",
        task_id=h.task_id,
        summary="No action required.",
        requested_human_action="",
        completion_condition="No action required.",
    )
    first = h.reconcile()
    ack_count = len(h.thread_posts())
    second = h.reconcile()
    assert first["acknowledgment_message_ts"] == second["acknowledgment_message_ts"]
    assert second["replayed"] is True
    assert len(h.thread_posts()) == ack_count


def test_hitl_chat_010_and_011_wrong_or_bot_user_fail_closed() -> None:
    h = Harness()
    h.notifier.post_interaction(
        thread_type="INFO",
        task_id=h.task_id,
        summary="No action required.",
        requested_human_action="",
        completion_condition="No action required.",
    )
    h.reply_user = "U0OTHER"
    with pytest.raises(PermissionError, match="configured approver"):
        h.reconcile()

    h2 = Harness()
    h2.notifier.post_interaction(
        thread_type="INFO",
        task_id=h2.task_id,
        summary="No action required.",
        requested_human_action="",
        completion_condition="No action required.",
    )
    h2.reply_fields["bot_id"] = "B0BOT"
    with pytest.raises(PermissionError, match="app-authored"):
        h2.reconcile()
