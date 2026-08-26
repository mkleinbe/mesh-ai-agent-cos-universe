from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ledger import TaskLedger
from .models import utcnow
from .slack import SlackWebClient

CHATGPT_SLACK_USER_ID = "U0BKV7Z8M96"
CHATGPT_AGENTS_SLACK_USER_ID = "U0BN8V2BU9Z"
MICHAEL_PRINCIPAL = "michael"
DEFAULT_ALLOWED_NOTICE_AUTHORS = frozenset(
    {CHATGPT_SLACK_USER_ID, CHATGPT_AGENTS_SLACK_USER_ID}
)

_DECISION_RE = re.compile(
    r"^(?P<verb>APPROVE|REJECT)\s+(?P<approval>approval-[A-Za-z0-9]+|APR-[A-Za-z0-9._:-]+)\s*$"
)
_CHANGES_RE = re.compile(
    r"^CHANGES\s+(?P<approval>approval-[A-Za-z0-9]+|APR-[A-Za-z0-9._:-]+):\s*(?P<change>\S(?:.*\S)?)\s*$"
)


def _configured_approver_user_id(values: Mapping[str, str]) -> str:
    direct = str(values.get("MESH_COS_SLACK_APPROVER_USER_ID", "")).strip()
    if direct:
        return direct
    identity_file = str(values.get("MESH_COS_SLACK_APPROVER_USER_ID_FILE", "")).strip()
    if not identity_file:
        return ""
    path = Path(identity_file).expanduser()
    if not path.is_file():
        raise RuntimeError("Slack approver identity file is unavailable")
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError("Slack approver identity file is empty")
    return value


@dataclass(frozen=True, slots=True)
class SlackHITLConfig:
    channel_id: str
    approver_user_id: str
    approver_principal: str = MICHAEL_PRINCIPAL
    allowed_notice_author_ids: frozenset[str] = DEFAULT_ALLOWED_NOTICE_AUTHORS

    def __post_init__(self) -> None:
        if not self.channel_id.strip():
            raise RuntimeError("Slack HITL channel ID is required")
        if not self.approver_user_id.strip():
            raise RuntimeError("Slack HITL approver user ID is required")
        if self.approver_principal != MICHAEL_PRINCIPAL:
            raise RuntimeError("Production HITL requires canonical principal michael")
        if not self.allowed_notice_author_ids:
            raise RuntimeError("At least one OpenAI Slack notice author is required")
        if not self.allowed_notice_author_ids.issubset(DEFAULT_ALLOWED_NOTICE_AUTHORS):
            raise RuntimeError("HITL notice authors must be official OpenAI Slack bot identities")

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> SlackHITLConfig:
        values = env if env is not None else os.environ
        raw_authors = str(
            values.get(
                "MESH_COS_SLACK_ALLOWED_NOTICE_AUTHOR_IDS",
                ",".join(sorted(DEFAULT_ALLOWED_NOTICE_AUTHORS)),
            )
        )
        authors = frozenset(x.strip() for x in raw_authors.split(",") if x.strip())
        return cls(
            channel_id=str(values.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")).strip(),
            approver_user_id=_configured_approver_user_id(values),
            approver_principal=str(
                values.get("MESH_COS_SLACK_APPROVER_PRINCIPAL", MICHAEL_PRINCIPAL)
            ).strip(),
            allowed_notice_author_ids=authors,
        )


def _require_str(message: Mapping[str, Any], field: str) -> str:
    value = str(message.get(field) or "").strip()
    if not value:
        raise PermissionError(f"Slack provider message is missing {field}")
    return value


def _parse_decision(text: str, approval_id: str) -> tuple[str, str | None]:
    match = _DECISION_RE.fullmatch(text.strip())
    if match:
        if match.group("approval") != approval_id:
            raise PermissionError("Slack decision Approval ID mismatch")
        return match.group("verb"), None
    match = _CHANGES_RE.fullmatch(text.strip())
    if match:
        if match.group("approval") != approval_id:
            raise PermissionError("Slack decision Approval ID mismatch")
        return "CHANGES", match.group("change")
    raise PermissionError("Slack decision command is not exact or attributable")


class SlackApprovalHITLService:
    """Provider-verifies the bot-authored approval notice only.

    This service deliberately has no human-decision ingestion method. Ordinary Slack
    message authorship cannot prove human presence because Slack apps may post with user
    attribution. Canonical approval decisions enter through the separately authenticated
    Socket Mode slash-command boundary in ``SlackSocketApprovalService``.
    """

    def __init__(
        self,
        ledger: TaskLedger,
        client: SlackWebClient,
        config: SlackHITLConfig,
    ) -> None:
        self.ledger = ledger
        self.client = client
        self.config = config

    @classmethod
    def from_env(
        cls,
        ledger: TaskLedger,
        env: Mapping[str, str] | None = None,
    ) -> SlackApprovalHITLService:
        values = env if env is not None else os.environ
        token_file = str(values.get("MESH_COS_SLACK_VERIFIER_TOKEN_FILE", "")).strip()
        if not token_file:
            raise RuntimeError("MESH_COS_SLACK_VERIFIER_TOKEN_FILE is required")
        path = Path(token_file).expanduser()
        if not path.is_file():
            raise RuntimeError("Slack verifier token file is unavailable")
        token = path.read_text(encoding="utf-8").strip()
        if not token:
            raise RuntimeError("Slack verifier token file is empty")
        return cls(ledger, SlackWebClient(token), SlackHITLConfig.from_env(values))

    def _thread(self, thread_ts: str) -> list[dict[str, Any]]:
        response = self.client.transport(
            "conversations.replies",
            {"channel": self.config.channel_id, "ts": thread_ts},
            self.client.token,
        )
        if response.get("ok") is not True:
            raise RuntimeError("Slack provider thread read failed")
        messages = response.get("messages")
        if not isinstance(messages, list) or not messages:
            raise PermissionError("Slack provider did not return the approval thread")
        return [dict(message) for message in messages if isinstance(message, dict)]

    def _approval(self, approval_id: str) -> dict[str, Any]:
        approval = self.ledger.get_record("approval", approval_id)
        if approval is None:
            raise KeyError(approval_id)
        return dict(approval)

    def bind_notice(
        self,
        approval_id: str,
        *,
        channel_id: str,
        thread_ts: str,
        payload_fingerprint: str,
    ) -> dict[str, Any]:
        if channel_id != self.config.channel_id:
            raise PermissionError("Slack approval channel mismatch")
        if not payload_fingerprint.strip():
            raise PermissionError("Approval payload fingerprint is required")

        approval = self._approval(approval_id)
        if approval.get("approval_owner") != self.config.approver_principal:
            raise PermissionError("Canonical approval owner is not Michael")
        canonical_action = str(approval.get("action") or "")
        if payload_fingerprint not in canonical_action:
            raise PermissionError("Slack payload fingerprint does not match canonical approval")

        messages = self._thread(thread_ts)
        parent = messages[0]
        if _require_str(parent, "ts") != thread_ts:
            raise PermissionError("Slack provider parent timestamp mismatch")
        author = _require_str(parent, "user")
        if author not in self.config.allowed_notice_author_ids:
            raise PermissionError("HITL parent is not authored by an allowed OpenAI Slack bot")
        text = _require_str(parent, "text")
        required_fragments = (
            approval_id,
            payload_fingerprint,
            f"<@{self.config.approver_user_id}>",
        )
        if not all(fragment in text for fragment in required_fragments):
            raise PermissionError("HITL parent notice is missing canonical approval binding")
        lowered = text.lower()
        if "approval owner" not in lowered or not ("mk" in lowered or "michael" in lowered):
            raise PermissionError("HITL parent notice does not identify MK as approval owner")

        existing = self.ledger.get_record("approval_slack_binding", approval_id)
        if existing is not None:
            existing = dict(existing)
            if (
                existing.get("channel_id") != channel_id
                or existing.get("thread_ts") != thread_ts
                or existing.get("payload_fingerprint") != payload_fingerprint
            ):
                raise RuntimeError("Approval is already bound to different Slack evidence")
            return existing

        binding = {
            "version": "mesh.cos.approval-slack-binding.v1",
            "approval_id": approval_id,
            "task_id": approval["task_id"],
            "channel_id": channel_id,
            "thread_ts": thread_ts,
            "notice_author_user_id": author,
            "approver_identity_verified": True,
            "approver_principal": self.config.approver_principal,
            "payload_fingerprint": payload_fingerprint,
            "bound_at": utcnow(),
        }
        self.ledger.save_record("approval_slack_binding", approval_id, binding)
        return binding
