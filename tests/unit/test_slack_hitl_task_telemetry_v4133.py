from __future__ import annotations

import pytest

from mesh_cos.approval import ApprovalService
from mesh_cos.ledger import TaskLedger
from mesh_cos.mcp_runtime import MCPRuntime
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.slack_bot import INTERACTION_STATE_KIND, SlackApprovalNotifier, SlackBotAPI
from mesh_cos.slack_native_trigger import SlackNativeTriggerApprovalService
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig

CHANNEL = "C0BRL4GCL3A"
USER = "U01KG3CNYHK"
APP = "A0B49RNE4K0"
ROOT = "1789921000.100001"
REPLY = "1789921001.100002"
REPLY2 = "1789921002.100003"
FINGERPRINT = "a" * 64


class TelemetryHarness:
    def __init__(self, *, authority: AuthorityLevel = AuthorityLevel.L2) -> None:
        self.ledger = TaskLedger()
        cos = ChiefOfStaffService(self.ledger)
        task = cos.intake(
            objective="Verify Slack task telemetry",
            expected_outcome="Canonical task telemetry matches provider-verified interaction",
            requested_by="cos",
            executive_sponsor="michael",
            accountable_agent="cos",
            decision_owner="michael",
            authority_level=authority,
            acceptance_test="TaskRecord telemetry is durable and replay safe",
            idempotency_key=f"HITL-TELEM-TASK-{int(authority)}",
        )
        for target in (
            TaskStatus.TRIAGED,
            TaskStatus.PLANNED,
            TaskStatus.ASSIGNED,
            TaskStatus.IN_PROGRESS,
        ):
            cos.advance(task.task_id, target)
        self.task_id = task.task_id
        self.replies: dict[str, dict[str, object]] = {
            REPLY: {"user": USER, "text": "DONE"},
            REPLY2: {"user": USER, "text": "Need context"},
        }
        self.calls: list[tuple[str, dict, str]] = []
        self.next_ack = 0

        def transport(method: str, payload: dict, token: str) -> dict:
            self.calls.append((method, dict(payload), token))
            if method == "conversations.replies":
                message_ts = str(payload["oldest"])
                reply = dict(self.replies[message_ts])
                return {
                    "ok": True,
                    "messages": [
                        {
                            "type": "message",
                            "channel": CHANNEL,
                            "thread_ts": ROOT,
                            "ts": message_ts,
                            **reply,
                        }
                    ],
                }
            if method == "chat.update":
                return {"ok": True, "channel": CHANNEL, "ts": payload["ts"]}
            if method == "chat.postMessage":
                if not payload.get("thread_ts"):
                    return {"ok": True, "channel": CHANNEL, "ts": ROOT}
                self.next_ack += 1
                return {
                    "ok": True,
                    "channel": CHANNEL,
                    "ts": f"1789921010.{self.next_ack:06d}",
                }
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

    def post_manual(self) -> None:
        self.notifier.post_interaction(
            thread_type="MANUAL_ACTION",
            task_id=self.task_id,
            summary="A bounded human action is required.",
            requested_human_action="Complete the bounded action and reply DONE.",
            completion_condition="Independent verification confirms the action.",
        )

    def reconcile(self, message_ts: str = REPLY) -> dict:
        return self.service.reconcile(thread_ts=ROOT, message_ts=message_ts)

    def task(self) -> dict:
        return MCPRuntime(self.ledger)._task_get("cos", {"task_id": self.task_id})

    def thread_posts(self) -> list[dict]:
        return [
            payload
            for method, payload, _ in self.calls
            if method == "chat.postMessage" and payload.get("thread_ts") == ROOT
        ]


def test_hitl_telem_001_provider_confirmed_post_binds_canonical_task() -> None:
    h = TelemetryHarness()
    before = h.task()
    assert before["slack_channel_id"] is None
    assert before["slack_thread_ts"] is None

    h.post_manual()

    after = h.task()
    assert after["slack_channel_id"] == CHANNEL
    assert after["slack_thread_ts"] == ROOT
    assert h.ledger.get_thread(h.task_id) == {
        "task_id": h.task_id,
        "channel_id": CHANNEL,
        "thread_ts": ROOT,
    }


def test_hitl_telem_002_verified_done_increments_human_touch_once() -> None:
    h = TelemetryHarness()
    h.post_manual()
    assert h.task()["human_touches"] == 0

    result = h.reconcile()

    assert result["reply_class"] == "MANUAL_ACTION_DONE"
    assert h.task()["human_touches"] == 1


def test_hitl_telem_003_replay_does_not_double_count_or_ack() -> None:
    h = TelemetryHarness()
    h.post_manual()

    first = h.reconcile()
    ack_count = len(h.thread_posts())
    second = h.reconcile()

    assert first == second
    assert h.task()["human_touches"] == 1
    assert len(h.thread_posts()) == ack_count
    assert h.ledger.record_human_touch(
        h.task_id,
        provider_event_id=f"native-slack:{CHANNEL}:{REPLY}",
        channel_id=CHANNEL,
        thread_ts=ROOT,
        message_ts=REPLY,
    ) is False
    assert h.task()["human_touches"] == 1


def test_hitl_telem_004_second_distinct_verified_reply_counts_once_more() -> None:
    h = TelemetryHarness()
    h.post_manual()

    h.reconcile(REPLY)
    second = h.reconcile(REPLY2)

    assert second["reply_class"] == "CONVERSATIONAL_RESPONSE"
    assert h.task()["human_touches"] == 2


def test_hitl_telem_005_bot_acknowledgment_is_not_a_human_touch() -> None:
    h = TelemetryHarness()
    h.post_manual()

    h.reconcile()

    assert len(h.thread_posts()) == 1
    assert h.task()["human_touches"] == 1


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ({"user": "U0OTHER"}, "configured approver"),
        ({"bot_id": "B0BOT"}, "app-authored"),
        ({"app_id": "A0APP"}, "app-authored"),
        ({"edited": {"ts": REPLY}}, "Edited Slack messages"),
    ],
)
def test_hitl_telem_006_rejected_provider_events_do_not_count(
    mutation: dict[str, object],
    error: str,
) -> None:
    h = TelemetryHarness()
    h.post_manual()
    h.replies[REPLY].update(mutation)

    with pytest.raises(PermissionError, match=error):
        h.reconcile()

    assert h.task()["human_touches"] == 0


def test_hitl_telem_006_unbound_or_invalid_state_does_not_count() -> None:
    h = TelemetryHarness()
    with pytest.raises(PermissionError, match="not in a governed bound thread"):
        h.reconcile()
    assert h.task()["human_touches"] == 0

    h.post_manual()
    state = dict(h.ledger.get_record(INTERACTION_STATE_KIND, ROOT))
    state["channel_id"] = "C0OTHER"
    h.ledger.save_record(INTERACTION_STATE_KIND, ROOT, state)
    result = h.reconcile(REPLY)
    assert result["authority_mutated"] is False
    assert h.task()["human_touches"] == 0

    assert h.service._record_verified_human_touch(
        state={"task_id": "", "channel_id": CHANNEL, "thread_ts": ROOT},
        provider_event_id="native-slack:empty",
        message_ts=REPLY,
    ) is False
    with pytest.raises(KeyError):
        h.ledger.record_human_touch(
            "task-missing",
            provider_event_id="native-slack:missing",
            channel_id=CHANNEL,
            thread_ts=ROOT,
            message_ts=REPLY,
        )


def test_hitl_telem_007_approve_on_nonapproval_counts_touch_but_not_authority() -> None:
    h = TelemetryHarness()
    h.post_manual()
    h.replies[REPLY]["text"] = "APPROVE"

    result = h.reconcile()
    task = h.task()

    assert result["reply_class"] == "INVALID_AUTHORITY_COMMAND"
    assert result["authority_mutated"] is False
    assert task["human_touches"] == 1
    assert task["approval_status"] == "NOT_REQUIRED"
    assert task["status"] == TaskStatus.IN_PROGRESS.value


def test_hitl_telem_008_real_approval_records_touch_independently() -> None:
    h = TelemetryHarness(authority=AuthorityLevel.L4)
    approval = ApprovalService(h.ledger).request(
        h.task_id,
        "cos",
        "michael",
        AuthorityLevel.L4,
        f"Synthetic bounded decision payload_fingerprint={FINGERPRINT}",
    )
    h.notifier.post_approval(approval.approval_id)
    h.replies[REPLY]["text"] = "APPROVE"

    result = h.reconcile()

    assert result["disposition"] == "APPROVE"
    assert h.ledger.get_record("approval", approval.approval_id)["status"] == "APPROVED"
    assert h.task()["human_touches"] == 1


def test_hitl_telem_009_telemetry_does_not_advance_task_lifecycle() -> None:
    h = TelemetryHarness()
    h.post_manual()
    before = h.task()["status"]

    h.reconcile()

    after = h.task()
    assert before == TaskStatus.IN_PROGRESS.value
    assert after["status"] == before
    assert after["completed_at"] is None
    assert after["verified_at"] is None


def test_hitl_telem_010_task_get_returns_all_persisted_telemetry() -> None:
    h = TelemetryHarness()
    h.post_manual()
    h.reconcile()

    task = h.task()
    assert task["slack_channel_id"] == CHANNEL
    assert task["slack_thread_ts"] == ROOT
    assert task["human_touches"] == 1
