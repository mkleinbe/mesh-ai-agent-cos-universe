from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .approval import ApprovalService
from .ledger import TaskLedger
from .models import utcnow
from .slack_hitl import MICHAEL_PRINCIPAL, SlackHITLConfig, _parse_thread_decision

_PAYLOAD_FINGERPRINT_RE = re.compile(r"\bpayload_fingerprint=(?P<fingerprint>[A-Fa-f0-9]{64})\b")
_APPROVAL_MARKER_RE = re.compile(
    r"\bApproval\s+ID\s*:\s*[`*_]?(?P<approval>approval-[A-Za-z0-9]+|APR-[A-Za-z0-9._:-]+)[`*_]?",
    re.IGNORECASE,
)
_THREAD_BINDING_KIND = "approval_slack_thread_binding"
_DECISION_KIND = "approval_slack_socket_decision"


@dataclass(frozen=True, slots=True)
class SlackSocketApprovalConfig:
    channel_id: str
    approver_user_id: str
    approver_principal: str = MICHAEL_PRINCIPAL

    def __post_init__(self) -> None:
        if not self.channel_id.strip():
            raise RuntimeError("Slack approval channel ID is required")
        if not self.approver_user_id.strip():
            raise RuntimeError("Slack approval user ID is required")
        if self.approver_principal != MICHAEL_PRINCIPAL:
            raise RuntimeError("Slack approval principal must be michael")

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
        )


class SlackSocketApprovalService:
    """Trusted human-principal ingress for provider-authenticated Slack events.

    Connected Slack collaboration is informational only. v4.1.17 observes provider-
    authenticated Socket Mode message events to bind an approval-notice thread and then
    accepts a simple manual reply from the configured human approver. App/bot-authored
    replies, wrong routes, unbound threads, and replay conflicts fail closed.
    """

    def __init__(self, ledger: TaskLedger, config: SlackSocketApprovalConfig) -> None:
        self.ledger = ledger
        self.config = config
        self.approvals = ApprovalService(ledger)

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

    def _provider_message(
        self,
        envelope: Mapping[str, Any],
    ) -> tuple[str, str, Mapping[str, Any]]:
        if str(envelope.get("type") or "") != "events_api":
            raise PermissionError("Canonical Slack approval requires an events_api envelope")
        envelope_id = self._require_str(envelope, "envelope_id")
        payload = envelope.get("payload")
        if not isinstance(payload, Mapping):
            raise PermissionError("Slack Socket Mode envelope payload is invalid")
        if self._require_str(payload, "type") != "event_callback":
            raise PermissionError("Slack Events API payload is not an event_callback")
        event_id = self._require_str(payload, "event_id")
        event = payload.get("event")
        if not isinstance(event, Mapping):
            raise PermissionError("Slack Events API event payload is invalid")
        if self._require_str(event, "type") != "message":
            raise PermissionError("Slack approval ingress accepts message events only")
        if self._require_str(event, "channel") != self.config.channel_id:
            raise PermissionError("Slack approval channel mismatch")
        return envelope_id, event_id, event

    @staticmethod
    def _approval_marker(text: str) -> str | None:
        matches = {match.group("approval") for match in _APPROVAL_MARKER_RE.finditer(text)}
        if not matches:
            return None
        if len(matches) != 1:
            raise PermissionError("Slack approval notice contains an ambiguous Approval ID")
        return next(iter(matches))

    def _bind_thread(
        self,
        *,
        envelope_id: str,
        event_id: str,
        event: Mapping[str, Any],
    ) -> dict[str, Any]:
        text = self._require_str(event, "text")
        approval_id = self._approval_marker(text)
        if approval_id is None:
            return {
                "version": "mesh.cos.slack-thread-event.v1",
                "source": "SLACK_SOCKET_MODE_EVENT",
                "status": "IGNORED",
                "reason": "NO_APPROVAL_MARKER",
            }
        thread_ts = self._require_str(event, "ts")
        prior_thread = self.ledger.get_record(_THREAD_BINDING_KIND, thread_ts)
        if prior_thread is not None:
            prior_thread = dict(prior_thread)
            if prior_thread.get("approval_id") == approval_id:
                return prior_thread
            raise ValueError("Slack approval thread is already bound to another approval")

        for prior in self.ledger.list_records(_THREAD_BINDING_KIND):
            if prior.get("approval_id") == approval_id:
                if prior.get("thread_ts") == thread_ts:
                    return dict(prior)
                raise ValueError("Approval is already bound to another Slack thread")

        approval = self.ledger.get_record("approval", approval_id)
        if approval is None:
            raise KeyError(approval_id)
        approval = dict(approval)
        if approval.get("status") != "PENDING":
            raise ValueError("Approval is not pending")
        if approval.get("approval_owner") != self.config.approver_principal:
            raise PermissionError("Canonical approval owner is not the configured human principal")
        payload_fingerprint = self._canonical_fingerprint(approval)

        record = {
            "version": "mesh.cos.slack-thread-binding.v1",
            "source": "SLACK_SOCKET_MODE_THREAD_BINDING",
            "approval_id": approval_id,
            "task_id": approval.get("task_id"),
            "channel_id": self.config.channel_id,
            "thread_ts": thread_ts,
            "envelope_id": envelope_id,
            "provider_event_id": event_id,
            "payload_fingerprint": payload_fingerprint,
            "recorded_at": utcnow(),
        }
        self.ledger.save_record(_THREAD_BINDING_KIND, thread_ts, record)
        return record

    @staticmethod
    def _require_manual_human_message(event: Mapping[str, Any]) -> None:
        if any(event.get(field) for field in ("app_id", "bot_id", "bot_profile")):
            raise PermissionError("Slack approval reply is app-authored, not manual human input")
        if str(event.get("subtype") or "").strip():
            raise PermissionError("Slack approval reply subtype is not manual human input")

    def _decide_from_reply(
        self,
        *,
        envelope_id: str,
        event_id: str,
        event: Mapping[str, Any],
    ) -> dict[str, Any]:
        thread_ts = self._require_str(event, "thread_ts")
        binding = self.ledger.get_record(_THREAD_BINDING_KIND, thread_ts)
        if binding is None:
            raise PermissionError("Slack approval reply is not in a bound approval thread")
        binding = dict(binding)
        approval_id = str(binding.get("approval_id") or "").strip()
        if not approval_id:
            raise PermissionError("Slack approval thread binding is invalid")

        prior = self.ledger.get_record(_DECISION_KIND, approval_id)
        if prior is not None:
            prior = dict(prior)
            if prior.get("provider_event_id") == event_id:
                return prior
            raise ValueError("Approval already decided by a different provider interaction")

        self._require_manual_human_message(event)
        if self._require_str(event, "user") != self.config.approver_user_id:
            raise PermissionError(
                "Slack approval interaction was not authored by the configured approver"
            )
        disposition, requested_change = _parse_thread_decision(
            self._require_str(event, "text")
        )

        approval = self.ledger.get_record("approval", approval_id)
        if approval is None:
            raise KeyError(approval_id)
        approval = dict(approval)
        if approval.get("status") != "PENDING":
            raise ValueError("Approval already decided")
        if approval.get("approval_owner") != self.config.approver_principal:
            raise PermissionError("Canonical approval owner is not the configured human principal")
        payload_fingerprint = self._canonical_fingerprint(approval)
        if payload_fingerprint != str(binding.get("payload_fingerprint") or "").lower():
            raise PermissionError("Canonical approval payload fingerprint changed after thread binding")

        approved = disposition == "APPROVE"
        reason = (
            "Provider-authenticated Slack Socket Mode thread reply "
            f"event={event_id} disposition={disposition}"
        )
        if requested_change:
            reason += f" requested_change={requested_change}"
        decided = self.approvals.decide(
            approval_id,
            actor=self.config.approver_principal,
            approved=approved,
            reason=reason,
        )
        record = {
            "version": "mesh.cos.slack-human-decision.v4",
            "source": "SLACK_SOCKET_MODE_THREAD_REPLY",
            "approval_id": approval_id,
            "task_id": decided.task_id,
            "disposition": disposition,
            "requested_change": requested_change,
            "canonical_principal": self.config.approver_principal,
            "provider_identity_verified": True,
            "channel_id": self.config.channel_id,
            "thread_ts": thread_ts,
            "envelope_id": envelope_id,
            "provider_event_id": event_id,
            "message_ts": self._require_str(event, "ts"),
            "payload_fingerprint": payload_fingerprint,
            "recorded_at": utcnow(),
        }
        self.ledger.save_record(_DECISION_KIND, approval_id, record)
        return record

    def handle_envelope(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        envelope_id, event_id, event = self._provider_message(envelope)
        if str(event.get("thread_ts") or "").strip():
            return self._decide_from_reply(
                envelope_id=envelope_id,
                event_id=event_id,
                event=event,
            )
        return self._bind_thread(
            envelope_id=envelope_id,
            event_id=event_id,
            event=event,
        )
