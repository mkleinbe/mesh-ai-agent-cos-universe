from __future__ import annotations

import pytest

from mesh_cos.adapters import GovernedAdapterRegistry
from mesh_cos.governance import GovernanceJournal
from mesh_cos.ledger import TaskLedger
from mesh_cos.models import AuthorityLevel, TaskStatus
from mesh_cos.orchestration import ChiefOfStaffService
from mesh_cos.registry import load_registry
from mesh_cos.slack_bot import (
    INTERACTION_STATE_KIND,
    THREAD_BINDING_KIND,
    SlackApprovalNotifier,
    SlackBotAPI,
)
from mesh_cos.slack_native_trigger import SlackNativeTriggerApprovalService
from mesh_cos.slack_socket_approval import SlackSocketApprovalConfig

CHANNEL = "C0BRL4GCL3A"
USER = "U01KG3CNYHK"
APP = "A0B49RNE4K0"
ROOT = "1789919200.100001"
REPLY = "1789919201.100002"


def _task(ledger: TaskLedger) -> str:
    cos = ChiefOfStaffService(ledger)
    task = cos.intake(
        objective="Cover peer HITL branches",
        expected_outcome="Coverage proves all guarded peer paths",
        requested_by="cos",
        executive_sponsor="michael",
        accountable_agent="cos",
        decision_owner="michael",
        authority_level=AuthorityLevel.L2,
        acceptance_test="All branch behavior is deterministic",
        idempotency_key="HITL-COVERAGE-V4130",
    )
    for target in (
        TaskStatus.TRIAGED,
        TaskStatus.PLANNED,
        TaskStatus.ASSIGNED,
        TaskStatus.IN_PROGRESS,
    ):
        cos.advance(task.task_id, target)
    return task.task_id


def _notifier(
    ledger: TaskLedger,
    *,
    root_channel: str = CHANNEL,
    root_ts: str = ROOT,
) -> tuple[SlackApprovalNotifier, list[tuple[str, dict, str]]]:
    calls: list[tuple[str, dict, str]] = []

    def transport(method: str, payload: dict, token: str) -> dict:
        calls.append((method, dict(payload), token))
        if method == "chat.postMessage":
            return {
                "ok": True,
                "channel": root_channel,
                "ts": (
                    root_ts
                    if not payload.get("thread_ts")
                    else "1789919210.100003"
                ),
            }
        if method == "chat.update":
            return {"ok": True, "channel": root_channel, "ts": payload["ts"]}
        raise AssertionError(method)

    return (
        SlackApprovalNotifier(
            ledger,
            SlackBotAPI("xoxb-test", transport),
            CHANNEL,
        ),
        calls,
    )


def test_post_interaction_validation_question_blocker_and_provider_identity_errors() -> None:
    ledger = TaskLedger()
    task_id = _task(ledger)
    notifier, calls = _notifier(ledger)

    with pytest.raises(ValueError, match="Unsupported"):
        notifier.post_interaction(
            thread_type="UNKNOWN",
            task_id=task_id,
            summary="x",
            requested_human_action="",
            completion_condition="",
        )
    with pytest.raises(ValueError, match="summary is required"):
        notifier.post_interaction(
            thread_type="QUESTION",
            task_id=task_id,
            summary=" ",
            requested_human_action="Answer this.",
            completion_condition="Answer recorded.",
        )

    question = notifier.post_interaction(
        thread_type="QUESTION",
        task_id=task_id,
        summary="Which option should I use?",
        requested_human_action="Reply with the option.",
        completion_condition="Answer is recorded.",
    )
    assert question["thread_type"] == "QUESTION"
    assert "normal language" in calls[-1][1]["text"]
    assert "conversational question" in calls[-1][1]["text"]

    blocker = notifier.post_interaction(
        thread_type="BLOCKER",
        task_id=task_id,
        summary="A source is unavailable.",
        requested_human_action="Provide the missing source.",
        completion_condition="Source is available.",
    )
    assert blocker["thread_type"] == "BLOCKER"
    assert "No approval authority is created" in calls[-1][1]["text"]

    missing, _ = _notifier(TaskLedger())
    with pytest.raises(KeyError, match="missing-task"):
        missing.post_interaction(
            thread_type="STATUS",
            task_id="missing-task",
            summary="Status.",
            requested_human_action="",
            completion_condition="",
        )

    wrong, _ = _notifier(ledger, root_channel="C0OTHER")
    with pytest.raises(RuntimeError, match="expected interaction message identity"):
        wrong.post_interaction(
            thread_type="STATUS",
            task_id=task_id,
            summary="Status.",
            requested_human_action="",
            completion_condition="",
        )


def test_governed_adapter_post_interaction_exact_contract() -> None:
    ledger = TaskLedger()
    task_id = _task(ledger)
    notifier, _ = _notifier(ledger)
    registry = GovernedAdapterRegistry(
        load_registry(),
        GovernanceJournal(ledger),
        slack_notifier=notifier,
    )
    result = registry.execute(
        "cos",
        "slack-adapter",
        {
            "operation": "post_interaction",
            "channel_id": CHANNEL,
            "payload": {
                "thread_type": "STATUS",
                "task_id": task_id,
                "summary": "The workflow remains active.",
                "requested_human_action": "",
                "completion_condition": "No action required.",
            },
        },
    )
    assert result["status"] == "POSTED"
    with pytest.raises(ValueError, match="Missing Slack collaboration payload fields"):
        registry.execute(
            "cos",
            "slack-adapter",
            {
                "operation": "post_interaction",
                "channel_id": CHANNEL,
                "payload": {
                    "thread_type": "STATUS",
                    "task_id": task_id,
                    "summary": "Missing completion.",
                    "requested_human_action": "",
                },
            },
        )


class ConversationHarness:
    def __init__(self, thread_type: str, text: str) -> None:
        self.ledger = TaskLedger()
        self.task_id = _task(self.ledger)
        self.text = text
        self.extra: dict[str, object] = {}
        self.calls: list[tuple[str, dict, str]] = []

        def transport(method: str, payload: dict, token: str) -> dict:
            self.calls.append((method, dict(payload), token))
            if method == "chat.postMessage":
                return {
                    "ok": True,
                    "channel": CHANNEL,
                    "ts": (
                        ROOT
                        if not payload.get("thread_ts")
                        else "1789919220.100004"
                    ),
                }
            if method == "conversations.replies":
                return {
                    "ok": True,
                    "messages": [
                        {
                            "type": "message",
                            "channel": CHANNEL,
                            "thread_ts": ROOT,
                            "ts": REPLY,
                            "user": USER,
                            "text": self.text,
                            **self.extra,
                        }
                    ],
                }
            raise AssertionError(method)

        self.notifier = SlackApprovalNotifier(
            self.ledger,
            SlackBotAPI("xoxb-test", transport),
            CHANNEL,
        )
        self.notifier.post_interaction(
            thread_type=thread_type,
            task_id=self.task_id,
            summary="Bounded interaction.",
            requested_human_action="Provide context.",
            completion_condition="Context is sufficient.",
        )
        self.service = SlackNativeTriggerApprovalService(
            self.ledger,
            SlackSocketApprovalConfig(CHANNEL, USER, "michael", APP),
            self.notifier,
        )


def test_conversation_subtype_question_and_fallback_paths() -> None:
    subtype = ConversationHarness("INFO", "ok")
    subtype.extra["subtype"] = "message_changed"
    with pytest.raises(PermissionError, match="subtype"):
        subtype.service.reconcile(thread_ts=ROOT, message_ts=REPLY)

    question = ConversationHarness("QUESTION", "Use option B")
    result = question.service.reconcile(thread_ts=ROOT, message_ts=REPLY)
    assert result["reply_class"] == "QUESTION_RESPONSE"
    assert "conversation, not approval" in [
        p[1]["text"]
        for p in question.calls
        if p[0] == "chat.postMessage" and p[1].get("thread_ts")
    ][-1]

    blocker = ConversationHarness("BLOCKER", "Still blocked")
    result = blocker.service.reconcile(thread_ts=ROOT, message_ts=REPLY)
    assert result["reply_class"] == "CONVERSATIONAL_RESPONSE"
    assert "Current task state" in [
        p[1]["text"]
        for p in blocker.calls
        if p[0] == "chat.postMessage" and p[1].get("thread_ts")
    ][-1]


def test_conversation_missing_task_and_empty_completion_paths() -> None:
    h = ConversationHarness("MANUAL_ACTION", "DONE")
    state = dict(h.ledger.get_record(INTERACTION_STATE_KIND, ROOT))
    state["task_id"] = "task-missing"
    state["completion_condition"] = ""
    h.ledger.save_record(INTERACTION_STATE_KIND, ROOT, state)
    result = h.service.reconcile(thread_ts=ROOT, message_ts=REPLY)
    assert result["reply_class"] == "MANUAL_ACTION_DONE"
    text = [
        p[1]["text"]
        for p in h.calls
        if p[0] == "chat.postMessage" and p[1].get("thread_ts")
    ][-1]
    assert "Verification remains separate" in text
    assert "Verification condition:" not in text


def test_compatibility_approval_thread_state_is_derived_from_legacy_binding() -> None:
    ledger = TaskLedger()
    task_id = _task(ledger)
    ledger.save_record(
        THREAD_BINDING_KIND,
        ROOT,
        {
            "approval_id": "approval-legacy",
            "task_id": task_id,
            "channel_id": CHANNEL,
            "thread_ts": ROOT,
        },
    )
    notifier, _ = _notifier(ledger)
    service = SlackNativeTriggerApprovalService(
        ledger,
        SlackSocketApprovalConfig(CHANNEL, USER, "michael", APP),
        notifier,
    )
    state = service._interaction_state(ROOT)
    assert state["thread_type"] == "APPROVAL"
    assert state["approval_id"] == "approval-legacy"

    empty = SlackNativeTriggerApprovalService(
        TaskLedger(),
        SlackSocketApprovalConfig(CHANNEL, USER, "michael", APP),
        notifier,
    )
    with pytest.raises(PermissionError, match="not in a governed bound thread"):
        empty._interaction_state("missing-thread")
