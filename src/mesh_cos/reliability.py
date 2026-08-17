from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Callable, Mapping, TypeVar

from .ledger import TaskLedger

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    max_attempts: int = 3
    retry_exceptions: tuple[type[BaseException], ...] = (TimeoutError, ConnectionError)
    backoff_seconds: float = 0.0
    timeout_seconds: float | None = None


def _invoke_with_timeout(fn: Callable[[], T], timeout_seconds: float | None) -> T:
    if timeout_seconds is None:
        return fn()
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout_seconds)
    except FutureTimeoutError as exc:
        future.cancel()
        raise TimeoutError(f"Execution timed out after {timeout_seconds} seconds") from exc
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def execute_with_policy(fn: Callable[[], T], policy: ExecutionPolicy) -> T:
    if policy.max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    last_error: BaseException | None = None
    retry_exceptions = tuple(set(policy.retry_exceptions + (TimeoutError,)))
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return _invoke_with_timeout(fn, policy.timeout_seconds)
        except retry_exceptions as exc:
            last_error = exc
            if attempt == policy.max_attempts:
                raise
            if policy.backoff_seconds:
                sleep(policy.backoff_seconds * attempt)
    assert last_error is not None
    raise last_error


def assert_runtime_enabled(env: Mapping[str, str] | None = None) -> None:
    source = env if env is not None else os.environ
    value = str(source.get("MESH_COS_KILL_SWITCH", "false")).strip().lower()
    if value in {"1", "true", "yes", "on"}:
        raise RuntimeError("Mesh CoS kill switch is enabled")


class ExecutionLeaseManager:
    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def acquire(self, task_id: str, owner: str, *, ttl_seconds: int) -> bool:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be positive")
        now = datetime.now(timezone.utc)
        current = self.ledger.get_record("execution_lease", task_id)
        if current:
            expires_at = datetime.fromisoformat(current["expires_at"])
            if expires_at > now and current["owner"] != owner:
                return False
        record = {
            "task_id": task_id,
            "owner": owner,
            "acquired_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=ttl_seconds)).isoformat(),
        }
        self.ledger.save_record("execution_lease", task_id, record)
        return True

    def release(self, task_id: str, owner: str) -> None:
        current = self.ledger.get_record("execution_lease", task_id)
        if current is None:
            return
        if current["owner"] != owner:
            raise PermissionError("Only the lease owner may release the lease")
        self.ledger.delete_record("execution_lease", task_id)
