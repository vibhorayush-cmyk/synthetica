"""JSON-backed repository for generation history."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.config import BASE_DIR
from app.history.models import HistoryEntry


class HistoryRepository(Protocol):
    def list(self) -> list[HistoryEntry]: ...

    def get(self, entry_id: str) -> HistoryEntry: ...

    def create(self, entry: HistoryEntry) -> HistoryEntry: ...

    def delete(self, entry_id: str) -> None: ...

    def delete_all(self) -> None: ...


class JsonHistoryRepository:
    """Store history metadata as JSON files in a directory."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._storage_dir = storage_dir or BASE_DIR / "history"
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[HistoryEntry]:
        entries = []
        for file_path in sorted(self._storage_dir.glob("*.json")):
            entries.append(self._load(file_path))
        return sorted(entries, key=lambda item: item.generated_at, reverse=True)

    def get(self, entry_id: str) -> HistoryEntry:
        file_path = self._storage_dir / f"{entry_id}.json"
        if not file_path.exists():
            raise ValueError(f"history entry not found: {entry_id}")
        return self._load(file_path)

    def create(self, entry: HistoryEntry) -> HistoryEntry:
        self._save(entry)
        return entry

    def delete(self, entry_id: str) -> None:
        file_path = self._storage_dir / f"{entry_id}.json"
        if file_path.exists():
            file_path.unlink()

    def delete_all(self) -> None:
        for file_path in self._storage_dir.glob("*.json"):
            file_path.unlink()

    def _save(self, entry: HistoryEntry) -> None:
        file_path = self._storage_dir / f"{entry.id}.json"
        file_path.write_text(json.dumps(entry.to_payload(), indent=2), encoding="utf-8")

    def _load(self, file_path: Path) -> HistoryEntry:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return HistoryEntry(**payload)


def build_history_id() -> str:
    return uuid4().hex
