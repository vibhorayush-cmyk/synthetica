"""Bounded local export-storage management."""

from dataclasses import dataclass
from pathlib import Path
import shutil
from time import time


class ExportStorageLimitError(RuntimeError):
    """Raised when an export cannot fit within configured local storage."""


@dataclass(frozen=True, slots=True)
class StorageMaintenance:
    """Safe aggregate result of export-storage maintenance."""

    expired_entries_removed: int
    capacity_entries_removed: int
    usage_bytes: int


class ExportStorageManager:
    """Remove expired exports and bound disk use without exposing file names."""

    def __init__(self, root: Path, ttl_hours: int, max_storage_mb: int) -> None:
        self._root = root
        self._ttl_seconds = ttl_hours * 3_600
        self._max_bytes = max_storage_mb * 1024 * 1024

    def maintain(self, protected_paths: set[Path] | None = None) -> StorageMaintenance:
        """Apply TTL cleanup and capacity cleanup, preserving active paths."""
        self._root.mkdir(parents=True, exist_ok=True)
        protected = {path.resolve() for path in protected_paths or set()}
        expired_removed = self.cleanup_expired()
        capacity_removed = 0
        while self.usage_bytes() > self._max_bytes:
            candidate = self._oldest_unprotected(protected)
            if candidate is None:
                raise ExportStorageLimitError(
                    "Export storage is full. Try again after older exports expire."
                )
            self._remove(candidate)
            capacity_removed += 1
        return StorageMaintenance(
            expired_entries_removed=expired_removed,
            capacity_entries_removed=capacity_removed,
            usage_bytes=self.usage_bytes(),
        )

    def cleanup_expired(self) -> int:
        """Delete top-level export entries older than the configured TTL."""
        self._root.mkdir(parents=True, exist_ok=True)
        cutoff = time() - self._ttl_seconds
        removed = 0
        for candidate in self._entries():
            if candidate.stat().st_mtime < cutoff:
                self._remove(candidate)
                removed += 1
        return removed

    def usage_bytes(self) -> int:
        """Return aggregate bytes beneath the export root without file details."""
        if not self._root.exists():
            return 0
        return sum(
            path.stat().st_size
            for path in self._root.rglob("*")
            if path.is_file() and not path.is_symlink()
        )

    def remove_paths(self, paths: set[Path]) -> None:
        """Remove partially written export paths after a capacity failure."""
        for path in paths:
            if path.exists() and path.resolve().parent == self._root.resolve():
                self._remove(path)

    def _entries(self) -> list[Path]:
        return [
            path
            for path in self._root.iterdir()
            if not path.is_symlink() and path.resolve().parent == self._root.resolve()
        ]

    def _oldest_unprotected(self, protected: set[Path]) -> Path | None:
        candidates = [path for path in self._entries() if path.resolve() not in protected]
        return min(candidates, key=lambda path: path.stat().st_mtime, default=None)

    @staticmethod
    def _remove(path: Path) -> None:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)
