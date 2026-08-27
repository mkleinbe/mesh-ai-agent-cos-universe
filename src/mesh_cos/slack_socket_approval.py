from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .approval import ApprovalService
from .ledger import TaskLedger
from .models import utcnow
from .slack_hitl import MICHAEL_PRINCIPAL, SlackHITLConfig, _parse_decision

DEFAULT_APPROVAL_COMMAND = "/mesh-approval"
_PAYLOAD_FINGERPRINT_RE = re.compile(r"\bpayload_fingerprint=(?P<fingerprint>[A-Fa-f0-9]{64})\b")


@dataclass(frozen=True, slots=True)
class SlackSocketApprovalConfig:
    channel_id: str
    approver_user_id: str
    approver_principal: str = MICHAEL_PRINCIPAL
    command: str = DEFAULT_APPROVAL_COMMAND

    def __post_init__(self) -> None:
        if not self.channel_id.strip():
            raise RuntimeError("Slack approval channel ID is required")
        if not self.approver_user_id.strip():
            raise RuntimeError("Slack approval user ID is required")
        if self.approver_principal != MICHAEL_PRINCIPAL:
            raise RuntimeError("Slack approval principal must be michael")
        if self.command != DEFAULT_APPROVAL_COMMAND:
            raise RuntimeError("Slack approval command must be /mesh-approval")

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
            command=str(
                values.get("MESH_COS_SLACK_APPROVAL_COMMAND", DEFAULT_APPROVAL_COMMAND)
            ).strip(),
        )


class SlackSocketApprovalService:
    """Trusted human-principal ingress for Slack Socket Mode slash commands.

    Slack collaboration and approval-request messages are informational only. They may be
    created by the connected Slack integration and are deliberately outside the approval
    authority boundary. Only a provider-authenticated ``slash_commands`` envelope received
    over the separately authenticated Socket Mode connection can become a canonical human
    approval decision.
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

    def handle_envelope(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        if str(envelope.get("type") or "") != "slash_commands":
            raise PermissionError("Canonical Slack approval requires a slash_commands envelope")
        envelope_id = self._require_str(envelope, "envelope_id")
        payload = envelope.get("payload")
        if not isinstance(payload, Mapping):
            raise PermissionError("Slack Socket Mode envelope payload is invalid")
        if self._require_str(payload, "channel_id") != self.config.channel_id:
            raise PermissionError("Slack approval channel mismatch")
        if self._require_str(payload, "user_id") != self.config.approver_user_id:
            raise PermissionError("Slack approval interaction was not authored by the configured approver")
        if self._require_str(payload, "command") != self.config.command:
            raise PermissionError("Slack approval command mismatch")
        trigger_id = self._require_str(payload, "trigger_id")
        text = self._require_str(payload, "text")

        candidate = text.split(maxsplit=1)
        if len(candidate) < 2:
            raise PermissionError("Slack approval command is missing an Approval ID")
        approval_id = candidate[1].split(":", 1)[0].strip()
        disposition, requested_change = _parse_decision(text, approval_id)

        prior = self.ledger.get_record("approval_slack_socket_decision", approval_id)
        if prior is not None:
            prior = dict(prior)
            if prior.get("envelope_id") == envelope_id:
                return prior
            raise ValueError("Approval already decided by a different provider interaction")

        approval = self.ledger.get_record("approval", approval_id)
        if approval is None:
            raise KeyError(approval_id)
        approval = dict(approval)
        if approval.get("status") != "PENDING":
            raise ValueError("Approval already decided")
        if approval.get("approval_owner") != self.config.approver_principal:
            raise PermissionError("Canonical approval owner is not the configured human principal")
        payload_fingerprint = self._canonical_fingerprint(approval)

        approved = disposition == "APPROVE"
        reason = (
            "Provider-authenticated Slack Socket Mode slash command "
            f"envelope={envelope_id} trigger={trigger_id} disposition={disposition}"
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
            "version": "mesh.cos.slack-human-decision.v3",
            "source": "SLACK_SOCKET_MODE_SLASH_COMMAND",
            "approval_id": approval_id,
            "task_id": decided.task_id,
            "disposition": disposition,
            "requested_change": requested_change,
            "canonical_principal": self.config.approver_principal,
            "provider_identity_verified": True,
            "channel_id": self.config.channel_id,
            "command": self.config.command,
            "envelope_id": envelope_id,
            "trigger_id": trigger_id,
            "payload_fingerprint": payload_fingerprint,
            "recorded_at": utcnow(),
        }
        self.ledger.save_record("approval_slack_socket_decision", approval_id, record)
        return record
