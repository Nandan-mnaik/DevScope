import json
import math
import re
import sqlite3
from pathlib import Path


class VectorStore:
    """Small local vector store using SQLite and cosine similarity."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute("CREATE TABLE IF NOT EXISTS code_chunks (key TEXT PRIMARY KEY, repository TEXT, path TEXT, content TEXT, embedding TEXT)")
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def upsert(self, key: str, repository: str, path: str, content: str, embedding: list[float]) -> None:
        self.connection.execute("INSERT OR REPLACE INTO code_chunks VALUES (?, ?, ?, ?, ?)", (key, repository, path, content, json.dumps(embedding)))
        self.connection.commit()

    def search(self, query: list[float], query_text: str, limit: int = 8) -> list[dict[str, str | float]]:
        terms = set(re.findall(r"[a-z][a-z0-9_]+", query_text.lower()))
        matches = []
        for repository, path, content, raw_embedding in self.connection.execute("SELECT repository, path, content, embedding FROM code_chunks"):
            embedding = json.loads(raw_embedding)
            score = self._cosine(query, embedding) if query and embedding else 0.0
            score += min(0.25, sum(term in content.lower() for term in terms) * 0.02)
            matches.append({"repository": repository, "path": path, "content": content, "score": score})
        return sorted(matches, key=lambda item: float(item["score"]), reverse=True)[:limit]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        size = min(len(left), len(right))
        dot = sum(left[index] * right[index] for index in range(size))
        left_norm = math.sqrt(sum(value * value for value in left[:size]))
        right_norm = math.sqrt(sum(value * value for value in right[:size]))
        return dot / (left_norm * right_norm) if left_norm and right_norm else 0.0