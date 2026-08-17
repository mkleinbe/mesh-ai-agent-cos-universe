from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any, Mapping, Protocol
from urllib.request import Request, urlopen

from .ledger import TaskLedger
from .slack import MESSAGE_TYPES, render_message


class SlackTransport(Protocol):
    def post_message(self, *, channel: str, text: str, thread_ts: str | None = None) -> dict[str, Any]: ...


class SlackWebApiTransport:
    """Minimal Slack Web API transport using only the standard library."""

    def __init__(self, bot_token: str, *, api_url: str = "https://slack.com/api/chat.postMessage") -> None:
        if not bot_token:
            raise ValueError("Slack bot token is required")
        self.bot_token = bot_token
        self.api_url = api_url

    def post_message(self, *, channel: str, text: str, thread_ts: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"channel": channel, "text": text}
        if thread_ts:
            payload["thread_ts"] = thread_ts
        request = Request(
            self.api_url,
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {self.bot_token}", "Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urlopen(request, timeout=15) as response:  # nosec B310 - fixed Slack API endpoint/configured test endpoint
            result = json.loads(response.read().decode())
        if not result.get("ok"):
            raise RuntimeError(f"Slack API error: {result.get('error', 'unknown')}")
        return result


def verify_request_signature(
    signing_secret: str,
    timestamp: str,
    body: str,
    signature: str,
    *,
    now: float | None = None,
    tolerance_seconds: int = 300,
) -> bool:
    if not signing_secret or not timestamp or not signature:
        return False
    try:
        ts = int(timestamp)
    except ValueError:
        return False
    current = int(now if now is not None else time.time())
    if abs(current - ts) > tolerance_seconds:
        return False
    base = f"v0:{timestamp}:{body}".encode()
    expected = "v0=" + hmac.new(signing_secret.encode(), base, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class SlackAdapter:
    def __init__(self, *, ledger: TaskLedger, transport: SlackTransport, agent_ops_channel_id: str, answer_desk_channel_id: str | None = None) -> None:
        if not agent_ops_channel_id:
            raise ValueError("Agent-operations Slack channel ID is required")
        self.ledger = ledger
        self.transport = transport
        self.agent_ops_channel_id = agent_ops_channel_id
        self.answer_desk_channel_id = answer_desk_channel_id

    @classmethod
    def from_env(cls, *, ledger: TaskLedger, transport: SlackTransport | None = None) -> "SlackAdapter":
        channel = os.getenv("MESH_COS_SLACK_AGENT_OPS_CHANNEL_ID", "")
        answer = os.getenv("MESH_COS_SLACK_ANSWER_DESK_CHANNEL_ID") or None
        if transport is None:
            transport = SlackWebApiTransport(os.getenv("MESH_COS_SLACK_BOT_TOKEN", ""))
        return cls(ledger=ledger, transport=transport, agent_ops_channel_id=channel, answer_desk_channel_id=answer)

    @staticmethod
    def signature_for_test(signing_secret: str, timestamp: str, body: str) -> str:
        base = f"v0:{timestamp}:{body}".encode()
        return "v0=" + hmac.new(signing_secret.encode(), base, hashlib.sha256).hexdigest()

    def accept_event(self, event_id: str) -> bool:
        return self.ledger.claim_idempotency(f"slack:event:{event_id}", event_id)

    def ensure_task_thread(self, task: dict[str, Any]) -> str:
        task_id = str(task["task_id"])
        mapping = self.ledger.get_thread_mapping(task_id)
        if mapping:
            return mapping["thread_ts"]
        text = "\n".join(
            [
                f"[TASK] {task_id}",
                f"Objective: {task.get('objective', '')}",
                f"Priority: {task.get('priority', 'P2')}",
                f"Accountable: {task.get('accountable_agent', '')}",
                f"Status: {task.get('status', 'INTAKE')}",
            ]
        )
        response = self.transport.post_message(channel=self.agent_ops_channel_id, text=text)
        if not response.get("ok", True) or not response.get("ts"):
            raise RuntimeError("Slack failed to create task thread")
        thread_ts = str(response["ts"])
        self.ledger.set_thread_mapping(task_id, self.agent_ops_channel_id, thread_ts)
        stored = self.ledger.get_task(task_id)
        if stored:
            stored.slack_channel_id = self.agent_ops_channel_id
            stored.slack_thread_ts = thread_ts
            self.ledger.save_task(stored)
        return thread_ts

    def post_structured(
        self,
        *,
        task_id: str,
        kind: str,
        agent_id: str,
        action: str,
        evidence_reference: str | None = None,
        requested_next_action: str | None = None,
    ) -> dict[str, Any]:
        if kind not in MESSAGE_TYPES:
            raise ValueError("Unknown structured Slack message type")
        task = self.ledger.get_task(task_id)
        task_payload = task.to_dict() if task else {"task_id": task_id, "objective": "", "accountable_agent": agent_id, "status": "IN_PROGRESS"}
        thread_ts = self.ensure_task_thread(task_payload)
        text = render_message(kind, task_id, agent_id, action, evidence_reference, requested_next_action)
        return self.transport.post_message(channel=self.agent_ops_channel_id, text=text, thread_ts=thread_ts)

    def notify_approval(self, *, task_id: str, agent_id: str, approval_id: str, action: str) -> dict[str, Any]:
        return self.post_structured(
            task_id=task_id,
            kind="APPROVAL",
            agent_id=agent_id,
            action=f"Approval required for {action}",
            evidence_reference=f"approval://{approval_id}",
            requested_next_action="Record decision in the control plane",
        )

    def post_answer_desk(self, *, text: str, thread_ts: str | None = None) -> dict[str, Any]:
        if not self.answer_desk_channel_id:
            raise RuntimeError("Answer Desk Slack channel is not configured")
        return self.transport.post_message(channel=self.answer_desk_channel_id, text=text, thread_ts=thread_ts)

    def handle_event(self, *, event_id: str, event: dict[str, Any]) -> dict[str, Any] | None:
        if not self.accept_event(event_id):
            return None
        return {"event_id": event_id, "accepted": True, "event": json.loads(json.dumps(event))}


class SlackEventReceiver:
    def __init__(self, *, signing_secret: str, adapter: SlackAdapter) -> None:
        if not signing_secret:
            raise ValueError("Slack signing secret is required")
        self.signing_secret = signing_secret
        self.adapter = adapter

    def process(self, headers: Mapping[str, str], body: str) -> dict[str, Any] | None:
        timestamp = headers.get("X-Slack-Request-Timestamp", "")
        signature = headers.get("X-Slack-Signature", "")
        if not verify_request_signature(self.signing_secret, timestamp, body, signature):
            raise PermissionError("Invalid Slack request signature")
        payload = json.loads(body)
        if payload.get("type") == "url_verification":
            return {"challenge": payload.get("challenge")}
        event_id = payload.get("event_id")
        if not event_id:
            raise ValueError("Slack event is missing event_id")
        return self.adapter.handle_event(event_id=str(event_id), event=dict(payload.get("event") or {}))
