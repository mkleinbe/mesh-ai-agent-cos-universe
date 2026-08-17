from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field

from .ledger import TaskLedger

MESSAGE_TYPES = {"ASSIGN", "ACK", "UPDATE", "REQUEST", "EVIDENCE", "RISK", "BLOCKED", "CONFLICT", "RECOMMEND", "DECISION", "APPROVAL", "COMPLETE", "VERIFY"}

@dataclass(slots=True)
class SlackEventGuard:
    seen_event_ids: set[str] = field(default_factory=set)
    def accept(self, event_id: str) -> bool:
        if event_id in self.seen_event_ids:
            return False
        self.seen_event_ids.add(event_id)
        return True

def verify_slack_signature(signing_secret: str, timestamp: str, body: str, signature: str) -> bool:
    expected = "v0=" + hmac.new(signing_secret.encode(), f"v0:{timestamp}:{body}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

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

def render_message(kind: str, task_id: str, agent_id: str, action: str, evidence_reference: str | None = None, requested_next_action: str | None = None) -> str:
    if kind not in MESSAGE_TYPES:
        raise ValueError("Unknown structured Slack message type")
    lines = [f"[{kind}] {task_id}", f"Agent: {agent_id}", f"Action: {action}"]
    if evidence_reference:
        lines.append(f"Evidence: {evidence_reference}")
    if requested_next_action:
        lines.append(f"Next: {requested_next_action}")
    return "\n".join(lines)
