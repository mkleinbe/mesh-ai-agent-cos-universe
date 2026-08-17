from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .models import AuthorityLevel, TaskRecord, TaskStatus


class TaskLedger:
    """Canonical persistence boundary for Phase 1 control-plane state."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, payload TEXT NOT NULL)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS records (kind TEXT NOT NULL, record_id TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(kind, record_id))")
        self.conn.execute("CREATE TABLE IF NOT EXISTS task_threads (task_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL, thread_ts TEXT NOT NULL)")
        self.conn.commit()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            self.conn.execute("BEGIN")
            yield self.conn
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def save_task(self, task: TaskRecord) -> None:
        self.conn.execute(
            "INSERT INTO tasks(task_id,payload) VALUES(?,?) ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload",
            (task.task_id, json.dumps(task.to_dict(), sort_keys=True)),
        )
        self.conn.commit()

    def _task_from_payload(self, payload: str) -> TaskRecord:
        data = json.loads(payload)
        data.pop("version", None)
        data["status"] = TaskStatus(data["status"])
        data["authority_level"] = AuthorityLevel(data["authority_level"])
        return TaskRecord(**data)

    def get_task(self, task_id: str) -> TaskRecord | None:
        row = self.conn.execute("SELECT payload FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return self._task_from_payload(row[0]) if row else None

    def list_tasks(self) -> list[TaskRecord]:
        rows = self.conn.execute("SELECT payload FROM tasks ORDER BY task_id").fetchall()
        return [self._task_from_payload(row[0]) for row in rows]

    def save_record(self, kind: str, record_id: str, payload: dict) -> None:
        self.conn.execute(
            "INSERT INTO records(kind,record_id,payload) VALUES(?,?,?) ON CONFLICT(kind,record_id) DO UPDATE SET payload=excluded.payload",
            (kind, record_id, json.dumps(payload, sort_keys=True)),
        )
        self.conn.commit()

    def get_record(self, kind: str, record_id: str) -> dict | None:
        row = self.conn.execute("SELECT payload FROM records WHERE kind=? AND record_id=?", (kind, record_id)).fetchone()
        return json.loads(row[0]) if row else None

    def list_records(self, kind: str) -> list[dict]:
        rows = self.conn.execute("SELECT payload FROM records WHERE kind=? ORDER BY record_id", (kind,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def delete_record(self, kind: str, record_id: str) -> None:
        self.conn.execute("DELETE FROM records WHERE kind=? AND record_id=?", (kind, record_id))
        self.conn.commit()

    def bind_thread(self, task_id: str, channel_id: str, thread_ts: str) -> dict:
        self.conn.execute(
            "INSERT INTO task_threads(task_id,channel_id,thread_ts) VALUES(?,?,?) ON CONFLICT(task_id) DO UPDATE SET channel_id=excluded.channel_id, thread_ts=excluded.thread_ts",
            (task_id, channel_id, thread_ts),
        )
        self.conn.commit()
        return {"task_id": task_id, "channel_id": channel_id, "thread_ts": thread_ts}

    def get_thread(self, task_id: str) -> dict | None:
        row = self.conn.execute("SELECT channel_id,thread_ts FROM task_threads WHERE task_id=?", (task_id,)).fetchone()
        return {"task_id": task_id, "channel_id": row[0], "thread_ts": row[1]} if row else None

    def claim_idempotency_key(self, key: str) -> bool:
        try:
            self.conn.execute("INSERT INTO idempotency(key) VALUES(?)", (key,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False

    def record_event(self, event: dict) -> bool:
        key = event["idempotency_key"]
        try:
            with self.transaction():
                self.conn.execute("INSERT INTO idempotency(key) VALUES(?)", (key,))
                self.conn.execute(
                    "INSERT INTO events(event_id,task_id,payload) VALUES(?,?,?)",
                    (event["event_id"], event["task_id"], json.dumps(event, sort_keys=True)),
                )
        except sqlite3.IntegrityError:
            return False
        if event.get("version") == "mesh.cos.agent-event.v1":
            self._bridge_legacy_event(event)
        return True

    def _bridge_legacy_event(self, event: dict) -> None:
        """Dual-write legacy audit envelopes into the richer v2 canonical governance stream."""
        from .governance import GovernanceJournal

        actor = str(event.get("actor_agent", "unknown"))
        actor_type = "SERVICE" if actor.endswith("-service") else "AGENT"
        evidence = event.get("evidence_references") or []
        error = event.get("error")
        GovernanceJournal(self).record_event(
            event_type=str(event.get("event_type", "legacy.event")),
            event_category="GOVERNANCE",
            action=str(event.get("event_type", "legacy.event")).upper(),
            actor_type=actor_type,
            actor_id=actor,
            actor_role=actor,
            task_id=event.get("task_id"),
            correlation_id=str(event.get("correlation_id") or f"legacy:{event['event_id']}"),
            authority_level=int(event.get("authority_level", 0)),
            policy_rule_ids=["governance-policy-v1", "legacy-agent-event-v1-bridge"],
            capability_tool=str(event.get("source", "mesh-cos")),
            target_resource=str(event.get("task_id") or "control-plane"),
            source_system=str(event.get("source", "mesh-cos")),
            input_summary="Legacy agent-event v1 envelope bridged to the v2 auditable governance stream.",
            result_status="FAILURE" if error else "SUCCESS",
            output_summary=str(event.get("result", "recorded")),
            before_state_ref="legacy-v1-before-state" if event.get("before_state") is not None else None,
            after_state_ref="legacy-v1-after-state" if event.get("after_state") is not None else None,
            evidence_references=list(evidence),
            approval_reference=event.get("approval_reference"),
            risk_severity="MEDIUM" if error else "LOW",
            data_classification="INTERNAL",
            error_code="LEGACY_EVENT_ERROR" if error else None,
            error_summary=str(error) if error else None,
            model_provider=None,
            model_id_version=None,
            skill_agent_version="legacy-agent-event-v1",
            environment="RUNTIME",
            retention_class="GOVERNANCE_LONG_TERM",
            idempotency_key=f"bridge:{event['event_id']}",
        )

    def list_events(self) -> list[dict]:
        rows = self.conn.execute("SELECT payload FROM events ORDER BY rowid").fetchall()
        return [json.loads(row[0]) for row in rows]
