from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import TaskRecord
from .performance import PerformanceEvent, recommendation, score


def stalled(task: TaskRecord, now: datetime | None = None) -> bool:
    if not task.next_check_at or task.status.value in {"CLOSED", "CANCELLED", "VERIFIED"}:
        return False
    now = now or datetime.now(timezone.utc)
    return datetime.fromisoformat(task.next_check_at) < now


def detect_coordination_loop(messages: list[dict], threshold: int = 4) -> bool:
    if len(messages) < threshold:
        return False
    recent = messages[-threshold:]
    return all(not m.get("state_change") and not m.get("evidence_reference") for m in recent) and len({m.get("agent_id") for m in recent}) > 1


def health_recommendation(events: list[PerformanceEvent]) -> str:
    return recommendation(events)


class AgentOpsEvaluator:
    def __init__(self, policy: dict) -> None:
        self.policy = policy
        self.events: list[PerformanceEvent] = []

    @classmethod
    def from_file(cls, path: str | Path) -> "AgentOpsEvaluator":
        return cls(json.loads(Path(path).read_text()))

    def record(self, agent_id: str, task_id: str, category: str, value: float, severity: str = "LOW", reason: str = "") -> None:
        self.events.append(PerformanceEvent(agent_id, task_id, category, value, severity, reason))

    def scorecard(self, agent_id: str) -> dict:
        events = [e for e in self.events if e.agent_id == agent_id]
        weights = self.policy["weights"]
        thresholds = self.policy["thresholds"]
        weighted = score(events, weights)
        if any(e.severity == "CRITICAL" for e in events):
            rec = "QUARANTINE"
        elif weighted < thresholds["restrict_below"]:
            rec = "RESTRICT"
        elif weighted < thresholds["watch_below"]:
            rec = "WATCH"
        elif weighted > thresholds["increase_above"] and len(events) >= thresholds["minimum_events_for_increase"]:
            rec = "INCREASE_ROUTING"
        else:
            rec = "CONTINUE"
        return {
            "version": "mesh.cos.performance-scorecard.v1",
            "agent_id": agent_id,
            "weighted_score": weighted,
            "weights_version": self.policy["version"],
            "recommendation": rec,
        }
