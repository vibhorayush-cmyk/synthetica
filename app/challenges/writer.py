"""Challenge pack artifact writer."""

from pathlib import Path

from app.challenges.base import ChallengePack
from app.challenges.renderer import ChallengePackRenderer


class ChallengePackWriter:
    """Write all learning-pack files required in an exported bundle."""

    def __init__(self, renderer: ChallengePackRenderer | None = None) -> None:
        self._renderer = renderer or ChallengePackRenderer()

    def write(self, pack: ChallengePack, destination: Path) -> list[Path]:
        """Write Markdown, PDF, requirements, and dataset overview artifacts."""
        challenge_path = destination / "challenge.md"
        requirements_path = destination / "requirements.md"
        overview_path = destination / "dataset_overview.md"
        pdf_path = destination / "challenge.pdf"
        challenge_path.write_text(
            self._renderer.render_markdown(pack), encoding="utf-8"
        )
        requirements_path.write_text(
            self._renderer.render_requirements(pack), encoding="utf-8"
        )
        overview_path.write_text(
            self._renderer.render_dataset_overview(pack), encoding="utf-8"
        )
        self._renderer.render_pdf(pack, pdf_path)
        return [challenge_path, pdf_path, requirements_path, overview_path]
