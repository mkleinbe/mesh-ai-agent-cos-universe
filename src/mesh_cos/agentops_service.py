from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

from .agentops import stalled
from .ledger import TaskLedger
from .models import new_id, utcnow


@dataclass(frozen=True, slots=True)
class PerformancePolicy:
    version: str
    weights: dict[str, float]
    thresholds: dict[str, float]
    critical_defect_recommendation: str = "QUARANTINE"

    @classmethod
    def from_file(cls, path: str | Path) -> "PerformancePolicy":
        data = json.loads(Path(path).read_text())
        weights = {str(k): float(v) for k, v in data["weights"].items()}
        if abs(sum(weights.values()) - 1.0) > 1e-9:
            raise ValueError("Performance policy weights must sum to 1.0")
        return cls(
            version=str(data["version"]),
            weights=weights,
            thresholds={str(k): float(v) for k, v in data["thresholds"].items()},
            critical_defect_recommendation=str(data.get("critical_defect_recommendation", "QUARANTINE")),
        )


class AgentOpsService:
    def __init__(self, *, ledger: TaskLedger, policy: PerformancePolicy) -> None:
        self.ledger = ledger
        self.policy = policy

    def record(self, *, agent_id: str, task_id: str, category: str, score: float, severity: str = "LOW", reason: str = "", cost: float | None = None) -> dict:
        if category not in self.policy.weights:
            raise ValueError(f"Unknown performance category: {category}")
        if not 0 <= score <= 1:
            raise ValueError("Performance score must be between 0 and 1")
        payload = {
            "version": "mesh.cos.performance-event.v1",
            "performance_event_id": new_id("perf"),
            "agent_id": agent_id,
            "task_id": task_id,
            "category": category,
            "score": score,
            "severity": severity,
            "reason": reason,
            "timestamp": utcnow(),
            "cost": cost,
        }
        self.ledger.save_performance_event(payload)
        return payload

    def _window_events(self, agent_id: str, window_start: str, window_end: str) -> list[dict]:
        start = datetime.fromisoformat(window_start)
        end = datetime.fromisoformat(window_end)
        return [
            e for e in self.ledger.list_performance_events(agent_id)
            if start <= datetime.fromisoformat(e["timestamp"]) <= end
        ]

    def scorecard(self, agent_id: str, *, window_start: str, window_end: str) -> dict:
        events = self._window_events(agent_id, window_start, window_end)
        grouped: dict[str, list[float]] = {}
        for event in events:
            grouped.setdefault(event["category"], []).append(float(event["score"]))
        weighted = 0.0
        used_weight = 0.0
        for category, weight in self.policy.weights.items():
            values = grouped.get(category, [])
            if values:
                weighted += (sum(values) / len(values)) * weight
                used_weight += weight
        score = round(weighted / used_weight, 4) if used_weight else 0.0
        recommendation = self.recommend(events, score)
        payload = {
            "version": "mesh.cos.performance-scorecard.v1",
            "scorecard_id": new_id("scorecard"),
            "agent_id": agent_id,
            "window_start": window_start,
            "window_end": window_end,
            "weighted_score": score,
            "weights_version": self.policy.version,
            "recommendation": recommendation,
            "event_count": len(events),
            "category_scores": {k: round(sum(v) / len(v), 4) for k, v in grouped.items()},
        }
        self.ledger.save_scorecard(payload)
        return payload

    def recommend(self, events: list[dict], score: float) -> str:
        if any(e.get("severity") == "CRITICAL" for e in events):
            return self.policy.critical_defect_recommendation
        thresholds = self.policy.thresholds
        if score < thresholds["restrict_below"]:
            return "RESTRICT"
        if score < thresholds["watch_below"]:
            return "WATCH"
        if score > thresholds["increase_routing_above"] and len(events) >= int(thresholds["min_events_for_increase"]):
            return "INCREASE_ROUTING"
        return "CONTINUE"

    def stalled_tasks(self) -> list[str]:
        return [task.task_id for task in self.ledger.list_tasks() if stalled(task)]

    def workload(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for task in self.ledger.list_tasks():
            if task.status.value not in {"CLOSED", "CANCELLED", "VERIFIED"}:
                counts[task.accountable_agent] = counts.get(task.accountable_agent, 0) + 1
        return counts

    def defect_taxonomy(self, agent_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for event in self.ledger.list_performance_events(agent_id):
            if event.get("severity") in {"CRITICAL", "HIGH", "MEDIUM"}:
                key = str(event.get("reason") or "unspecified")
                counts[key] = counts.get(key, 0) + 1
        return counts
