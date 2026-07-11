"""Retail business-event scenarios."""

from app.scenarios.registry import ScenarioRegistry
from app.scenarios.retail.black_friday import BlackFridayScenario
from app.scenarios.retail.christmas import ChristmasScenario
from app.scenarios.retail.no_scenario import NoScenario
from app.scenarios.retail.recession import RecessionScenario
from app.scenarios.retail.summer_sale import SummerSaleScenario


def create_retail_scenario_registry() -> ScenarioRegistry:
    """Create the default registry for retail scenario names."""
    return ScenarioRegistry(
        [
            NoScenario(),
            BlackFridayScenario(),
            ChristmasScenario(),
            SummerSaleScenario(),
            RecessionScenario(),
        ]
    )


__all__ = ["create_retail_scenario_registry"]
