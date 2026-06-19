from __future__ import annotations

import json
import random
import string
import time
from pathlib import Path
from typing import Any


class SessionManager:
    def __init__(self, history_dir: str, model: str) -> None:
        self.history_dir = Path(history_dir)
        self.session_id = self._generate_id()
        self.messages: list[dict[str, Any]] = []
        self.total_tokens = 0
        self.model = model

    def _generate_id(self) -> str:
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"session_{int(time.time())}_{suffix}"

    def add_message(self, message: dict[str, Any]) -> None:
        self.messages.append(message)

    def get_messages(self) -> list[dict[str, Any]]:
        return self.messages

    def clear(self) -> None:
        self.messages = []
        self.total_tokens = 0

    def update_tokens(self, tokens: int) -> None:
        self.total_tokens += tokens

    def get_info(self) -> dict[str, Any]:
        return {
            "id": self.session_id,
            "message_count": len(self.messages),
            "tokens_used": self.total_tokens,
            "model": self.model,
        }

    def save(self) -> None:
        try:
            self.history_dir.mkdir(parents=True, exist_ok=True)
            path = self.history_dir / f"{self.session_id}.json"
            data = {
                "id": self.session_id,
                "model": self.model,
                "messages": self.messages,
                "total_tokens": self.total_tokens,
            }
            path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    @classmethod
    def list_sessions(cls, history_dir: str) -> list[str]:
        try:
            return [p.stem for p in Path(history_dir).glob("*.json")]
        except Exception:
            return []
