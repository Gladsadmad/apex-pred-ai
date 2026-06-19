from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from platformdirs import user_config_dir

load_dotenv()

CONFIG_DIR = Path(user_config_dir("apex-pred-ai"))
CONFIG_FILE = CONFIG_DIR / "config.json"


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
        return int(env_val) if env_val else self.max_tokens


def get_config() -> ApexConfig:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return ApexConfig(**{k: v for k, v in data.items() if k in ApexConfig.__dataclass_fields__})
        except Exception:
            pass
    return ApexConfig()


def set_config(updates: dict) -> None:
    config = get_config()
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(config), indent=2))


def get_config_path() -> str:
    return str(CONFIG_FILE)
