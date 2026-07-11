"""Industry-agnostic challenge pack contract."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ChallengePack:
    """Professional analytics case study and portfolio brief."""

    title: str
    business_story: str
    business_problem: str
    difficulty: str
    recommended_tools: list[str]
    dashboard_requirements: list[str]
    sql_questions: list[str]
    excel_questions: list[str]
    python_questions: list[str]
    powerbi_tasks: list[str]
    tableau_tasks: list[str]
    kpis: list[str]
    deliverables: list[str]
    success_criteria: list[str]
    estimated_completion_time: str
    machine_learning_ideas: list[str]
    dataset_metadata: Mapping[str, object]
    scenario: str
    quality: Mapping[str, float]


class BaseChallengeGenerator(ABC):
    """Generate an industry-specific learning pack from dataset metadata."""

    industry: str

    @abstractmethod
    def generate(
        self,
        dataset_metadata: Mapping[str, object],
        scenario: str,
        quality: Mapping[str, float],
    ) -> ChallengePack:
        """Return a complete case study adapted to the generated dataset."""
