from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any

from .ledger import TaskLedger


class MetricsService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def snapshot(self) -> dict[str, Any]:
        tasks = self.ledger.list_tasks()
        verified = [t for t in tasks if t.status.value in {"VERIFIED", "CLOSED"} and t.outcome_evidence]
        completed = [t for t in tasks if t.status.value in {"COMPLETED", "VERIFIED", "CLOSED"}]
        active = [t for t in tasks if t.status.value not in {"CLOSED", "CANCELLED", "VERIFIED"}]
        now = datetime.now(timezone.utc)
        stalled = [t for t in active if t.next_check_at and datetime.fromisoformat(t.next_check_at) < now]

        desk = self.ledger.list_metrics("answer_desk_disposition")
        deflected = sum(1 for m in desk if m.get("disposition") in {"ANSWERED", "ROUTED", "RECOMMENDATION_PROVIDED"})
        desk_escalations = sum(1 for m in desk if m.get("disposition") == "ESCALATED")

        cycle_times: list[float] = []
        for task in verified:
            end = task.verified_at or task.closed_at
            if end:
                cycle_times.append((datetime.fromisoformat(end) - datetime.fromisoformat(task.created_at)).total_seconds())

        approvals = self.ledger.list_approvals()
        approval_times: list[float] = []
        for approval in approvals:
            if approval.get("requested_at") and approval.get("decided_at"):
                approval_times.append((datetime.fromisoformat(approval["decided_at"]) - datetime.fromisoformat(approval["requested_at"])).total_seconds())

        perf_events = self.ledger.list_performance_events()
        escalation_scores = [float(e["score"]) for e in perf_events if e.get("category") == "escalation_judgment"]
        total_cost = sum(float(e["cost"]) for e in perf_events if e.get("cost") is not None)
        has_cost = any(e.get("cost") is not None for e in perf_events)

        return {
            "work_resolved_without_michael": self._ratio([t for t in verified if t.CEO_touches == 0], verified),
            "questions_deflected_from_michael": deflected,
            "answer_desk_ceo_escalations": desk_escalations,
            "ceo_touches_per_completed_task": (sum(t.CEO_touches for t in completed) / len(completed)) if completed else None,
            "first_pass_acceptance_rate": self._ratio([t for t in verified if t.rework_count == 0], verified),
            "rework_rate": self._ratio([t for t in completed if t.rework_count > 0], completed),
            "escalation_quality": mean(escalation_scores) if escalation_scores else None,
            "average_task_cycle_seconds": mean(cycle_times) if cycle_times else None,
            "stalled_task_rate": self._ratio(stalled, active),
            "verified_outcome_rate": self._ratio(verified, completed or tasks),
            "agent_failure_rate": self._ratio([e for e in perf_events if e.get("severity") in {"CRITICAL", "HIGH"}], perf_events),
            "average_approval_cycle_seconds": mean(approval_times) if approval_times else None,
            "cross_agent_conflict_rate": (len(self.ledger.list_conflicts()) / len(tasks)) if tasks else None,
            "agent_conversation_loop_rate": self._metric_rate("coordination_loop"),
            "average_contributors_per_task": (sum(len(t.contributors) for t in tasks) / len(tasks)) if tasks else None,
            "cost_per_verified_outcome": (total_cost / len(verified)) if has_cost and verified else None,
        }

    @staticmethod
    def _ratio(numerator: list[Any], denominator: list[Any]) -> float | None:
        return (len(numerator) / len(denominator)) if denominator else None

    def _metric_rate(self, metric_name: str) -> float | None:
        values = self.ledger.list_metrics(metric_name)
        if not values:
            return None
        return sum(float(v.get("value") or 0) for v in values) / len(values)
