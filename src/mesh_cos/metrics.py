from __future__ import annotations

from datetime import UTC, datetime
from statistics import median

from .ledger import TaskLedger
from .models import TaskStatus


def _as_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


class MetricsService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    @staticmethod
    def _duration_minutes(start: str | None, end: str | None) -> float | None:
        if not start or not end:
            return None
        return (_as_utc(end) - _as_utc(start)).total_seconds() / 60.0

    def summary(self) -> dict:
        tasks = self.ledger.list_tasks()
        completed = [
            task
            for task in tasks
            if task.status in {TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.CLOSED}
        ]
        verified = [task for task in tasks if task.status in {TaskStatus.VERIFIED, TaskStatus.CLOSED}]
        resolved_without_ceo = [task for task in verified if task.CEO_touches == 0]
        work_without_michael_rate = len(resolved_without_ceo) / len(verified) if verified else 0.0
        time_avoided = sum(
            int(task.ceo_time_avoided_estimate_minutes or 0)
            for task in verified
            if task.ceo_time_avoided_methodology
        )
        ceo_touches_per_completed = (
            sum(task.CEO_touches for task in completed) / len(completed) if completed else 0.0
        )

        verifications = self.ledger.list_records("verification")
        passed = [record for record in verifications if record.get("passed")]
        first_pass = [record for record in passed if int(record.get("attempt", 1)) == 1]
        first_pass_rate = len(first_pass) / len(passed) if passed else 0.0
        rework_rate = len([task for task in tasks if task.rework_count > 0]) / len(tasks) if tasks else 0.0
        verified_outcome_rate = len(verified) / len(tasks) if tasks else 0.0

        escalations = self.ledger.list_records("escalation")
        correct_escalations = sum(
            1 for record in escalations if record.get("classification") == "correct"
        )
        false_escalations = sum(
            1 for record in escalations if record.get("classification") == "false"
        )
        missed_escalations = sum(
            1 for record in escalations if record.get("classification") == "missed"
        )
        escalation_total = correct_escalations + false_escalations + missed_escalations

        cycle_times = [
            duration
            for task in verified
            if (
                duration := self._duration_minutes(
                    task.started_at or task.created_at,
                    task.verified_at or task.closed_at,
                )
            )
            is not None
        ]
        median_cycle = round(median(cycle_times), 3) if cycle_times else 0.0

        now = datetime.now(UTC)
        active = [
            task
            for task in tasks
            if task.status not in {TaskStatus.CLOSED, TaskStatus.CANCELLED, TaskStatus.VERIFIED}
        ]
        stalled = [
            task for task in active if task.next_check_at and _as_utc(task.next_check_at) < now
        ]
        stalled_rate = len(stalled) / len(active) if active else 0.0

        failures = self.ledger.list_records("execution_failure")
        agent_failure_rate = len(failures) / len(tasks) if tasks else 0.0

        approvals = self.ledger.list_records("approval")
        approval_times = [
            duration
            for record in approvals
            if (
                duration := self._duration_minutes(
                    record.get("requested_at"),
                    record.get("decided_at"),
                )
            )
            is not None
        ]
        approval_median = round(median(approval_times), 3) if approval_times else 0.0

        conflicts = self.ledger.list_records("conflict")
        conflict_rate = len(conflicts) / len(tasks) if tasks else 0.0
        loops = self.ledger.list_records("coordination_loop")
        loop_rate = len(loops) / len(tasks) if tasks else 0.0

        costs = sum(float(record.get("amount", 0.0)) for record in self.ledger.list_records("cost"))
        cost_per_verified = round(costs / len(verified), 4) if verified else 0.0

        answer_records = self.ledger.list_records("answer_desk")
        deflected = [
            record
            for record in answer_records
            if record.get("disposition") in {"ANSWERED", "RECOMMENDATION_PROVIDED", "ROUTED"}
        ]
        answer_deflection = len(deflected) / len(answer_records) if answer_records else 0.0
        answer_resolution_times = [
            duration
            for record in answer_records
            if (
                duration := self._duration_minutes(
                    record.get("received_at"),
                    record.get("resolved_at"),
                )
            )
            is not None
        ]

        contributor_counts = [len(task.contributors) for task in tasks]
        avg_contributors = (
            sum(contributor_counts) / len(contributor_counts) if contributor_counts else 0.0
        )

        return {
            "verified_outcomes": len(verified),
            "verified_outcome_rate": round(verified_outcome_rate, 4),
            "tasks_resolved_without_ceo": len(resolved_without_ceo),
            "work_resolved_without_michael_rate": round(work_without_michael_rate, 4),
            "questions_deflected_from_michael": len(deflected),
            "questions_deflected_from_michael_rate": round(answer_deflection, 4),
            "ceo_touches_per_completed_task": round(ceo_touches_per_completed, 4),
            "ceo_time_avoided_minutes": time_avoided,
            "first_pass_acceptance_rate": round(first_pass_rate, 4),
            "rework_rate": round(rework_rate, 4),
            "correct_escalations": correct_escalations,
            "false_escalations": false_escalations,
            "missed_escalations": missed_escalations,
            "correct_escalation_rate": round(correct_escalations / escalation_total, 4)
            if escalation_total
            else 0.0,
            "false_escalation_rate": round(false_escalations / escalation_total, 4)
            if escalation_total
            else 0.0,
            "missed_escalation_rate": round(missed_escalations / escalation_total, 4)
            if escalation_total
            else 0.0,
            "median_cycle_time_minutes": median_cycle,
            "stalled_task_rate": round(stalled_rate, 4),
            "execution_failures": len(failures),
            "agent_failure_rate": round(agent_failure_rate, 4),
            "approval_median_time_minutes": approval_median,
            "conflicts": len(conflicts),
            "cross_agent_conflict_rate": round(conflict_rate, 4),
            "coordination_loops": len(loops),
            "agent_conversation_loop_rate": round(loop_rate, 4),
            "avg_contributors_per_task": round(avg_contributors, 4),
            "cost_per_verified_outcome": cost_per_verified,
            "answer_desk_deflection_rate": round(answer_deflection, 4),
            "answer_desk_incorrect_answers": sum(
                1 for record in answer_records if record.get("incorrect")
            ),
            "answer_desk_corrected_answers": sum(
                1 for record in answer_records if record.get("corrected")
            ),
            "answer_desk_access_control_failures": sum(
                1 for record in answer_records if record.get("access_control_failure")
            ),
            "answer_desk_median_resolution_minutes": round(
                median(answer_resolution_times), 3
            )
            if answer_resolution_times
            else 0.0,
        }
