"""Single source of truth for the package version.

The version is declared once, in pyproject.toml, and read back from the
installed distribution metadata — nothing else in the package hardcodes it.
"""

from __future__ import annotations

from importlib import metadata

#: Reported when running from a source checkout that was never installed.
_FALLBACK = "0.0.0.dev0"


def get_version() -> str:
    try:
        return metadata.version("apex-pred-ai")
    except metadata.PackageNotFoundError:  # pragma: no cover - source checkout only
        return _FALLBACK


__version__ = get_version()
