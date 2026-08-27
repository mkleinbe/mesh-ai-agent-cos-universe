from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .ledger import TaskLedger
from .slack_bot import SlackApprovalNotifier
from .slack_socket_approval import SlackSocketApprovalConfig, SlackSocketApprovalService

_NATIVE_DECISION_KIND = "approval_slack_socket_decision"
_NATIVE_SOURCE = "CHATGPT_NATIVE_SLACK_EVENT_TRIGGER_RECONCILIATION"


class SlackNativeTriggerApprovalService:
    """Reconcile a ChatGPT-native Slack wake-up against provider state.

    The ChatGPT task trigger is intentionally treated only as a wake-up and locator.
    Decision text, user identity, channel, thread binding, approval state, and immutable
    payload fingerprint are re-derived server-side before canonical authority changes.
    """

    def __init__(
        self,
        ledger: TaskLedger,
        config: SlackSocketApprovalConfig,
        notifier: SlackApprovalNotifier,
    ) -> None:
        self.ledger = ledger
        self.config = config
        self.notifier = notifier
        self.compat = SlackSocketApprovalService(ledger, config, notifier=notifier)

    def _provider_message(self, *, thread_ts: str, message_ts: str) -> dict[str, Any]:
        if not thread_ts.strip() or not message_ts.strip():
            raise PermissionError("Slack trigger reconciliation requires thread and message timestamps")
        if thread_ts == message_ts:
            raise PermissionError("Slack approval decisions must be replies in a bound thread")
        response = self.notifier.api.transport(
            "conversations.replies",
            {
                "channel": self.config.channel_id,
                "ts": thread_ts,
                "oldest": message_ts,
                "latest": message_ts,
                "inclusive": True,
                "limit": 1,
            },
            self.notifier.api.token,
        )
        messages = response.get("messages")
        if not isinstance(messages, list):
            raise RuntimeError("Slack did not return a message collection")
        exact = [item for item in messages if isinstance(item, Mapping) and str(item.get("ts") or "") == message_ts]
        if len(exact) != 1:
            raise PermissionError("Slack trigger message could not be reconciled exactly")
        message = dict(exact[0])
        if message.get("edited"):
            raise PermissionError("Edited Slack messages cannot create approval authority")
        if str(message.get("thread_ts") or "") != thread_ts:
            raise PermissionError("Slack provider message thread does not match trigger locator")
        return message

    def reconcile(self, *, thread_ts: str, message_ts: str) -> dict[str, Any]:
        message = self._provider_message(thread_ts=thread_ts, message_ts=message_ts)
        provider_event_id = f"native-slack:{self.config.channel_id}:{message_ts}"
        event: dict[str, Any] = {
            "type": "message",
            "channel": self.config.channel_id,
            "thread_ts": thread_ts,
            "ts": message_ts,
            "user": message.get("user"),
            "text": message.get("text"),
        }
        for field in ("app_id", "bot_id", "bot_profile", "subtype"):
            if field in message:
                event[field] = message[field]
        envelope = {
            "type": "events_api",
            "envelope_id": provider_event_id,
            "payload": {
                "type": "event_callback",
                "api_app_id": self.config.app_id,
                "event_id": provider_event_id,
                "event": event,
            },
        }
        result = self.compat.handle_envelope(envelope)
        approval_id = str(result.get("approval_id") or "")
        if approval_id and result.get("disposition") in {"APPROVE", "DENY"}:
            record = self.ledger.get_record(_NATIVE_DECISION_KIND, approval_id)
            if record is not None:
                updated = dict(record)
                updated["version"] = "mesh.cos.slack-human-decision.v6"
                updated["source"] = _NATIVE_SOURCE
                updated["trigger_is_authority"] = False
                updated["provider_reconciled"] = True
                self.ledger.save_record(_NATIVE_DECISION_KIND, approval_id, updated)
                return updated
        result = dict(result)
        result["trigger_is_authority"] = False
        result["provider_reconciled"] = True
        return result
