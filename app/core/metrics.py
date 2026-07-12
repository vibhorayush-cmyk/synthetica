"""In-process operational metrics for health monitoring."""

from dataclasses import dataclass, field
from threading import Lock


@dataclass(slots=True)
class GenerationMetrics:
    """Thread-safe aggregate generation and export statistics."""

    generation_count: int = 0
    generation_failures: int = 0
    generation_timeouts: int = 0
    generation_duration_ms: float = 0
    export_duration_ms: float = 0
    peak_memory_bytes: int = 0
    expired_exports_removed: int = 0
    capacity_exports_removed: int = 0
    export_storage_bytes: int = 0
    _lock: Lock = field(default_factory=Lock)

    def record_success(
        self, generation_ms: float, export_ms: float, peak_memory_bytes: int
    ) -> None:
        """Record a completed generation operation."""
        with self._lock:
            self.generation_count += 1
            self.generation_duration_ms += generation_ms
            self.export_duration_ms += export_ms
            self.peak_memory_bytes = max(self.peak_memory_bytes, peak_memory_bytes)

    def record_failure(self) -> None:
        """Record a failed generation operation."""
        with self._lock:
            self.generation_failures += 1

    def record_timeout(self) -> None:
        """Record an API request that exceeded its configured time budget."""
        with self._lock:
            self.generation_timeouts += 1

    def record_storage_maintenance(
        self,
        expired_entries_removed: int,
        capacity_entries_removed: int,
        usage_bytes: int,
    ) -> None:
        """Record aggregate storage state without exposing customer data or paths."""
        with self._lock:
            self.expired_exports_removed += expired_entries_removed
            self.capacity_exports_removed += capacity_entries_removed
            self.export_storage_bytes = usage_bytes

    def snapshot(self) -> dict[str, float | int]:
        """Return a serializable metrics snapshot."""
        with self._lock:
            average_generation_ms = (
                self.generation_duration_ms / self.generation_count
                if self.generation_count
                else 0
            )
            return {
                "generation_count": self.generation_count,
                "generation_failures": self.generation_failures,
                "generation_timeouts": self.generation_timeouts,
                "average_generation_duration_ms": round(average_generation_ms, 2),
                "total_export_duration_ms": round(self.export_duration_ms, 2),
                "peak_memory_bytes": self.peak_memory_bytes,
                "expired_exports_removed": self.expired_exports_removed,
                "capacity_exports_removed": self.capacity_exports_removed,
                "export_storage_bytes": self.export_storage_bytes,
            }


metrics = GenerationMetrics()
