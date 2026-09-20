from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .ledger import TaskLedger
from .slack_bot import (
    INTERACTION_REPLY_KIND,
    INTERACTION_STATE_KIND,
    THREAD_BINDING_KIND,
    SlackApprovalNotifier,
)
from .slack_hitl import _parse_thread_decision
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
            raise PermissionError("Slack interactions must be replies in a bound thread")
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
            raise TypeError("Slack did not return a message collection")
        exact = [item for item in messages if isinstance(item, Mapping) and str(item.get("ts") or "") == message_ts]
        if len(exact) != 1:
            raise PermissionError("Slack trigger message could not be reconciled exactly")
        message = dict(exact[0])
        if message.get("edited"):
            raise PermissionError(
                "Edited Slack messages cannot create approval authority or be reconciled as human interaction"
            )
        if str(message.get("thread_ts") or "") != thread_ts:
            raise PermissionError("Slack provider message thread does not match trigger locator")
        self._require_manual_human_message(message)
        return message

    def _require_manual_human_message(self, message: Mapping[str, Any]) -> None:
        if any(message.get(field) for field in ("app_id", "bot_id", "bot_profile")):
            raise PermissionError(
                "Slack interaction is app-authored, not manual human input"
            )
        if str(message.get("subtype") or "").strip():
            raise PermissionError("Slack interaction subtype is not manual human input")
        if str(message.get("user") or "").strip() != self.config.approver_user_id:
            raise PermissionError(
                "Slack interaction was not authored by the configured approver human principal"
            )

    def _interaction_state(self, thread_ts: str) -> dict[str, Any]:
        state = self.ledger.get_record(INTERACTION_STATE_KIND, thread_ts)
        if state is not None:
            return dict(state)
        binding = self.ledger.get_record(THREAD_BINDING_KIND, thread_ts)
        if binding is None:
            raise PermissionError("Slack interaction is not in a governed bound thread")
        binding = dict(binding)
        return {
            "version": "mesh.cos.slack-interaction-state.compat.v1",
            "thread_type": "APPROVAL",
            "task_id": binding.get("task_id"),
            "approval_id": binding.get("approval_id"),
            "requesting_agent": "cos",
            "accountable_owner": "cos",
            "current_task_state": None,
            "response_required": True,
            "valid_response_classes": ["APPROVE", "DENY", "CHANGE", "CHANGES"],
            "explicit_approval_required": True,
            "requested_human_action": "Explicit approval decision",
            "completion_condition": "Canonical approval is decided.",
            "last_processed_reply": None,
            "last_bot_acknowledgment": None,
            "channel_id": self.config.channel_id,
            "thread_ts": thread_ts,
        }

    def _record_acknowledgment(
        self,
        *,
        state: dict[str, Any],
        provider_event_id: str,
        message_ts: str,
        reply_class: str,
        acknowledgment: str,
        authority_mutated: bool,
        result: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        posted = self.notifier.post_thread_reply(str(state["thread_ts"]), acknowledgment)
        task_id = str(state.get("task_id") or "")
        task = self.ledger.get_task(task_id) if task_id else None
        updated_state = dict(state)
        updated_state["last_processed_reply"] = message_ts
        updated_state["last_bot_acknowledgment"] = posted["message_ts"]
        updated_state["last_reply_class"] = reply_class
        if task is not None:
            updated_state["current_task_state"] = task.status.value
        self.ledger.save_record(
            INTERACTION_STATE_KIND,
            str(state["thread_ts"]),
            updated_state,
        )
        record: dict[str, Any] = {
            "version": "mesh.cos.slack-interaction-reply.v1",
            "source": _NATIVE_SOURCE,
            "provider_event_id": provider_event_id,
            "channel_id": self.config.channel_id,
            "thread_ts": str(state["thread_ts"]),
            "message_ts": message_ts,
            "task_id": state.get("task_id"),
            "approval_id": state.get("approval_id"),
            "thread_type": state.get("thread_type"),
            "reply_class": reply_class,
            "provider_identity_verified": True,
            "trigger_is_authority": False,
            "provider_reconciled": True,
            "authority_mutated": authority_mutated,
            "acknowledgment_message_ts": posted["message_ts"],
        }
        if result is not None:
            record["canonical_result"] = dict(result)
        self.ledger.save_record(INTERACTION_REPLY_KIND, provider_event_id, record)
        return record

    @staticmethod
    def _is_completion_text(text: str) -> bool:
        clean = " ".join(text.strip().lower().split())
        return clean in {
            "done",
            "completed",
            "complete",
            "fixed",
            "i repaired it",
            "repaired",
        }

    @staticmethod
    def _is_confirmation_text(text: str) -> bool:
        clean = " ".join(text.strip().lower().split())
        return clean in {
            "confirmed",
            "confirm",
            "yes",
            "looks good",
            "ack",
            "acknowledged",
        }

    def _reconcile_conversation(
        self,
        *,
        state: dict[str, Any],
        text: str,
        provider_event_id: str,
        message_ts: str,
    ) -> dict[str, Any]:
        try:
            disposition, _ = _parse_thread_decision(text)
        except PermissionError:
            disposition = None
        if disposition is not None:
            return self._record_acknowledgment(
                state=state,
                provider_event_id=provider_event_id,
                message_ts=message_ts,
                reply_class="INVALID_AUTHORITY_COMMAND",
                acknowledgment=(
                    "Received, but this thread is not awaiting approval. "
                    "No approval was recorded. This is a "
                    f"{str(state.get('thread_type') or 'conversation').lower()} thread."
                ),
                authority_mutated=False,
            )

        thread_type = str(state.get("thread_type") or "STATUS")
        task_id = str(state.get("task_id") or "")
        task = self.ledger.get_task(task_id) if task_id else None
        requested = str(state.get("requested_human_action") or "").strip()
        completion = str(state.get("completion_condition") or "").strip()

        if thread_type == "MANUAL_ACTION" and self._is_completion_text(text):
            state["manual_completion_reported"] = True
            state["manual_completion_message_ts"] = message_ts
            acknowledgment = (
                "Received. I recorded that the manual action is complete. "
                "Verification remains separate and is the next governed step."
            )
            if completion:
                acknowledgment += f" Verification condition: {completion}"
            reply_class = "MANUAL_ACTION_DONE"
        elif thread_type == "MANUAL_ACTION" and self._is_confirmation_text(text):
            acknowledgment = (
                "Confirmed. No approval was required for this item. "
                "The outstanding action is still: "
                f"{requested or 'complete the requested manual action.'}"
            )
            reply_class = "CONVERSATIONAL_CONFIRMATION"
        elif thread_type == "INFO":
            acknowledgment = "Received. This item required no action or approval."
            reply_class = "INFORMATION_ACKNOWLEDGED"
        elif thread_type == "QUESTION":
            acknowledgment = (
                f"Received for task {task_id}. Your response is recorded as "
                "conversation, not approval."
            )
            reply_class = "QUESTION_RESPONSE"
        else:
            current = (
                task.status.value
                if task is not None
                else str(state.get("current_task_state") or "UNKNOWN")
            )
            next_text = (
                requested
                or completion
                or "No additional human action is currently specified."
            )
            acknowledgment = (
                f"Received. Current task state: {current}. Next: {next_text} "
                "No approval authority was created by this reply."
            )
            reply_class = "CONVERSATIONAL_RESPONSE"

        return self._record_acknowledgment(
            state=state,
            provider_event_id=provider_event_id,
            message_ts=message_ts,
            reply_class=reply_class,
            acknowledgment=acknowledgment,
            authority_mutated=False,
        )

    def _reconcile_approval(
        self,
        *,
        state: dict[str, Any],
        message: Mapping[str, Any],
        provider_event_id: str,
        message_ts: str,
    ) -> dict[str, Any]:
        text = str(message.get("text") or "")
        try:
            disposition, change_detail = _parse_thread_decision(text)
        except PermissionError:
            return self._record_acknowledgment(
                state=state,
                provider_event_id=provider_event_id,
                message_ts=message_ts,
                reply_class="APPROVAL_AMBIGUOUS",
                acknowledgment=(
                    "I received your message. This action requires explicit approval. "
                    "Reply APPROVE, DENY, or CHANGES: <details>."
                ),
                authority_mutated=False,
            )

        event: dict[str, Any] = {
            "type": "message",
            "channel": self.config.channel_id,
            "thread_ts": str(state["thread_ts"]),
            "ts": message_ts,
            "user": message.get("user"),
            "text": text,
        }
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
        result = dict(self.compat.handle_envelope(envelope))
        approval_id = str(
            result.get("approval_id") or state.get("approval_id") or ""
        )
        if approval_id and disposition in {"APPROVE", "DENY"}:
            record = self.ledger.get_record(_NATIVE_DECISION_KIND, approval_id)
            if record is not None:
                result = dict(record)
                result["version"] = "mesh.cos.slack-human-decision.v6"
                result["source"] = _NATIVE_SOURCE
                result["trigger_is_authority"] = False
                result["provider_reconciled"] = True
                self.ledger.save_record(_NATIVE_DECISION_KIND, approval_id, result)
        if disposition == "APPROVE":
            acknowledgment = (
                f"Approved. Approval {approval_id} is recorded. "
                "The governed workflow may now continue within the approved scope."
            )
            reply_class = "APPROVAL_APPROVED"
            mutated = True
        elif disposition == "DENY":
            acknowledgment = (
                f"Denied. Approval {approval_id} is recorded as rejected. "
                "No action is authorized by this approval."
            )
            reply_class = "APPROVAL_DENIED"
            mutated = True
        elif change_detail is not None:
            acknowledgment = (
                "Change request captured. The prior approval is superseded. "
                "A revised request requires a new immutable approval before "
                "consequential action."
            )
            reply_class = "APPROVAL_CHANGES_REQUESTED"
            mutated = True
        else:
            state["last_processed_reply"] = message_ts
            state["last_reply_class"] = "APPROVAL_CHANGE_STARTED"
            prompt_ts = str(result.get("prompt_message_ts") or "")
            if prompt_ts:
                state["last_bot_acknowledgment"] = prompt_ts
            self.ledger.save_record(
                INTERACTION_STATE_KIND,
                str(state["thread_ts"]),
                state,
            )
            interaction = {
                "version": "mesh.cos.slack-interaction-reply.v1",
                "source": _NATIVE_SOURCE,
                "provider_event_id": provider_event_id,
                "channel_id": self.config.channel_id,
                "thread_ts": str(state["thread_ts"]),
                "message_ts": message_ts,
                "task_id": state.get("task_id"),
                "approval_id": state.get("approval_id"),
                "thread_type": "APPROVAL",
                "reply_class": "APPROVAL_CHANGE_STARTED",
                "provider_identity_verified": True,
                "trigger_is_authority": False,
                "provider_reconciled": True,
                "authority_mutated": False,
                "canonical_result": result,
            }
            if prompt_ts:
                interaction["acknowledgment_message_ts"] = prompt_ts
            self.ledger.save_record(
                INTERACTION_REPLY_KIND,
                provider_event_id,
                interaction,
            )
            result["trigger_is_authority"] = False
            result["provider_reconciled"] = True
            return result

        self._record_acknowledgment(
            state=state,
            provider_event_id=provider_event_id,
            message_ts=message_ts,
            reply_class=reply_class,
            acknowledgment=acknowledgment,
            authority_mutated=mutated,
            result=result,
        )
        result["trigger_is_authority"] = False
        result["provider_reconciled"] = True
        return result

    def reconcile(self, *, thread_ts: str, message_ts: str) -> dict[str, Any]:
        provider_event_id = f"native-slack:{self.config.channel_id}:{message_ts}"
        prior = self.ledger.get_record(INTERACTION_REPLY_KIND, provider_event_id)
        if prior is not None:
            replay = dict(prior)
            canonical = replay.get("canonical_result")
            if isinstance(canonical, Mapping):
                return dict(canonical)
            return replay
        message = self._provider_message(thread_ts=thread_ts, message_ts=message_ts)
        state = self._interaction_state(thread_ts)
        if str(state.get("thread_type") or "") == "APPROVAL":
            return self._reconcile_approval(
                state=state,
                message=message,
                provider_event_id=provider_event_id,
                message_ts=message_ts,
            )
        return self._reconcile_conversation(
            state=state,
            text=str(message.get("text") or ""),
            provider_event_id=provider_event_id,
            message_ts=message_ts,
        )
