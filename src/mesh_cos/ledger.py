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

    def get_task(self, task_id: str) -> TaskRecord | None:
        row = self.conn.execute("SELECT payload FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        data["status"] = TaskStatus(data["status"])
        data["authority_level"] = AuthorityLevel(data["authority_level"])
        return TaskRecord(**data)

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
            return True
        except sqlite3.IntegrityError:
            return False
