from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from .models import TaskRecord, TaskStatus, AuthorityLevel

class TaskLedger:
    def __init__(self, path: str | Path = ':memory:') -> None:
        self.conn = sqlite3.connect(str(path))
        self.conn.execute('CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, payload TEXT NOT NULL)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS idempotency (key TEXT PRIMARY KEY)')
        self.conn.commit()

    def save_task(self, task: TaskRecord) -> None:
        self.conn.execute('INSERT INTO tasks(task_id,payload) VALUES(?,?) ON CONFLICT(task_id) DO UPDATE SET payload=excluded.payload',
                          (task.task_id, json.dumps(task.to_dict(), sort_keys=True)))
        self.conn.commit()

    def get_task(self, task_id: str) -> TaskRecord | None:
        row = self.conn.execute('SELECT payload FROM tasks WHERE task_id=?', (task_id,)).fetchone()
        if not row:
            return None
        data = json.loads(row[0])
        data['status'] = TaskStatus(data['status'])
        data['authority_level'] = AuthorityLevel(data['authority_level'])
        return TaskRecord(**data)

    def record_event(self, event: dict) -> bool:
        key = event['idempotency_key']
        try:
            self.conn.execute('INSERT INTO idempotency(key) VALUES(?)', (key,))
            self.conn.execute('INSERT INTO events(event_id,task_id,payload) VALUES(?,?,?)',
                              (event['event_id'], event['task_id'], json.dumps(event, sort_keys=True)))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False
