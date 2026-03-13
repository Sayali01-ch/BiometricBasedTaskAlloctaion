import os
import sqlite3
import threading
from datetime import datetime, timezone


_LOCK = threading.Lock()


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with _LOCK, self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    status TEXT NOT NULL DEFAULT 'Offline',
                    last_seen_at TEXT,
                    fcm_token TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    assigned_to TEXT,
                    assigned_at TEXT,
                    status TEXT NOT NULL DEFAULT 'Created',
                    FOREIGN KEY (assigned_to) REFERENCES employees (id)
                )
                """
            )
            conn.commit()

    def upsert_employee_available(self, employee_id: str, name: str | None = None) -> dict:
        now = _utc_now_iso()
        with _LOCK, self.connect() as conn:
            conn.execute(
                """
                INSERT INTO employees (id, name, status, last_seen_at)
                VALUES (?, COALESCE(?, ?), 'Available', ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = COALESCE(excluded.name, employees.name),
                    status = 'Available',
                    last_seen_at = excluded.last_seen_at
                """,
                (employee_id, name, employee_id, now),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
            return dict(row) if row else {"id": employee_id, "name": name or employee_id, "status": "Available"}

    def list_employees(self) -> list[dict]:
        with _LOCK, self.connect() as conn:
            rows = conn.execute("SELECT * FROM employees ORDER BY id ASC").fetchall()
            return [dict(r) for r in rows]

    def set_employee_fcm_token(self, employee_id: str, token: str) -> dict | None:
        with _LOCK, self.connect() as conn:
            conn.execute(
                """
                INSERT INTO employees (id, status, fcm_token, last_seen_at)
                VALUES (?, 'Offline', ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    fcm_token = excluded.fcm_token
                """,
                (employee_id, token, _utc_now_iso()),
            )
            conn.commit()
            row = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
            return dict(row) if row else None

    def assign_task(self, employee_id: str, title: str, description: str | None) -> dict:
        now = _utc_now_iso()
        with _LOCK, self.connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks (title, description, assigned_to, assigned_at, status)
                VALUES (?, ?, ?, ?, 'Assigned')
                """,
                (title, description, employee_id, now),
            )
            conn.execute(
                "UPDATE employees SET status = 'Busy' WHERE id = ?",
                (employee_id,),
            )
            conn.commit()
            task = conn.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 1").fetchone()
            return dict(task)

    def get_employee(self, employee_id: str) -> dict | None:
        with _LOCK, self.connect() as conn:
            row = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()
            return dict(row) if row else None

