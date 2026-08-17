from __future__ import annotations

from datetime import datetime, timezone
from statistics import median

from .ledger import TaskLedger
from .models import TaskStatus


class MetricsService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    @staticmethod
    def _duration_minutes(start: str | None, end: str | None) -> float | None:
        if not start or not end:
            return None
        return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() / 60.0

    def summary(self) -> dict:
        tasks = self.ledger.list_tasks()
        verified = [task for task in tasks if task.status in {TaskStatus.VERIFIED, TaskStatus.CLOSED}]
        resolved_without_ceo = [task for task in verified if task.CEO_touches == 0]
        time_avoided = sum(
            int(task.ceo_time_avoided_estimate_minutes or 0)
            for task in verified
            if task.ceo_time_avoided_methodology
        )

        verifications = self.ledger.list_records("verification")
        passed = [record for record in verifications if record.get("passed")]
        first_pass = [record for record in passed if int(record.get("attempt", 1)) == 1]
        first_pass_rate = len(first_pass) / len(passed) if passed else 0.0
        rework_rate = len([task for task in tasks if task.rework_count > 0]) / len(tasks) if tasks else 0.0

        escalations = self.ledger.list_records("escalation")
        correct_escalations = sum(1 for record in escalations if record.get("classification") == "correct")
        false_escalations = sum(1 for record in escalations if record.get("classification") == "false")
        missed_escalations = sum(1 for record in escalations if record.get("classification") == "missed")

        cycle_times = [
            duration
            for task in verified
            if (duration := self._duration_minutes(task.started_at or task.created_at, task.verified_at or task.closed_at)) is not None
        ]
        median_cycle = round(median(cycle_times), 3) if cycle_times else 0.0

        now = datetime.now(timezone.utc)
        active = [task for task in tasks if task.status not in {TaskStatus.CLOSED, TaskStatus.CANCELLED, TaskStatus.VERIFIED}]
        stalled = [task for task in active if task.next_check_at and datetime.fromisoformat(task.next_check_at) < now]
        stalled_rate = len(stalled) / len(active) if active else 0.0

        approvals = self.ledger.list_records("approval")
        approval_times = [
            duration
            for record in approvals
            if (duration := self._duration_minutes(record.get("requested_at"), record.get("decided_at"))) is not None
        ]
        approval_median = round(median(approval_times), 3) if approval_times else 0.0

        costs = sum(float(record.get("amount", 0.0)) for record in self.ledger.list_records("cost"))
        cost_per_verified = round(costs / len(verified), 4) if verified else 0.0

        answer_records = self.ledger.list_records("answer_desk")
        deflected = [record for record in answer_records if record.get("disposition") in {"ANSWERED", "RECOMMENDATION_PROVIDED"}]
        answer_deflection = len(deflected) / len(answer_records) if answer_records else 0.0

        contributor_counts = [len(task.contributors) for task in tasks]
        avg_contributors = sum(contributor_counts) / len(contributor_counts) if contributor_counts else 0.0

        return {
            "verified_outcomes": len(verified),
            "tasks_resolved_without_ceo": len(resolved_without_ceo),
            "ceo_time_avoided_minutes": time_avoided,
            "first_pass_acceptance_rate": round(first_pass_rate, 4),
            "rework_rate": round(rework_rate, 4),
            "correct_escalations": correct_escalations,
            "false_escalations": false_escalations,
            "missed_escalations": missed_escalations,
            "median_cycle_time_minutes": median_cycle,
            "stalled_task_rate": round(stalled_rate, 4),
            "execution_failures": len(self.ledger.list_records("execution_failure")),
            "approval_median_time_minutes": approval_median,
            "conflicts": len(self.ledger.list_records("conflict")),
            "coordination_loops": len(self.ledger.list_records("coordination_loop")),
            "avg_contributors_per_task": round(avg_contributors, 4),
            "cost_per_verified_outcome": cost_per_verified,
            "answer_desk_deflection_rate": round(answer_deflection, 4),
        }
