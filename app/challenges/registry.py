"""Challenge generator registration and resolution."""

from collections.abc import Iterable

from app.challenges.base import BaseChallengeGenerator


class ChallengeRegistry:
    """Resolve challenge generators without coupling callers to industries."""

    def __init__(self, generators: Iterable[BaseChallengeGenerator] = ()) -> None:
        self._generators: dict[str, BaseChallengeGenerator] = {}
        for generator in generators:
            self.register(generator)

    def register(self, generator: BaseChallengeGenerator) -> None:
        """Register a challenge generator by industry."""
        if generator.industry in self._generators:
            raise ValueError(
                f"challenge generator already registered: {generator.industry}"
            )
        self._generators[generator.industry] = generator

    def get(self, industry: str) -> BaseChallengeGenerator:
        """Return the generator for an industry."""
        try:
            return self._generators[industry]
        except KeyError as error:
            raise ValueError(
                f"no challenge generator registered for {industry}"
            ) from error
