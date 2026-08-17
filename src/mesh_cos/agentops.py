from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import TaskRecord, TaskStatus, new_id, utcnow
from .performance import PerformanceEvent, recommendation, score

SUPPORTED_RECOMMENDATIONS = {
    "CONTINUE",
    "INCREASE_ROUTING",
    "DECREASE_ROUTING",
    "WATCH",
    "RESTRICT",
    "RETRAIN_OR_REVISE",
    "QUARANTINE",
    "RETIRE",
    "BUILD_NEW_SPECIALIST",
}


def stalled(task: TaskRecord, now: datetime | None = None) -> bool:
    if not task.next_check_at or task.status in {TaskStatus.CLOSED, TaskStatus.CANCELLED, TaskStatus.VERIFIED}:
        return False
    now = now or datetime.now(timezone.utc)
    return datetime.fromisoformat(task.next_check_at) < now


def detect_coordination_loop(messages: list[dict], threshold: int = 4) -> bool:
    if len(messages) < threshold:
        return False
    recent = messages[-threshold:]
    return all(not message.get("state_change") and not message.get("evidence_reference") for message in recent) and len({message.get("agent_id") for message in recent}) > 1


def health_recommendation(events: list[PerformanceEvent]) -> str:
    return recommendation(events)


class AgentOpsEvaluator:
    def __init__(self, policy: dict, *, ledger: TaskLedger | None = None, window_size: int = 20) -> None:
        if window_size < 1:
            raise ValueError("window_size must be positive")
        self.policy = policy
        self.ledger = ledger
        self.window_size = window_size
        self.events: list[PerformanceEvent] = []

    @classmethod
    def from_file(cls, path: str | Path, *, ledger: TaskLedger | None = None, window_size: int = 20) -> "AgentOpsEvaluator":
        return cls(json.loads(Path(path).read_text()), ledger=ledger, window_size=window_size)

    def record(self, agent_id: str, task_id: str, category: str, value: float, severity: str = "LOW", reason: str = "") -> None:
        event = PerformanceEvent(agent_id, task_id, category, value, severity, reason)
        self.events.append(event)
        if self.ledger is not None:
            self.ledger.save_record("performance_event", new_id("perf"), event.to_dict())

    def _window(self, agent_id: str) -> list[PerformanceEvent]:
        local = [event for event in self.events if event.agent_id == agent_id]
        if self.ledger is not None:
            persisted = []
            for raw in self.ledger.list_records("performance_event"):
                if raw.get("agent_id") != agent_id:
                    continue
                persisted.append(
                    PerformanceEvent(
                        raw["agent_id"], raw["task_id"], raw["category"], float(raw["score"]),
                        raw.get("severity", "LOW"), raw.get("reason", ""), raw.get("timestamp", utcnow()),
                    )
                )
            if persisted:
                local = persisted
        return local[-self.window_size :]

    def scorecard(self, agent_id: str) -> dict:
        events = self._window(agent_id)
        weights = self.policy["weights"]
        thresholds = self.policy["thresholds"]
        weighted = score(events, weights)
        if any(event.severity == "CRITICAL" for event in events):
            rec = "QUARANTINE"
        elif weighted < thresholds["restrict_below"]:
            rec = "RESTRICT"
        elif weighted < thresholds["watch_below"]:
            rec = "WATCH"
        elif weighted > thresholds["increase_above"] and len(events) >= thresholds["minimum_events_for_increase"]:
            rec = "INCREASE_ROUTING"
        else:
            rec = "CONTINUE"
        now = utcnow()
        result = {
            "version": "mesh.cos.performance-scorecard.v1",
            "agent_id": agent_id,
            "window_start": events[0].timestamp if events else now,
            "window_end": events[-1].timestamp if events else now,
            "weighted_score": weighted,
            "weights_version": self.policy["version"],
            "recommendation": rec,
            "event_count": len(events),
            "window_size": self.window_size,
            "generated_at": now,
        }
        if self.ledger is not None:
            self.ledger.save_record("scorecard", agent_id, result)
        return result

    def supported_recommendations(self) -> set[str]:
        return set(SUPPORTED_RECOMMENDATIONS)

    def observe_tasks(self, tasks: list[TaskRecord], *, max_concurrency: dict[str, int] | None = None) -> dict:
        active_states = {TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.AWAITING_INPUT, TaskStatus.AWAITING_APPROVAL, TaskStatus.QA, TaskStatus.REWORK}
        stalled_ids = [task.task_id for task in tasks if stalled(task)]
        counts = Counter(task.accountable_agent for task in tasks if task.status in active_states)
        limits = max_concurrency or {}
        overloaded = sorted(agent_id for agent_id, count in counts.items() if count > limits.get(agent_id, 10**9))
        return {"stalled_task_ids": stalled_ids, "active_by_agent": dict(counts), "overloaded_agents": overloaded}

    def record_health_change(self, agent_id: str, from_state: str, to_state: str, reason: str, *, approved_by: str) -> dict:
        if self.ledger is None:
            raise RuntimeError("A ledger is required for durable health changes")
        record = {
            "agent_id": agent_id,
            "from_state": from_state,
            "to_state": to_state,
            "reason": reason,
            "approved_by": approved_by,
            "timestamp": utcnow(),
        }
        self.ledger.save_record("registry_change", agent_id, record)
        event = AuditEvent("agent_health_change", "agentops", agent_id, new_id("corr"), 2, f"{from_state}->{to_state}: {reason}")
        self.ledger.record_event(event.to_dict())
        return record
