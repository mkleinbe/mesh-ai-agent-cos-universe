from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .models import AuthorityLevel, TaskRecord, TaskStatus, utcnow


class TaskLedger:
    """Canonical Phase 1 persistence boundary."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        statements = [
            "CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, event_type TEXT, timestamp TEXT, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY, result_ref TEXT, created_at TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS intake_keys (key TEXT PRIMARY KEY, task_id TEXT NOT NULL UNIQUE)",
            "CREATE TABLE IF NOT EXISTS delegations (delegation_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, accountable_agent TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS approvals (approval_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS decisions (decision_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS conflicts (conflict_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, disposition TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS performance_events (performance_event_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, task_id TEXT NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS scorecards (scorecard_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, window_start TEXT NOT NULL, window_end TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS registry_changes (change_id TEXT PRIMARY KEY, agent_id TEXT NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS verifications (verification_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, passed INTEGER NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS thread_mappings (task_id TEXT PRIMARY KEY, channel_id TEXT NOT NULL, thread_ts TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS metrics (metric_id TEXT PRIMARY KEY, metric_name TEXT NOT NULL, task_id TEXT, agent_id TEXT, timestamp TEXT NOT NULL, value REAL, payload TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS work_leases (task_id TEXT PRIMARY KEY, owner TEXT NOT NULL, expires_at TEXT NOT NULL, heartbeat_at TEXT NOT NULL)",
        ]
        with self.conn:
            for statement in statements:
                self.conn.execute(statement)

    @staticmethod
    def _json(payload: dict[str, Any]) -> str:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def save_task(self, task: TaskRecord) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT INTO tasks(task_id,payload) VALUES(?,?) ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload",
                (task.task_id, self._json(task.to_dict())),
            )

    def get_task(self, task_id: str) -> TaskRecord | None:
        row = self.conn.execute("SELECT payload FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        data.pop("version", None)
        data["status"] = TaskStatus(data["status"])
        data["authority_level"] = AuthorityLevel(data["authority_level"])
        return TaskRecord(**data)

    def list_tasks(self) -> list[TaskRecord]:
        ids = [r[0] for r in self.conn.execute("SELECT task_id FROM tasks ORDER BY task_id")]
        return [task for task_id in ids if (task := self.get_task(task_id)) is not None]

    def register_intake_key(self, key: str, task_id: str) -> bool:
        try:
            with self.conn:
                self.conn.execute("INSERT INTO intake_keys(key,task_id) VALUES(?,?)", (key, task_id))
            return True
        except sqlite3.IntegrityError:
            return False

    def task_for_intake_key(self, key: str) -> str | None:
        row = self.conn.execute("SELECT task_id FROM intake_keys WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else None

    def claim_idempotency(self, key: str, result_ref: str | None = None) -> bool:
        try:
            with self.conn:
                self.conn.execute("INSERT INTO idempotency(key,result_ref,created_at) VALUES(?,?,?)", (key, result_ref, utcnow()))
            return True
        except sqlite3.IntegrityError:
            return False

    def idempotency_result(self, key: str) -> str | None:
        row = self.conn.execute("SELECT result_ref FROM idempotency WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row and row[0] is not None else None

    def record_event(self, event: dict[str, Any]) -> bool:
        key = event["idempotency_key"]
        if not self.claim_idempotency(key, event.get("event_id")):
            return False
        try:
            with self.conn:
                self.conn.execute(
                    "INSERT INTO events(event_id,task_id,event_type,timestamp,payload) VALUES(?,?,?,?,?)",
                    (event["event_id"], event["task_id"], event.get("event_type"), event.get("timestamp", utcnow()), self._json(event)),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def list_events(self, task_id: str | None = None) -> list[dict[str, Any]]:
        if task_id is None:
            rows = self.conn.execute("SELECT payload FROM events ORDER BY timestamp,event_id")
        else:
            rows = self.conn.execute("SELECT payload FROM events WHERE task_id=? ORDER BY timestamp,event_id", (task_id,))
        return [json.loads(r[0]) for r in rows]

    def _save_record(self, table: str, id_column: str, record_id: str, payload: dict[str, Any], *, columns: dict[str, Any]) -> None:
        names = [id_column, *columns.keys(), "payload"]
        values = [record_id, *columns.values(), self._json(payload)]
        placeholders = ",".join("?" for _ in names)
        updates = ",".join(f"{name}=excluded.{name}" for name in names[1:])
        sql = f"INSERT INTO {table}({','.join(names)}) VALUES({placeholders}) ON CONFLICT({id_column}) DO UPDATE SET {updates}"
        with self.conn:
            self.conn.execute(sql, values)

    def _get_record(self, table: str, id_column: str, record_id: str) -> dict[str, Any] | None:
        row = self.conn.execute(f"SELECT payload FROM {table} WHERE {id_column}=?", (record_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def _list_records(self, table: str, where: str = "", args: Iterable[Any] = ()) -> list[dict[str, Any]]:
        sql = f"SELECT payload FROM {table}" + (f" WHERE {where}" if where else "") + " ORDER BY rowid"
        return [json.loads(r[0]) for r in self.conn.execute(sql, tuple(args))]

    def save_delegation(self, payload: dict[str, Any]) -> None:
        self._save_record("delegations", "delegation_id", payload["delegation_id"], payload, columns={"task_id": payload["task_id"], "accountable_agent": payload["accountable_agent"], "status": payload.get("status", "ACTIVE")})

    def get_delegation(self, delegation_id: str) -> dict[str, Any] | None:
        return self._get_record("delegations", "delegation_id", delegation_id)

    def list_delegations(self, task_id: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        conditions: list[str] = []
        args: list[Any] = []
        if task_id:
            conditions.append("task_id=?")
            args.append(task_id)
        if status:
            conditions.append("status=?")
            args.append(status)
        return self._list_records("delegations", " AND ".join(conditions), args)

    def active_owner_for_task(self, task_id: str) -> str | None:
        row = self.conn.execute("SELECT accountable_agent FROM delegations WHERE task_id=? AND status='ACTIVE' ORDER BY rowid DESC LIMIT 1", (task_id,)).fetchone()
        return str(row[0]) if row else None

    def save_approval(self, payload: dict[str, Any]) -> None:
        self._save_record("approvals", "approval_id", payload["approval_id"], payload, columns={"task_id": payload["task_id"], "status": payload["status"]})

    def get_approval(self, approval_id: str) -> dict[str, Any] | None:
        return self._get_record("approvals", "approval_id", approval_id)

    def list_approvals(self, task_id: str | None = None) -> list[dict[str, Any]]:
        return self._list_records("approvals", "task_id=?" if task_id else "", (task_id,) if task_id else ())

    def save_decision(self, payload: dict[str, Any]) -> None:
        self._save_record("decisions", "decision_id", payload["decision_id"], payload, columns={"task_id": payload["task_id"]})

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        return self._get_record("decisions", "decision_id", decision_id)

    def save_conflict(self, payload: dict[str, Any]) -> None:
        self._save_record("conflicts", "conflict_id", payload["conflict_id"], payload, columns={"task_id": payload["task_id"], "disposition": payload.get("disposition", "OPEN")})

    def get_conflict(self, conflict_id: str) -> dict[str, Any] | None:
        return self._get_record("conflicts", "conflict_id", conflict_id)

    def list_conflicts(self, task_id: str | None = None) -> list[dict[str, Any]]:
        return self._list_records("conflicts", "task_id=?" if task_id else "", (task_id,) if task_id else ())

    def save_performance_event(self, payload: dict[str, Any]) -> None:
        self._save_record("performance_events", "performance_event_id", payload["performance_event_id"], payload, columns={"agent_id": payload["agent_id"], "task_id": payload["task_id"], "timestamp": payload["timestamp"]})

    def list_performance_events(self, agent_id: str | None = None) -> list[dict[str, Any]]:
        return self._list_records("performance_events", "agent_id=?" if agent_id else "", (agent_id,) if agent_id else ())

    def save_scorecard(self, payload: dict[str, Any]) -> None:
        self._save_record("scorecards", "scorecard_id", payload["scorecard_id"], payload, columns={"agent_id": payload["agent_id"], "window_start": payload["window_start"], "window_end": payload["window_end"]})

    def list_scorecards(self, agent_id: str | None = None) -> list[dict[str, Any]]:
        return self._list_records("scorecards", "agent_id=?" if agent_id else "", (agent_id,) if agent_id else ())

    def save_registry_change(self, payload: dict[str, Any]) -> None:
        self._save_record("registry_changes", "change_id", payload["change_id"], payload, columns={"agent_id": payload["agent_id"], "timestamp": payload.get("timestamp", utcnow())})

    def save_verification(self, payload: dict[str, Any]) -> None:
        self._save_record("verifications", "verification_id", payload["verification_id"], payload, columns={"task_id": payload["task_id"], "passed": 1 if payload["passed"] else 0, "timestamp": payload.get("timestamp", utcnow())})

    def list_verifications(self, task_id: str) -> list[dict[str, Any]]:
        return self._list_records("verifications", "task_id=?", (task_id,))

    def set_thread_mapping(self, task_id: str, channel_id: str, thread_ts: str) -> None:
        with self.conn:
            self.conn.execute("INSERT INTO thread_mappings(task_id,channel_id,thread_ts) VALUES(?,?,?) ON CONFLICT(task_id) DO UPDATE SET channel_id=excluded.channel_id,thread_ts=excluded.thread_ts", (task_id, channel_id, thread_ts))

    def get_thread_mapping(self, task_id: str) -> dict[str, str] | None:
        row = self.conn.execute("SELECT channel_id,thread_ts FROM thread_mappings WHERE task_id=?", (task_id,)).fetchone()
        return {"channel_id": str(row[0]), "thread_ts": str(row[1])} if row else None

    def record_metric(self, payload: dict[str, Any]) -> None:
        self._save_record("metrics", "metric_id", payload["metric_id"], payload, columns={"metric_name": payload["metric_name"], "task_id": payload.get("task_id"), "agent_id": payload.get("agent_id"), "timestamp": payload.get("timestamp", utcnow()), "value": payload.get("value")})

    def list_metrics(self, metric_name: str | None = None) -> list[dict[str, Any]]:
        return self._list_records("metrics", "metric_name=?" if metric_name else "", (metric_name,) if metric_name else ())

    def claim_lease(self, task_id: str, owner: str, expires_at: str) -> bool:
        try:
            with self.conn:
                self.conn.execute("INSERT INTO work_leases(task_id,owner,expires_at,heartbeat_at) VALUES(?,?,?,?)", (task_id, owner, expires_at, utcnow()))
            return True
        except sqlite3.IntegrityError:
            return False

    def heartbeat_lease(self, task_id: str, owner: str, expires_at: str) -> bool:
        with self.conn:
            cur = self.conn.execute("UPDATE work_leases SET expires_at=?,heartbeat_at=? WHERE task_id=? AND owner=?", (expires_at, utcnow(), task_id, owner))
        return cur.rowcount == 1

    def release_lease(self, task_id: str, owner: str) -> bool:
        with self.conn:
            cur = self.conn.execute("DELETE FROM work_leases WHERE task_id=? AND owner=?", (task_id, owner))
        return cur.rowcount == 1
