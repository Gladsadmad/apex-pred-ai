"""Apex-Pred AI — the apex predator of AI assistants."""

from ._version import __version__
from .agent import ApexPredAgent
from .config import ApexConfig, get_config, set_config
from .personality import APEX_PRED_SYSTEM_PROMPT

__all__ = [
    "APEX_PRED_SYSTEM_PROMPT",
    "ApexConfig",
    "ApexPredAgent",
    "__version__",
    "get_config",
    "set_config",
]
