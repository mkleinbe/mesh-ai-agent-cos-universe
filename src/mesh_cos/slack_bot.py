from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ledger import TaskLedger
from .models import utcnow

SLACK_API_BASE = "https://slack.com/api"
SLACK_BOT_API = "SLACK_BOT_API"
THREAD_BINDING_KIND = "approval_slack_thread_binding"
CHANGE_REQUEST_KIND = "approval_change_request"
_PAYLOAD_FINGERPRINT_RE = re.compile(
    r"\bpayload_fingerprint=(?P<fingerprint>[A-Fa-f0-9]{64})\b"
)

SlackTransport = Callable[[str, dict[str, Any], str], dict[str, Any]]


def read_slack_bot_token(env: Mapping[str, str] | None = None) -> str:
    values = env if env is not None else os.environ
    path_value = str(values.get("MESH_COS_SLACK_BOT_TOKEN_FILE", "")).strip()
    if not path_value:
        raise RuntimeError("MESH_COS_SLACK_BOT_TOKEN_FILE is required")
    path = Path(path_value).expanduser()
    try:
        token = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise RuntimeError("Slack bot OAuth token file is unavailable") from exc
    if not token.startswith("xoxb-"):
        raise RuntimeError("Slack bot OAuth token must begin with xoxb-")
    return token


def _default_transport(method: str, payload: dict[str, Any], token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{SLACK_API_BASE}/{method}",
        data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - fixed Slack API host
            body = response.read(1_000_001)
    except (OSError, urllib.error.URLError) as exc:
        raise RuntimeError("Slack Web API request failed") from exc
    if len(body) > 1_000_000:
        raise RuntimeError("Slack Web API response exceeded maximum size")
    try:
        decoded = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Slack Web API returned invalid JSON") from exc
    if not isinstance(decoded, dict) or decoded.get("ok") is not True:
        raise RuntimeError("Slack Web API rejected the request")
    return decoded


@dataclass(slots=True)
class SlackBotAPI:
    token: str
    transport: SlackTransport = _default_transport

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
        *,
        transport: SlackTransport = _default_transport,
    ) -> SlackBotAPI:
        return cls(read_slack_bot_token(env), transport)

    def post_message(
        self,
        *,
        channel_id: str,
        text: str,
        blocks: list[dict[str, Any]] | None = None,
        thread_ts: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "channel": channel_id,
            "text": text,
            "unfurl_links": False,
            "unfurl_media": False,
        }
        if blocks is not None:
            payload["blocks"] = blocks
        if thread_ts:
            payload["thread_ts"] = thread_ts
        # Intentionally do not pass username, icon_emoji, or icon_url. Slack must render
        # the installed app's configured bot identity rather than impersonating a human.
        return self.transport("chat.postMessage", payload, self.token)

    def update_message(
        self,
        *,
        channel_id: str,
        message_ts: str,
        text: str,
        blocks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self.transport(
            "chat.update",
            {
                "channel": channel_id,
                "ts": message_ts,
                "text": text,
                "blocks": blocks,
            },
            self.token,
        )


def _fingerprint(approval: Mapping[str, Any]) -> str:
    match = _PAYLOAD_FINGERPRINT_RE.search(str(approval.get("action") or ""))
    if match is None:
        raise PermissionError("Canonical approval is missing payload_fingerprint")
    return match.group("fingerprint").lower()


def _rich_text_line(text: str, *, bold: bool = False) -> dict[str, Any]:
    element: dict[str, Any] = {"type": "text", "text": text}
    if bold:
        element["style"] = {"bold": True}
    return element


def approval_blocks(approval_id: str, action: str) -> list[dict[str, Any]]:
    summary = " ".join(action.split())
    if len(summary) > 2800:
        summary = summary[:2797] + "..."
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "Approval required", "emoji": True},
        },
        {
            "type": "rich_text",
            "block_id": f"approval_summary_{approval_id}",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        _rich_text_line("Request\n", bold=True),
                        _rich_text_line(summary),
                        _rich_text_line("\n\nApproval ID\n", bold=True),
                        _rich_text_line(approval_id),
                    ],
                }
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "Human decision required. No consequential action occurs until this approval is authorized.",
                }
            ],
        },
        {
            "type": "actions",
            "block_id": f"approval_actions_{approval_id}",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Approve", "emoji": True},
                    "style": "primary",
                    "action_id": "mesh_approval_approve",
                    "value": approval_id,
                    "accessibility_label": "Approve this request",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Deny", "emoji": True},
                    "style": "danger",
                    "action_id": "mesh_approval_deny",
                    "value": approval_id,
                    "accessibility_label": "Deny this request",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Change", "emoji": True},
                    "action_id": "mesh_approval_change",
                    "value": approval_id,
                    "accessibility_label": "Request changes before approval",
                },
            ],
        },
    ]


def resolved_blocks(approval_id: str, disposition: str) -> list[dict[str, Any]]:
    return [
        {
            "type": "rich_text",
            "block_id": f"approval_resolved_{approval_id}",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        _rich_text_line("Approval decision\n", bold=True),
                        _rich_text_line(disposition),
                        _rich_text_line("\n\nApproval ID\n", bold=True),
                        _rich_text_line(approval_id),
                    ],
                }
            ],
        }
    ]


class SlackApprovalNotifier:
    def __init__(self, ledger: TaskLedger, api: SlackBotAPI, channel_id: str) -> None:
        self.ledger = ledger
        self.api = api
        self.channel_id = channel_id.strip()
        if not self.channel_id:
            raise RuntimeError("Slack approval channel ID is required")

    @classmethod
    def from_env(
        cls,
        ledger: TaskLedger,
        env: Mapping[str, str] | None = None,
        *,
        transport: SlackTransport = _default_transport,
    ) -> SlackApprovalNotifier:
        values = env if env is not None else os.environ
        return cls(
            ledger,
            SlackBotAPI.from_env(values, transport=transport),
            str(values.get("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")),
        )

    def _existing_binding_for_approval(self, approval_id: str) -> dict[str, Any] | None:
        for record in self.ledger.list_records(THREAD_BINDING_KIND):
            if record.get("approval_id") == approval_id:
                return dict(record)
        return None

    def post_approval(self, approval_id: str) -> dict[str, Any]:
        existing = self._existing_binding_for_approval(approval_id)
        if existing is not None:
            return {
                "status": "ALREADY_POSTED",
                "execution_mode": SLACK_BOT_API,
                "authority": "COLLABORATION_ONLY",
                "approval_id": approval_id,
                "channel_id": existing["channel_id"],
                "thread_ts": existing["thread_ts"],
            }
        approval = self.ledger.get_record("approval", approval_id)
        if approval is None:
            raise KeyError(approval_id)
        approval = dict(approval)
        if approval.get("status") != "PENDING":
            raise ValueError("Only PENDING approvals can be posted to Slack")
        fingerprint = _fingerprint(approval)
        action = str(approval.get("action") or "").strip()
        response = self.api.post_message(
            channel_id=self.channel_id,
            text=f"Approval required: {approval_id}",
            blocks=approval_blocks(approval_id, action),
        )
        channel = str(response.get("channel") or "").strip()
        thread_ts = str(response.get("ts") or "").strip()
        if channel != self.channel_id or not thread_ts:
            raise RuntimeError("Slack did not return the expected approval message identity")
        binding = {
            "version": "mesh.cos.slack-thread-binding.v2",
            "source": "SLACK_BOT_API_CHAT_POSTMESSAGE",
            "approval_id": approval_id,
            "task_id": approval.get("task_id"),
            "channel_id": channel,
            "thread_ts": thread_ts,
            "payload_fingerprint": fingerprint,
            "recorded_at": utcnow(),
        }
        self.ledger.save_record(THREAD_BINDING_KIND, thread_ts, binding)
        return {
            "status": "POSTED",
            "execution_mode": SLACK_BOT_API,
            "authority": "COLLABORATION_ONLY",
            "approval_id": approval_id,
            "channel_id": channel,
            "thread_ts": thread_ts,
            "format": "BLOCK_KIT_RICH_TEXT_V1",
        }

    def post_thread_reply(self, thread_ts: str, text: str) -> dict[str, Any]:
        response = self.api.post_message(
            channel_id=self.channel_id,
            text=text,
            thread_ts=thread_ts,
        )
        message_ts = str(response.get("ts") or "").strip()
        if not message_ts:
            raise RuntimeError("Slack did not return a thread reply timestamp")
        return {"channel_id": self.channel_id, "thread_ts": thread_ts, "message_ts": message_ts}

    def mark_resolved(self, approval_id: str, disposition: str) -> None:
        binding = self._existing_binding_for_approval(approval_id)
        if binding is None:
            return
        try:
            self.api.update_message(
                channel_id=str(binding["channel_id"]),
                message_ts=str(binding["thread_ts"]),
                text=f"Approval {disposition.lower()}: {approval_id}",
                blocks=resolved_blocks(approval_id, disposition),
            )
        except RuntimeError:
            # Canonical approval state must not be rolled back because a presentation-only
            # Slack update failed. A stale button will fail closed against decided state.
            return

    def list_pending_change_requests(self) -> list[dict[str, Any]]:
        return [
            dict(record)
            for record in self.ledger.list_records(CHANGE_REQUEST_KIND)
            if record.get("status") == "PENDING_AGENT_REVISION"
            and record.get("channel_id") == self.channel_id
        ]

    def mark_change_request_revised(self, change_request_id: str, new_approval_id: str) -> dict[str, Any]:
        record = self.ledger.get_record(CHANGE_REQUEST_KIND, change_request_id)
        if record is None:
            raise KeyError(change_request_id)
        record = dict(record)
        if record.get("status") != "PENDING_AGENT_REVISION":
            raise ValueError("Change request is not pending agent revision")
        new_approval = self.ledger.get_record("approval", new_approval_id)
        if new_approval is None:
            raise KeyError(new_approval_id)
        new_approval = dict(new_approval)
        if new_approval.get("task_id") != record.get("task_id"):
            raise PermissionError("Revised approval must belong to the same task")
        if new_approval.get("status") != "PENDING":
            raise ValueError("Revised approval must be PENDING")
        new_fingerprint = _fingerprint(new_approval)
        if new_fingerprint == str(record.get("payload_fingerprint") or "").lower():
            raise ValueError("Revised approval must bind a new payload_fingerprint")
        record["status"] = "REVISED"
        record["new_approval_id"] = new_approval_id
        record["new_payload_fingerprint"] = new_fingerprint
        record["revised_at"] = utcnow()
        self.ledger.save_record(CHANGE_REQUEST_KIND, change_request_id, record)
        return record
