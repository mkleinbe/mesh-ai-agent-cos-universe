from __future__ import annotations

from datetime import datetime, timezone


def _as_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def readiness(
    *,
    capability_match: bool,
    availability_checked_at: str | None,
    max_age_days: int,
    rate_valid: bool,
    contracting_ready: bool,
    availability_confirmed: bool,
) -> str:
    if max_age_days < 0:
        raise ValueError("max_age_days must be non-negative")
    if not capability_match:
        return "NOT_A_FIT"
    if not availability_checked_at:
        return "REQUIRES_REFRESH"
    checked_at = _as_utc(availability_checked_at)
    if (datetime.now(timezone.utc) - checked_at).days > max_age_days or not availability_confirmed:
        return "REQUIRES_REFRESH"
    if not rate_valid or not contracting_ready:
        return "NOT_READY"
    return "STAFFING_READY"
