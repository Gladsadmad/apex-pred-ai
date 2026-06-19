from __future__ import annotations

import asyncio
import os
from typing import Any

from anthropic.types import ToolParam

BLOCKED_GIT_COMMANDS = ["push --force", "reset --hard", "clean -f", "branch -D"]


async def _git(command: str, cwd: str | None = None) -> str:
    for blocked in BLOCKED_GIT_COMMANDS:
        if blocked in command:
            return f'Blocked: "{blocked}" requires explicit user confirmation.'

    working_dir = cwd or os.getcwd()
    try:
        proc = await asyncio.create_subprocess_shell(
            f"git {command}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        result = (stdout + stderr).decode("utf-8", errors="replace").strip()
        return result or "(no output)"
    except asyncio.TimeoutError:
        return "git command timed out"
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
