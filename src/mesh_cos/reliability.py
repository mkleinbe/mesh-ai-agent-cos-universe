from __future__ import annotations

from dataclasses import dataclass
from time import sleep
from typing import Callable, TypeVar

T = TypeVar("T")

@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    max_attempts: int = 3
    retry_exceptions: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError)
    backoff_seconds: float = 0.0


def execute_with_policy(fn: Callable[[], T], policy: ExecutionPolicy) -> T:
    if policy.max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    last_error: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return fn()
        except policy.retry_exceptions as exc:
            last_error = exc
            if attempt == policy.max_attempts:
                raise
            if policy.backoff_seconds:
                sleep(policy.backoff_seconds * attempt)
    assert last_error is not None
    raise last_error
