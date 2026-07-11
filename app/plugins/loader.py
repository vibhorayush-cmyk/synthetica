from __future__ import annotations

import importlib
import logging
from pathlib import Path

from app.plugins.base import BaseIndustryPlugin


logger = logging.getLogger(__name__)


def discover_plugins() -> list[BaseIndustryPlugin]:
    """Discover plugin packages under the plugins package."""
    package_root = Path(__file__).resolve().parent
    plugins: list[BaseIndustryPlugin] = []
    for child in package_root.iterdir():
        if not child.is_dir() or child.name.startswith("_"):
            continue
        plugin_module_path = child / "plugin.py"
        if not plugin_module_path.exists():
            continue
        module_name = f"app.plugins.{child.name}.plugin"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            logger.exception("plugin_load_failed", extra={"plugin": child.name})
            raise
        for attr in vars(module).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseIndustryPlugin)
                and attr is not BaseIndustryPlugin
            ):
                plugins.append(attr())
                logger.info("plugin_loaded", extra={"plugin": child.name})
                break
    return plugins
