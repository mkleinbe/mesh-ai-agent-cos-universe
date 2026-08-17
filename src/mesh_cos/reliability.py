from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import time
from typing import Callable, TypeVar

from .ledger import TaskLedger
from .runtime import KillSwitch

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    max_attempts: int = 3
    timeout_seconds: float = 30.0
    retry_delay_seconds: float = 0.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


def execute_with_policy(function: Callable[[], T], policy: ExecutionPolicy) -> T:
    KillSwitch.assert_automation_allowed()
    last_error: BaseException | None = None
    for attempt in range(1, policy.max_attempts + 1):
        try:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(function)
                return future.result(timeout=policy.timeout_seconds)
        except FutureTimeoutError as exc:
            last_error = TimeoutError(f"Execution timed out after {policy.timeout_seconds}s")
            if attempt == policy.max_attempts:
                raise last_error from exc
        except Exception as exc:  # bounded retries intentionally cover tool/runtime failures
            last_error = exc
            if attempt == policy.max_attempts:
                raise
        if policy.retry_delay_seconds:
            time.sleep(policy.retry_delay_seconds)
    if last_error:
        raise last_error
    raise RuntimeError("Execution policy terminated without a result")


class WorkLease:
    def __init__(self, ledger: TaskLedger, *, lease_seconds: int = 300) -> None:
        self.ledger = ledger
        self.lease_seconds = lease_seconds

    def _expiry(self) -> str:
        return (datetime.now(timezone.utc) + timedelta(seconds=self.lease_seconds)).isoformat()

    def acquire(self, task_id: str, owner: str) -> bool:
        return self.ledger.claim_lease(task_id, owner, self._expiry())

    def heartbeat(self, task_id: str, owner: str) -> bool:
        return self.ledger.heartbeat_lease(task_id, owner, self._expiry())

    def release(self, task_id: str, owner: str) -> bool:
        return self.ledger.release_lease(task_id, owner)
