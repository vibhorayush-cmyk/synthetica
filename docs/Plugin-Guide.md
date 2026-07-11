# Plugin Guide

Implement `BaseIndustryPlugin`, place the plugin in `app/plugins/<industry>/plugin.py`, and expose a concrete plugin class. The loader discovers packages at startup and logs successful or failed plugin loading.

Plugins own industry validation, baseline generation, scenario and quality application, challenge generation, and export handoff. Keep HTTP concerns in `app/api`.
