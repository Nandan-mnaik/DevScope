import sqlite3
from pathlib import Path


class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, idea TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL)")
        self.connection.commit()

    def save_report(self, idea: str, payload: str, created_at: str) -> int:
        cursor = self.connection.execute("INSERT INTO reports(idea, payload, created_at) VALUES (?, ?, ?)", (idea, payload, created_at))
        self.connection.commit()
        return int(cursor.lastrowid)

    def latest(self) -> tuple | None:
        return self.connection.execute("SELECT id, idea, payload, created_at FROM reports ORDER BY id DESC LIMIT 1").fetchone()

    def list_reports(self) -> list[tuple]:
        return self.connection.execute("SELECT id, idea, created_at FROM reports ORDER BY id DESC").fetchall()
