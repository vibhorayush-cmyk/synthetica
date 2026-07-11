"""Backward-compatible configuration exports.

New application code should inject ``Settings`` from ``app.core.settings``.
"""

from app.core.settings import BASE_DIR, get_settings


settings = get_settings()
DOWNLOADS_DIR = BASE_DIR / "downloads"
EXPORTS_DIR = settings.export_dir
API_PREFIX = settings.api_v1_prefix
