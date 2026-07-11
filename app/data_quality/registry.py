"""Data quality rule registration and resolution."""

from collections.abc import Iterable

from app.data_quality.base import BaseQualityRule


class QualityRegistry:
    """Register reusable quality rules by a stable public name."""

    def __init__(self, rules: Iterable[BaseQualityRule] = ()) -> None:
        self._rules: dict[str, BaseQualityRule] = {}
        for rule in rules:
            self.register(rule)

    def register(self, rule: BaseQualityRule) -> None:
        """Register a uniquely named quality rule."""
        if not rule.name:
            raise ValueError("quality rule name cannot be empty")
        if rule.name in self._rules:
            raise ValueError(f"quality rule already registered: {rule.name}")
        self._rules[rule.name] = rule

    def get(self, name: str) -> BaseQualityRule:
        """Return a registered rule or raise a descriptive validation error."""
        try:
            return self._rules[name]
        except KeyError as error:
            available = ", ".join(sorted(self._rules))
            raise ValueError(
                f"unsupported quality rule '{name}'. Available rules: {available}"
            ) from error

    @property
    def names(self) -> tuple[str, ...]:
        """Return all registered names in deterministic order."""
        return tuple(sorted(self._rules))
