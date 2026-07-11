"""Retail analytics challenge generators."""

from app.challenges.registry import ChallengeRegistry
from app.challenges.retail.executive_dashboard import (
    ExecutiveDashboardChallengeGenerator,
)


def create_retail_challenge_registry() -> ChallengeRegistry:
    """Create the registry for available retail learning packs."""
    return ChallengeRegistry([ExecutiveDashboardChallengeGenerator()])


__all__ = ["create_retail_challenge_registry"]
