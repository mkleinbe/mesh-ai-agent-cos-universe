from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .approval import ApprovalService
from .ledger import TaskLedger
from .models import new_id, utcnow
from .slack_bot import CHANGE_REQUEST_KIND, THREAD_BINDING_KIND, SlackApprovalNotifier
from .slack_hitl import MICHAEL_PRINCIPAL, SlackHITLConfig, _parse_thread_decision

_PAYLOAD_FINGERPRINT_RE = re.compile(r"\bpayload_fingerprint=(?P<fingerprint>[A-Fa-f0-9]{64})\b")
_CHANGE_SESSION_KIND = "approval_change_session"
_DECISION_KIND = "approval_slack_socket_decision"
_BUTTON_DISPOSITIONS = {
    "mesh_approval_approve": "APPROVE",
    "mesh_approval_deny": "DENY",
    "mesh_approval_change": "CHANGE",
}


@dataclass(frozen=True, slots=True)
class SlackSocketApprovalConfig:
    channel_id: str
    approver_user_id: str
    approver_principal: str = MICHAEL_PRINCIPAL
    app_id: str = ""

    def __post_init__(self) -> None:
        if not self.channel_id.strip():
            raise RuntimeError("Slack approval channel ID is required")
        if not self.approver_user_id.strip():
            raise RuntimeError("Slack approval user ID is required")
        if self.approver_principal != MICHAEL_PRINCIPAL:
            raise RuntimeError("Slack approval principal must be michael")
        if self.app_id and not self.app_id.startswith("A"):
            raise RuntimeError("Slack app ID must begin with A")

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
    ) -> SlackSocketApprovalConfig:
        values = env if env is not None else os.environ
        hitl = SlackHITLConfig.from_env(values)
        return cls(
            channel_id=hitl.channel_id,
            approver_user_id=hitl.approver_user_id,
            approver_principal=hitl.approver_principal,
            app_id=str(values.get("MESH_COS_SLACK_APP_ID", "")).strip(),
        )


class SlackSocketApprovalService:
    """Provider-authenticated Slack HITL ingress for approval and change workflows.

    The dedicated Slack bot creates the approval message and canonical thread binding.
    Socket Mode then supplies provider-authenticated Events API messages and Block Kit
    interactions. Human identity, channel, app, bound thread, pending approval, and the
    immutable payload fingerprint are all revalidated before authority changes.
    """

    def __init__(
        self,
        ledger: TaskLedger,
        config: SlackSocketApprovalConfig,
        *,
        notifier: SlackApprovalNotifier | None = None,
    ) -> None:
        self.ledger = ledger
        self.config = config
        self.approvals = ApprovalService(ledger)
        self.notifier = notifier

    @staticmethod
    def _require_str(payload: Mapping[str, Any], field: str) -> str:
        value = str(payload.get(field) or "").strip()
        if not value:
            raise PermissionError(f"Slack Socket Mode envelope is missing {field}")
        return value

    @staticmethod
    def _canonical_fingerprint(approval: Mapping[str, Any]) -> str:
        action = str(approval.get("action") or "")
        match = _PAYLOAD_FINGERPRINT_RE.search(action)
        if match is None:
            raise PermissionError(
                "Canonical approval is missing an immutable payload_fingerprint binding"
            )
        return match.group("fingerprint").lower()

    def _validate_app(self, payload: Mapping[str, Any]) -> None:
        if not self.config.app_id:
            return
        if self._require_str(payload, "api_app_id") != self.config.app_id:
            raise PermissionError("Slack app identity mismatch")

    def _binding(self, thread_ts: str) -> dict[str, Any]:
        binding = self.ledger.get_record(THREAD_BINDING_KIND, thread_ts)
        if binding is None:
            raise PermissionError("Slack approval interaction is not in a bound approval thread")
        binding = dict(binding)
        if binding.get("channel_id") != self.config.channel_id:
            raise PermissionError("Slack approval thread binding channel mismatch")
        approval_id = str(binding.get("approval_id") or "").strip()
        if not approval_id:
            raise PermissionError("Slack approval thread binding is invalid")
        return binding

    def _require_pending_bound_approval(
        self,
        binding: Mapping[str, Any],
    ) -> tuple[str, dict[str, Any], str]:
        approval_id = str(binding.get("approval_id") or "").strip()
        approval = self.ledger.get_record("approval", approval_id)
        if approval is None:
            raise KeyError(approval_id)
        approval = dict(approval)
        if approval.get("status") != "PENDING":
            raise ValueError("Approval already decided")
        if approval.get("approval_owner") != self.config.approver_principal:
            raise PermissionError("Canonical approval owner is not the configured human principal")
        fingerprint = self._canonical_fingerprint(approval)
        if fingerprint != str(binding.get("payload_fingerprint") or "").lower():
            raise PermissionError("Canonical approval payload fingerprint changed after Slack binding")
        return approval_id, approval, fingerprint

    @staticmethod
    def _require_manual_human_message(event: Mapping[str, Any]) -> None:
        if any(event.get(field) for field in ("app_id", "bot_id", "bot_profile")):
            raise PermissionError("Slack approval reply is app-authored, not manual human input")
        if str(event.get("subtype") or "").strip():
            raise PermissionError("Slack approval reply subtype is not manual human input")

    def _require_approver_user(self, user_id: str) -> None:
        if user_id != self.config.approver_user_id:
            raise PermissionError(
                "Slack approval interaction was not authored by the configured approver"
            )

    def _decision_replay(
        self,
        approval_id: str,
        provider_event_id: str,
    ) -> dict[str, Any] | None:
        prior = self.ledger.get_record(_DECISION_KIND, approval_id)
        if prior is None:
            return None
        prior = dict(prior)
        if prior.get("provider_event_id") == provider_event_id:
            return prior
        raise ValueError("Approval already decided by a different provider interaction")

    def _finalize_decision(
        self,
        *,
        binding: Mapping[str, Any],
        disposition: str,
        envelope_id: str,
        provider_event_id: str,
        message_ts: str | None = None,
    ) -> dict[str, Any]:
        approval_id = str(binding.get("approval_id") or "").strip()
        replay = self._decision_replay(approval_id, provider_event_id)
        if replay is not None:
            return replay
        approval_id, _, fingerprint = self._require_pending_bound_approval(binding)
        if disposition not in {"APPROVE", "DENY"}:
            raise PermissionError("Only APPROVE or DENY may finalize an approval")
        approved = disposition == "APPROVE"
        decided = self.approvals.decide(
            approval_id,
            actor=self.config.approver_principal,
            approved=approved,
            reason=(
                "Provider-authenticated Slack human interaction "
                f"event={provider_event_id} disposition={disposition}"
            ),
        )
        record = {
            "version": "mesh.cos.slack-human-decision.v5",
            "source": "SLACK_SOCKET_MODE_HUMAN_INTERACTION",
            "approval_id": approval_id,
            "task_id": decided.task_id,
            "disposition": disposition,
            "canonical_principal": self.config.approver_principal,
            "provider_identity_verified": True,
            "channel_id": self.config.channel_id,
            "thread_ts": str(binding["thread_ts"]),
            "envelope_id": envelope_id,
            "provider_event_id": provider_event_id,
            "payload_fingerprint": fingerprint,
            "recorded_at": utcnow(),
        }
        if message_ts:
            record["message_ts"] = message_ts
        self.ledger.save_record(_DECISION_KIND, approval_id, record)
        if self.notifier is not None:
            self.notifier.mark_resolved(approval_id, disposition)
        return record

    def _begin_change(
        self,
        *,
        binding: Mapping[str, Any],
        envelope_id: str,
        provider_event_id: str,
    ) -> dict[str, Any]:
        approval_id, approval, fingerprint = self._require_pending_bound_approval(binding)
        prior = self.ledger.get_record(_CHANGE_SESSION_KIND, approval_id)
        if prior is not None:
            prior = dict(prior)
            if prior.get("status") == "AWAITING_CHANGE_INPUT":
                return prior
            if prior.get("provider_event_id") == provider_event_id:
                return prior
            raise ValueError("Approval change session already completed")
        session = {
            "version": "mesh.cos.slack-change-session.v1",
            "status": "AWAITING_CHANGE_INPUT",
            "approval_id": approval_id,
            "task_id": approval.get("task_id"),
            "channel_id": self.config.channel_id,
            "thread_ts": str(binding["thread_ts"]),
            "payload_fingerprint": fingerprint,
            "canonical_principal": self.config.approver_principal,
            "provider_identity_verified": True,
            "envelope_id": envelope_id,
            "provider_event_id": provider_event_id,
            "prompt": "What would you like to change?",
            "prompt_delivery": "NOT_ATTEMPTED",
            "recorded_at": utcnow(),
        }
        self.ledger.save_record(_CHANGE_SESSION_KIND, approval_id, session)
        if self.notifier is not None:
            try:
                posted = self.notifier.post_thread_reply(
                    str(binding["thread_ts"]), "What would you like to change?"
                )
                session["prompt_delivery"] = "POSTED"
                session["prompt_message_ts"] = posted["message_ts"]
            except RuntimeError:
                session["prompt_delivery"] = "FAILED"
            self.ledger.save_record(_CHANGE_SESSION_KIND, approval_id, session)
        return session

    def _capture_change_instruction(
        self,
        *,
        binding: Mapping[str, Any],
        envelope_id: str,
        provider_event_id: str,
        message_ts: str,
        instruction: str,
    ) -> dict[str, Any]:
        approval_id, approval, fingerprint = self._require_pending_bound_approval(binding)
        session = self.ledger.get_record(_CHANGE_SESSION_KIND, approval_id)
        if session is None:
            raise PermissionError("Slack approval is not awaiting change input")
        session = dict(session)
        if session.get("status") == "CAPTURED":
            request_id = str(session.get("change_request_id") or "")
            prior = self.ledger.get_record(CHANGE_REQUEST_KIND, request_id) if request_id else None
            if prior is not None and prior.get("provider_event_id") == provider_event_id:
                return dict(prior)
            raise ValueError("Approval change input already captured")
        if session.get("status") != "AWAITING_CHANGE_INPUT":
            raise ValueError("Approval change session is not accepting input")
        clean_instruction = instruction.strip()
        if not clean_instruction:
            raise PermissionError("Change instruction cannot be empty")
        change_request_id = new_id("change")
        record = {
            "version": "mesh.cos.approval-change-request.v1",
            "change_request_id": change_request_id,
            "status": "PENDING_AGENT_REVISION",
            "approval_id": approval_id,
            "task_id": approval.get("task_id"),
            "change_instruction": clean_instruction,
            "canonical_principal": self.config.approver_principal,
            "provider_identity_verified": True,
            "channel_id": self.config.channel_id,
            "thread_ts": str(binding["thread_ts"]),
            "envelope_id": envelope_id,
            "provider_event_id": provider_event_id,
            "message_ts": message_ts,
            "payload_fingerprint": fingerprint,
            "recorded_at": utcnow(),
        }
        self.approvals.decide(
            approval_id,
            actor=self.config.approver_principal,
            approved=False,
            reason=f"SUPERSEDED_BY_CHANGE change_request={change_request_id}",
        )
        self.ledger.save_record(CHANGE_REQUEST_KIND, change_request_id, record)
        session["status"] = "CAPTURED"
        session["change_request_id"] = change_request_id
        session["captured_at"] = utcnow()
        session["provider_event_id"] = provider_event_id
        self.ledger.save_record(_CHANGE_SESSION_KIND, approval_id, session)
        if self.notifier is not None:
            self.notifier.mark_resolved(approval_id, "CHANGE REQUESTED")
            try:
                self.notifier.post_thread_reply(
                    str(binding["thread_ts"]),
                    "Change request captured. I’ll revise the request and return a new approval.",
                )
            except RuntimeError:
                pass
        return record

    def _handle_events_api(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        envelope_id = self._require_str(envelope, "envelope_id")
        payload = envelope.get("payload")
        if not isinstance(payload, Mapping):
            raise PermissionError("Slack Socket Mode envelope payload is invalid")
        if self._require_str(payload, "type") != "event_callback":
            raise PermissionError("Slack Events API payload is not an event_callback")
        self._validate_app(payload)
        event_id = self._require_str(payload, "event_id")
        event = payload.get("event")
        if not isinstance(event, Mapping):
            raise PermissionError("Slack Events API event payload is invalid")
        if self._require_str(event, "type") != "message":
            raise PermissionError("Slack approval ingress accepts message events only")
        if self._require_str(event, "channel") != self.config.channel_id:
            raise PermissionError("Slack approval channel mismatch")
        thread_ts = str(event.get("thread_ts") or "").strip()
        if not thread_ts:
            return {
                "version": "mesh.cos.slack-thread-event.v2",
                "source": "SLACK_SOCKET_MODE_EVENT",
                "status": "IGNORED",
                "reason": "ROOT_OR_UNTHREADED_MESSAGE",
            }
        binding = self._binding(thread_ts)
        self._require_manual_human_message(event)
        self._require_approver_user(self._require_str(event, "user"))
        message_ts = self._require_str(event, "ts")
        text = self._require_str(event, "text")
        approval_id = str(binding["approval_id"])
        session = self.ledger.get_record(_CHANGE_SESSION_KIND, approval_id)
        if session is not None and session.get("status") == "AWAITING_CHANGE_INPUT":
            return self._capture_change_instruction(
                binding=binding,
                envelope_id=envelope_id,
                provider_event_id=event_id,
                message_ts=message_ts,
                instruction=text,
            )
        disposition, _ = _parse_thread_decision(text)
        if disposition == "CHANGE":
            return self._begin_change(
                binding=binding,
                envelope_id=envelope_id,
                provider_event_id=event_id,
            )
        return self._finalize_decision(
            binding=binding,
            disposition=disposition,
            envelope_id=envelope_id,
            provider_event_id=event_id,
            message_ts=message_ts,
        )

    def _handle_block_actions(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        envelope_id = self._require_str(envelope, "envelope_id")
        payload = envelope.get("payload")
        if not isinstance(payload, Mapping):
            raise PermissionError("Slack interactive payload is invalid")
        if self._require_str(payload, "type") != "block_actions":
            raise PermissionError("Slack interactive payload is not block_actions")
        self._validate_app(payload)
        user = payload.get("user")
        if not isinstance(user, Mapping):
            raise PermissionError("Slack block action user identity is missing")
        self._require_approver_user(self._require_str(user, "id"))
        channel = payload.get("channel")
        if not isinstance(channel, Mapping):
            raise PermissionError("Slack block action channel identity is missing")
        if self._require_str(channel, "id") != self.config.channel_id:
            raise PermissionError("Slack approval channel mismatch")
        container = payload.get("container")
        if not isinstance(container, Mapping):
            raise PermissionError("Slack block action container is missing")
        if self._require_str(container, "channel_id") != self.config.channel_id:
            raise PermissionError("Slack block action container channel mismatch")
        thread_ts = self._require_str(container, "message_ts")
        binding = self._binding(thread_ts)
        actions = payload.get("actions")
        if not isinstance(actions, list) or len(actions) != 1 or not isinstance(actions[0], Mapping):
            raise PermissionError("Slack approval requires exactly one Block Kit action")
        action = actions[0]
        action_id = self._require_str(action, "action_id")
        disposition = _BUTTON_DISPOSITIONS.get(action_id)
        if disposition is None:
            raise PermissionError("Slack Block Kit action is not an approval control")
        if self._require_str(action, "value") != str(binding["approval_id"]):
            raise PermissionError("Slack Block Kit approval value does not match bound approval")
        provider_event_id = envelope_id
        if disposition == "CHANGE":
            return self._begin_change(
                binding=binding,
                envelope_id=envelope_id,
                provider_event_id=provider_event_id,
            )
        return self._finalize_decision(
            binding=binding,
            disposition=disposition,
            envelope_id=envelope_id,
            provider_event_id=provider_event_id,
        )

    def handle_envelope(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        envelope_type = str(envelope.get("type") or "")
        if envelope_type == "events_api":
            return self._handle_events_api(envelope)
        if envelope_type == "interactive":
            return self._handle_block_actions(envelope)
        raise PermissionError("Canonical Slack HITL requires events_api or interactive envelope")
