"""Jinja2 Markdown and PDF rendering for challenge packs."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from app.challenges.base import ChallengePack


class ChallengePackRenderer:
    """Render one challenge pack into professional portable artifacts."""

    def __init__(self) -> None:
        templates_dir = Path(__file__).parent / "templates"
        self._templates = Environment(
            loader=FileSystemLoader(templates_dir),
            undefined=StrictUndefined,
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_markdown(self, pack: ChallengePack) -> str:
        """Render the complete challenge brief from its Jinja2 template."""
        return self._templates.get_template("challenge.md.j2").render(pack=pack)

    def render_requirements(self, pack: ChallengePack) -> str:
        """Render concise project requirements for a portfolio submission."""
        return "\n".join(
            [
                f"# {pack.title} — Requirements",
                "",
                "## Required Deliverables",
                *[f"- {item}" for item in pack.deliverables],
                "",
                "## Success Criteria",
                *[f"- {item}" for item in pack.success_criteria],
                "",
                "## Recommended Tools",
                *[f"- {item}" for item in pack.recommended_tools],
            ]
        )

    @staticmethod
    def render_dataset_overview(pack: ChallengePack) -> str:
        """Render dataset metadata and quality context for the learner."""
        row_counts = pack.dataset_metadata.get("row_counts", {})
        table_lines = (
            [f"- {name}: {count:,}" for name, count in row_counts.items()]
            if isinstance(row_counts, dict)
            else ["- Row-count metadata unavailable"]
        )
        quality_lines = [
            f"- {name.replace('_', ' ').title()}: {value:g}%"
            for name, value in pack.quality.items()
        ]
        return "\n".join(
            [
                "# Dataset Overview",
                "",
                "## Scenario",
                pack.scenario.replace("_", " ").title(),
                "",
                "## Table Counts",
                *table_lines,
                "",
                "## Data Quality Configuration",
                *(quality_lines or ["- No quality rules supplied"]),
            ]
        )

    def render_pdf(self, pack: ChallengePack, destination: Path) -> Path:
        """Create a professional PDF version of the challenge brief."""
        styles = getSampleStyleSheet()
        heading = ParagraphStyle(
            "ChallengeHeading",
            parent=styles["Heading2"],
            spaceBefore=12,
            spaceAfter=6,
        )
        body = ParagraphStyle(
            "ChallengeBody", parent=styles["BodyText"], leading=15, spaceAfter=5
        )
        story = [Paragraph(pack.title, styles["Title"]), Spacer(1, 0.15 * inch)]
        sections = [
            ("Business Story", [pack.business_story]),
            ("Business Problem", [pack.business_problem]),
            (
                "Difficulty and Time",
                [f"{pack.difficulty} · {pack.estimated_completion_time}"],
            ),
            ("KPIs", pack.kpis),
            ("Dashboard Requirements", pack.dashboard_requirements),
            ("SQL Questions", pack.sql_questions),
            ("Excel Tasks", pack.excel_questions),
            ("Python Tasks", pack.python_questions),
            ("Power BI Tasks", pack.powerbi_tasks),
            ("Tableau Tasks", pack.tableau_tasks),
            ("Machine Learning Ideas", pack.machine_learning_ideas),
            ("Deliverables", pack.deliverables),
            ("Success Criteria", pack.success_criteria),
        ]
        for title, items in sections:
            story.append(Paragraph(title, heading))
            for item in items:
                story.append(Paragraph(f"• {item}", body))
        story.append(PageBreak())
        story.append(Paragraph("Portfolio Guidance", styles["Heading2"]))
        story.append(
            Paragraph(
                "Document assumptions, show reproducible analysis, and communicate recommendations in executive-ready language.",
                body,
            )
        )
        SimpleDocTemplate(
            str(destination),
            pagesize=LETTER,
            leftMargin=0.7 * inch,
            rightMargin=0.7 * inch,
        ).build(story)
        return destination
