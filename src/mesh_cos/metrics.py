from __future__ import annotations

from .ledger import TaskLedger


class MetricsService:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def summary(self) -> dict:
        records = self.ledger.list_records("metric_task")
        verified = [r for r in records if r.get("verified")]
        resolved_without_ceo = [r for r in verified if int(r.get("ceo_touches", 0)) == 0]
        time_avoided = sum(
            int(r.get("ceo_time_avoided_estimate_minutes", 0) or 0)
            for r in verified
            if r.get("methodology")
        )
        return {
            "verified_outcomes": len(verified),
            "tasks_resolved_without_ceo": len(resolved_without_ceo),
            "ceo_time_avoided_minutes": time_avoided,
        }
