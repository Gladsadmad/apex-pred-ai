"""Apex-Pred AI — the apex predator of AI assistants."""

from .agent import ApexPredAgent
from .config import ApexConfig, get_config, set_config
from .personality import APEX_PRED_SYSTEM_PROMPT

__version__ = "1.0.0"
__all__ = ["ApexPredAgent", "ApexConfig", "get_config", "set_config", "APEX_PRED_SYSTEM_PROMPT"]
