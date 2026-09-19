from __future__ import annotations

from datetime import date, timedelta
from hashlib import sha256
from typing import Any

BUSINESS_STATES = {
    "BUSINESS_PROGRESS",
    "RESPONSIBLE_NO_ACTION",
    "BUSINESS_FAILURE",
    "SYSTEM_FAILURE",
}
INVOCATION_MODES = {"AD_HOC", "SCHEDULED", "EVENT_TRIGGERED"}
LOOP_ID = "LOOP-COM-001"
HITL_LOOP_ID = "LOOP-COM-HITL-001"


def _first_weekday(year: int, month: int) -> date:
    current = date(year, month, 1)
    while current.weekday() >= 5:
        current += timedelta(days=1)
    return current


def _quarter(as_of: date) -> tuple[int, int]:
    quarter = ((as_of.month - 1) // 3) + 1
    start_month = 1 + (quarter - 1) * 3
    return quarter, start_month


def due_reviews(as_of: date, completed_period_keys: set[str] | None = None) -> list[dict[str, Any]]:
    """Return canonical due reviews. Quarterly review subsumes the same-day monthly review."""
    completed = completed_period_keys or set()
    month_key = f"MONTH:{as_of:%Y-%m}"
    monthly_due = as_of >= _first_weekday(as_of.year, as_of.month) and month_key not in completed

    quarter, start_month = _quarter(as_of)
    quarter_key = f"QUARTER:{as_of.year}-Q{quarter}"
    quarter_due_date = _first_weekday(as_of.year, start_month)
    quarterly_due = as_of >= quarter_due_date and quarter_key not in completed

    if quarterly_due:
        keys = [quarter_key]
        if monthly_due:
            keys.append(month_key)
        return [{
            "review": "QUARTERLY",
            "period_key": quarter_key,
            "subsumes_monthly": monthly_due,
            "completion_keys": keys,
        }]
    if monthly_due:
        return [{
            "review": "MONTHLY",
            "period_key": month_key,
            "subsumes_monthly": False,
            "completion_keys": [month_key],
        }]
    return []


def trigger_semantics(
    invocation_mode: str,
    *,
    native_event_delivery: bool = False,
    provider_bound: bool = False,
) -> dict[str, Any]:
    mode = invocation_mode.upper()
    if mode not in INVOCATION_MODES:
        return {"eligible": False, "business_state": "SYSTEM_FAILURE", "reason_code": "invalid-invocation-mode"}
    if mode != "EVENT_TRIGGERED":
        return {
            "eligible": True,
            "trigger_class": "SCHEDULED_ELIGIBILITY" if mode == "SCHEDULED" else "AD_HOC",
            "business_state": None,
            "reason_code": "valid-invocation",
        }
    if not native_event_delivery:
        return {
            "eligible": False,
            "trigger_class": "UNSUPPORTED_AS_EVENT",
            "business_state": "SYSTEM_FAILURE",
            "reason_code": "event-source-not-natively-delivered",
        }
    if not provider_bound:
        return {
            "eligible": False,
            "trigger_class": "UNSUPPORTED_AS_EVENT",
            "business_state": "SYSTEM_FAILURE",
            "reason_code": "event-provider-boundary-unverified",
        }
    return {
        "eligible": True,
        "trigger_class": "NATIVE_EVENT",
        "business_state": None,
        "reason_code": "native-event-verified",
    }


def classify_checkpoint(
    *,
    source_authority_ok: bool = True,
    system_integrity_ok: bool = True,
    business_regressed: bool = False,
    outcome_advanced: bool = False,
    buyer_owned_commitment_created: bool = False,
    work_evaluated: bool = True,
    action_warranted: bool = False,
) -> str:
    if not source_authority_ok or not system_integrity_ok:
        return "SYSTEM_FAILURE"
    if business_regressed:
        return "BUSINESS_FAILURE"
    if outcome_advanced or buyer_owned_commitment_created:
        return "BUSINESS_PROGRESS"
    if work_evaluated and not action_warranted:
        return "RESPONSIBLE_NO_ACTION"
    return "SYSTEM_FAILURE"


def execution_key(
    *,
    loop_id: str,
    occurrence_key: str,
    invocation_mode: str,
    native_event_id: str | None = None,
) -> str:
    mode = invocation_mode.upper()
    trigger = trigger_semantics(
        mode,
        native_event_delivery=(mode != "EVENT_TRIGGERED" or native_event_id is not None),
        provider_bound=(mode != "EVENT_TRIGGERED" or native_event_id is not None),
    )
    if not trigger["eligible"]:
        raise ValueError(trigger["reason_code"])
    material = "|".join([loop_id, occurrence_key, mode, native_event_id or ""])
    return "commercial:" + sha256(material.encode("utf-8")).hexdigest()


def build_dispatch_plan(
    *,
    as_of: date,
    invocation_mode: str,
    completed_period_keys: set[str] | None = None,
    native_event_delivery: bool = False,
    provider_bound: bool = False,
    native_event_id: str | None = None,
    fresh_evidence_available: bool = True,
) -> dict[str, Any]:
    trigger = trigger_semantics(
        invocation_mode,
        native_event_delivery=native_event_delivery,
        provider_bound=provider_bound,
    )
    if not trigger["eligible"]:
        return {
            "loop_id": LOOP_ID,
            "business_state": "SYSTEM_FAILURE",
            "reason_code": trigger["reason_code"],
            "trigger_class": trigger.get("trigger_class"),
            "reviews": [],
            "reuse_fresh_evidence": fresh_evidence_available,
        }

    reviews = due_reviews(as_of, completed_period_keys)
    occurrence = native_event_id or (reviews[0]["period_key"] if reviews else f"WAKE:{as_of.isoformat()}")
    key = execution_key(
        loop_id=LOOP_ID,
        occurrence_key=occurrence,
        invocation_mode=invocation_mode,
        native_event_id=native_event_id,
    )
    return {
        "loop_id": LOOP_ID,
        "hitl_loop_id": HITL_LOOP_ID,
        "business_state": "RESPONSIBLE_NO_ACTION" if not reviews else None,
        "reason_code": "no-due-commercial-work" if not reviews else "due-commercial-work",
        "trigger_class": trigger["trigger_class"],
        "reviews": reviews,
        "reuse_fresh_evidence": fresh_evidence_available,
        "idempotency_key": key,
        "scheduler_wake_is_business_progress": False,
        "completion_equals_verification": False,
    }
