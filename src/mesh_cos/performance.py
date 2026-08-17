from __future__ import annotations

from dataclasses import dataclass

DEFAULT_WEIGHTS = {
    "outcome_achievement": 0.30,
    "first_pass_quality": 0.20,
    "escalation_judgment": 0.15,
    "evidence_governance": 0.10,
    "execution_reliability": 0.10,
    "ceo_leverage": 0.10,
    "efficiency": 0.05,
}


@dataclass(frozen=True, slots=True)
class PerformanceEvent:
    agent_id: str
    task_id: str
    category: str
    score: float
    severity: str = "LOW"
    reason: str = ""


def score(events: list[PerformanceEvent], weights: dict[str, float] | None = None) -> float:
    weights = weights or DEFAULT_WEIGHTS
    grouped: dict[str, list[float]] = {}
    for event in events:
        grouped.setdefault(event.category, []).append(event.score)
    weighted = 0.0
    used = 0.0
    for category, weight in weights.items():
        values = grouped.get(category)
        if values:
            weighted += (sum(values) / len(values)) * weight
            used += weight
    return round(weighted / used, 4) if used else 0.0


def recommendation(events: list[PerformanceEvent]) -> str:
    if any(event.severity == "CRITICAL" for event in events):
        return "QUARANTINE"
    result = score(events)
    if result < 0.30:
        return "RESTRICT"
    if result < 0.65:
        return "WATCH"
    if result > 0.90 and len(events) >= 5:
        return "INCREASE_ROUTING"
    return "CONTINUE"
