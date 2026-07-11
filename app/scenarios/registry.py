"""Scenario registration and resolution."""

from collections.abc import Iterable

from app.scenarios.base import BaseScenario


class ScenarioRegistry:
    """Resolve named scenarios without coupling callers to implementations."""

    def __init__(self, scenarios: Iterable[BaseScenario] = ()) -> None:
        self._scenarios: dict[str, BaseScenario] = {}
        for scenario in scenarios:
            self.register(scenario)

    def register(self, scenario: BaseScenario) -> None:
        """Register a scenario under its unique name."""
        if not scenario.name:
            raise ValueError("scenario name cannot be empty")
        if scenario.name in self._scenarios:
            raise ValueError(f"scenario already registered: {scenario.name}")
        self._scenarios[scenario.name] = scenario

    def get(self, name: str) -> BaseScenario:
        """Return a registered scenario or explain which names are available."""
        try:
            return self._scenarios[name]
        except KeyError as error:
            available = ", ".join(sorted(self._scenarios))
            raise ValueError(
                f"unsupported scenario '{name}'. Available scenarios: {available}"
            ) from error

    @property
    def names(self) -> tuple[str, ...]:
        """Return registered scenario names in deterministic order."""
        return tuple(sorted(self._scenarios))
