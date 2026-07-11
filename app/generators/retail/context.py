"""Shared random-data dependencies for retail table generators."""

from dataclasses import dataclass

import numpy as np
from faker import Faker


@dataclass(slots=True)
class GenerationContext:
    """Provide seeded Faker and NumPy instances to table generators."""

    faker: Faker
    random: np.random.Generator

    @classmethod
    def create(cls, seed: int | None = None) -> "GenerationContext":
        """Create a context, optionally making generated data repeatable."""
        faker = Faker()
        faker.seed_instance(seed)
        return cls(faker=faker, random=np.random.default_rng(seed))
