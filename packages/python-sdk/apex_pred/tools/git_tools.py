from __future__ import annotations

import asyncio
import os
import re
import shlex
from typing import Any

from anthropic.types import ToolParam

BLOCKED_GIT = [
    re.compile(r"\bpush\s+.*--force\b", re.IGNORECASE),
    re.compile(r"\bpush\s+-f\b", re.IGNORECASE),
    re.compile(r"\breset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bclean\s+-[a-z]*f", re.IGNORECASE),
    re.compile(r"\bbranch\s+-D\b", re.IGNORECASE),
]


async def _git(command: str, cwd: str | None = None) -> str:
    for pattern in BLOCKED_GIT:
        if pattern.search(command):
            return f'Blocked: "{command}" requires explicit user confirmation.'

    working_dir = cwd or os.getcwd()

    # Use shlex.split + create_subprocess_exec (no shell=True) to prevent injection
    try:
        args = shlex.split(command)
    except ValueError as e:
        return f"Invalid command syntax: {e}"

    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        # Decode stdout and stderr separately, then join — don't concatenate bytes
        parts = []
        if stdout.strip():
            parts.append(stdout.decode("utf-8", errors="replace").strip())
        if stderr.strip():
            parts.append(stderr.decode("utf-8", errors="replace").strip())
        return "\n".join(parts) or "(no output)"
    except asyncio.TimeoutError:
        return "git command timed out"
    except FileNotFoundError:
        return "git not found — is it installed and on PATH?"
    except Exception as e:
        return f"git error: {e}"


TOOL_HANDLERS: dict[str, Any] = {
    "git": _git,
}

git_tools: list[ToolParam] = [
    {
        "name": "git",
        "description": "Execute git commands. Provide the subcommand and args without the 'git' prefix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": 'Git command (e.g. "status", "log --oneline -10", "diff HEAD")',
                },
                "cwd": {"type": "string", "description": "Working directory (optional)"},
            },
            "required": ["command"],
        },
    }
]
