from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Callable, Mapping, TypeVar

from .audit import AuditEvent
from .ledger import TaskLedger
from .models import new_id, utcnow

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
    retry_exceptions = tuple(set(policy.retry_exceptions + (TimeoutError,)))
    for attempt in range(1, policy.max_attempts + 1):
        try:
            return _invoke_with_timeout(fn, policy.timeout_seconds)
        except retry_exceptions:
            if attempt == policy.max_attempts:
                raise
            if policy.backoff_seconds:
                sleep(policy.backoff_seconds * attempt)
    raise RuntimeError("Execution policy exhausted without returning or raising")  # pragma: no cover


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
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at.astimezone(timezone.utc) > now and current["owner"] != owner:
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


class ReplayManager:
    """Durable partial-failure record and explicit replay/human-override boundary."""

    def __init__(self, ledger: TaskLedger) -> None:
        self.ledger = ledger

    def record_failure(
        self,
        effect_id: str,
        task_id: str,
        *,
        agent_id: str,
        error: BaseException,
        payload: dict | None = None,
    ) -> dict:
        record = {
            "effect_id": effect_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "error_type": type(error).__name__,
            "error": str(error),
            "payload": dict(payload or {}),
            "status": "FAILED",
            "failed_at": utcnow(),
            "replayed_at": None,
            "overridden_at": None,
        }
        self.ledger.save_record("execution_failure", effect_id, record)
        self._audit(record, "execution_failed", agent_id, str(error), error=str(error))
        return record

    def replay(
        self,
        effect_id: str,
        fn: Callable[[], T],
        *,
        actor: str,
        policy: ExecutionPolicy | None = None,
    ) -> T:
        assert_runtime_enabled()
        record = self.ledger.get_record("execution_failure", effect_id)
        if record is None:
            raise KeyError(effect_id)
        if record["status"] == "REPLAYED":
            existing = self.ledger.get_record("replay_result", effect_id)
            if existing is None:
                raise RuntimeError("Replay marked complete without a stored result")
            return existing["result"]  # type: ignore[return-value]
        if record["status"] == "OVERRIDDEN":
            raise RuntimeError("Human override closed this failed effect")
        result = execute_with_policy(fn, policy or ExecutionPolicy())
        record["status"] = "REPLAYED"
        record["replayed_at"] = utcnow()
        record["replayed_by"] = actor
        self.ledger.save_record("execution_failure", effect_id, record)
        self.ledger.save_record("replay_result", effect_id, {"effect_id": effect_id, "result": result})
        self._audit(record, "execution_replayed", actor, effect_id)
        return result

    def override(self, effect_id: str, *, actor: str, disposition: str, reason: str) -> dict:
        record = self.ledger.get_record("execution_failure", effect_id)
        if record is None:
            raise KeyError(effect_id)
        if record["status"] == "REPLAYED":
            raise RuntimeError("Cannot override an effect that has already been replayed")
        if record["status"] == "OVERRIDDEN":
            raise RuntimeError("Effect has already been overridden")
        record["status"] = "OVERRIDDEN"
        record["overridden_at"] = utcnow()
        record["overridden_by"] = actor
        record["override_disposition"] = disposition
        record["override_reason"] = reason
        self.ledger.save_record("execution_failure", effect_id, record)
        self.ledger.save_record(
            "human_override",
            effect_id,
            {
                "effect_id": effect_id,
                "actor": actor,
                "disposition": disposition,
                "reason": reason,
                "timestamp": utcnow(),
            },
        )
        self._audit(record, "execution_overridden", actor, f"{disposition}: {reason}")
        return record

    def _audit(
        self,
        failure_record: dict,
        event_type: str,
        actor: str,
        result: str,
        *,
        error: str | None = None,
    ) -> None:
        task_id = str(failure_record["task_id"])
        task = self.ledger.get_task(task_id)
        correlation_id = task.correlation_id if task else new_id("corr")
        authority = int(task.authority_level) if task else 0
        event = AuditEvent(
            event_type,
            actor,
            task_id,
            correlation_id,
            authority,
            result,
            error=error,
        )
        self.ledger.record_event(event.to_dict())
