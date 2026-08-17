from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from urllib.request import Request, urlopen

from .answer_desk import AnswerDeskService
from .ledger import TaskLedger
from .models import utcnow

MESSAGE_TYPES = {
    "ASSIGN",
    "ACK",
    "UPDATE",
    "REQUEST",
    "EVIDENCE",
    "RISK",
    "BLOCKED",
    "CONFLICT",
    "RECOMMEND",
    "DECISION",
    "APPROVAL",
    "COMPLETE",
    "VERIFY",
}


@dataclass(slots=True)
class SlackEventGuard:
    seen_event_ids: set[str] = field(default_factory=set)

    def accept(self, event_id: str) -> bool:
        if event_id in self.seen_event_ids:
            return False
        self.seen_event_ids.add(event_id)
        return True


def verify_slack_signature(signing_secret: str, timestamp: str, body: str, signature: str) -> bool:
    expected = "v0=" + hmac.new(
        signing_secret.encode(),
        f"v0:{timestamp}:{body}".encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_slack_request(
    signing_secret: str,
    timestamp: str,
    body: str,
    signature: str,
    *,
    now: datetime | None = None,
    max_age_seconds: int = 300,
) -> bool:
    try:
        request_time = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return False
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    if abs((current.astimezone(timezone.utc) - request_time).total_seconds()) > max_age_seconds:
        return False
    return verify_slack_signature(signing_secret, timestamp, body, signature)


def _default_transport(method: str, payload: dict, token: str) -> dict:
    request = Request(
        f"https://slack.com/api/{method}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError(f"Slack API error: {result.get('error', 'unknown_error')}")
    return result


class SlackWebClient:
    def __init__(
        self,
        token: str,
        *,
        transport: Callable[[str, dict, str], dict] | None = None,
    ) -> None:
        if not token:
            raise ValueError("Slack bot token is required")
        self.token = token
        self.transport = transport or _default_transport

    def post_message(
        self,
        channel_id: str,
        text: str,
        *,
        thread_ts: str | None = None,
    ) -> dict:
        payload = {"channel": channel_id, "text": text}
        if thread_ts:
            payload["thread_ts"] = thread_ts
        return self.transport("chat.postMessage", payload, self.token)


class SlackCoordinator:
    def __init__(self, ledger: TaskLedger, channel_id: str) -> None:
        self.ledger = ledger
        self.channel_id = channel_id

    def bind_thread(self, task_id: str, thread_ts: str) -> dict:
        return self.ledger.bind_thread(task_id, self.channel_id, thread_ts)

    def thread_for(self, task_id: str) -> dict | None:
        return self.ledger.get_thread(task_id)

    def accept_event(self, event_id: str) -> bool:
        return self.ledger.claim_idempotency_key(f"slack:{event_id}")

    def ensure_thread(self, task_id: str, client: SlackWebClient, text: str) -> dict:
        existing = self.thread_for(task_id)
        if existing:
            return existing
        result = client.post_message(self.channel_id, text)
        thread_ts = result.get("ts")
        if not thread_ts:
            raise RuntimeError("Slack response did not include a thread timestamp")
        return self.bind_thread(task_id, thread_ts)

    def notify_approval(
        self,
        task_id: str,
        client: SlackWebClient,
        approval_owner: str,
        action: str,
    ) -> dict:
        mapping = self.thread_for(task_id)
        if mapping is None:
            mapping = self.ensure_thread(
                task_id,
                client,
                render_message("APPROVAL", task_id, "cos", f"Approval required: {action}"),
            )
        text = render_message(
            "APPROVAL",
            task_id,
            "cos",
            f"{approval_owner} approval required for {action}",
            requested_next_action="approve or reject",
        )
        return client.post_message(self.channel_id, text, thread_ts=mapping["thread_ts"])


def render_message(
    kind: str,
    task_id: str,
    agent_id: str,
    action: str,
    evidence_reference: str | None = None,
    requested_next_action: str | None = None,
) -> str:
    if kind not in MESSAGE_TYPES:
        raise ValueError("Unknown structured Slack message type")
    lines = [f"[{kind}] {task_id}", f"Agent: {agent_id}", f"Action: {action}"]
    if evidence_reference:
        lines.append(f"Evidence: {evidence_reference}")
    if requested_next_action:
        lines.append(f"Next: {requested_next_action}")
    return "\n".join(lines)


def parse_message(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines or not lines[0].startswith("[") or "] " not in lines[0]:
        raise ValueError("Message does not use the Mesh structured Slack protocol")
    kind, task_id = lines[0][1:].split("] ", 1)
    if kind not in MESSAGE_TYPES:
        raise ValueError("Unknown structured Slack message type")
    fields = {"kind": kind, "task_id": task_id}
    aliases = {
        "Agent": "agent_id",
        "Action": "action",
        "Evidence": "evidence_reference",
        "Next": "requested_next_action",
    }
    for line in lines[1:]:
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        fields[aliases.get(key, key.lower())] = value
    if "agent_id" not in fields or "action" not in fields:
        raise ValueError("Structured Slack message requires Agent and Action")
    return fields


class SlackInboundService:
    def __init__(self, coordinator: SlackCoordinator, *, signing_secret: str | None = None) -> None:
        self.coordinator = coordinator
        self.signing_secret = signing_secret

    def handle(self, event_id: str, text: str) -> dict | None:
        # Parse first so malformed input cannot poison the durable dedupe key and
        # prevent a corrected Slack retry from being processed.
        parsed = parse_message(text)
        if not self.coordinator.accept_event(event_id):
            return None
        self.coordinator.ledger.save_record(
            "slack_event",
            event_id,
            {
                "event_id": event_id,
                "channel_id": self.coordinator.channel_id,
                "received_at": utcnow(),
                **parsed,
            },
        )
        return parsed

    def handle_request(
        self,
        event_id: str,
        text: str,
        *,
        timestamp: str,
        body: str,
        signature: str,
        now: datetime | None = None,
    ) -> dict | None:
        if not self.signing_secret:
            raise RuntimeError("Slack signing secret is required for inbound request handling")
        if not verify_slack_request(
            self.signing_secret,
            timestamp,
            body,
            signature,
            now=now,
        ):
            raise PermissionError("Invalid or stale Slack request")
        return self.handle(event_id, text)


class AnswerDeskSlackService:
    """Separate configurable team-facing Slack boundary for Answer Desk."""

    def __init__(
        self,
        channel_id: str,
        answer_desk: AnswerDeskService,
        client: SlackWebClient,
    ) -> None:
        if not channel_id:
            raise ValueError("Answer Desk Slack channel ID is required")
        self.channel_id = channel_id
        self.answer_desk = answer_desk
        self.client = client

    def handle_question(self, request_id: str, question: str, **decision_context) -> dict:
        disposition = self.answer_desk.handle(request_id=request_id, **decision_context)
        text = (
            f"[{disposition.disposition}] {request_id}\n"
            f"Question: {question}\n"
            f"Reason: {disposition.reason}"
        )
        if disposition.routed_to:
            text += f"\nRouted to: {disposition.routed_to}"
        result = self.client.post_message(self.channel_id, text)
        return {
            "disposition": disposition.disposition,
            "routed_to": disposition.routed_to,
            "slack": result,
        }
