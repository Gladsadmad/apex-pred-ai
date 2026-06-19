from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from platformdirs import user_config_dir

load_dotenv()

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(user_config_dir("apex-pred-ai"))
CONFIG_FILE = CONFIG_DIR / "config.json"

_VALID_FIELDS = {
    "api_key", "model", "max_tokens", "debug",
    "streaming_enabled", "session_history_dir", "theme", "swearing_level",
}


@dataclass
class ApexConfig:
    api_key: str | None = None
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 8096
    debug: bool = False
    streaming_enabled: bool = True
    session_history_dir: str = field(
        default_factory=lambda: str(Path.home() / ".apex-pred" / "sessions")
    )
    theme: Literal["dark", "light"] = "dark"
    swearing_level: Literal["mild", "moderate", "full"] = "full"

    def effective_api_key(self) -> str | None:
        return (
            os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("APEX_API_KEY")
            or self.api_key
        )

    def effective_model(self) -> str:
        return os.environ.get("APEX_MODEL", self.model)

    def effective_max_tokens(self) -> int:
        env_val = os.environ.get("APEX_MAX_TOKENS")
        if env_val:
            try:
                parsed = int(env_val)
                if parsed > 0:
                    return parsed
            except ValueError:
                logger.warning("APEX_MAX_TOKENS=%r is not a valid integer; using config value", env_val)
        return self.max_tokens


def get_config() -> ApexConfig:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            # Only pass known fields; ignore unknown or wrongly-typed values
            # rather than crashing with TypeError on unexpected data
            known = {k: v for k, v in raw.items() if k in _VALID_FIELDS}
            return ApexConfig(**known)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Config file is corrupt (%s); falling back to defaults", e)
    return ApexConfig()


def set_config(updates: dict) -> None:
    config = get_config()
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2), encoding="utf-8")


def get_config_path() -> str:
    return str(CONFIG_FILE)
