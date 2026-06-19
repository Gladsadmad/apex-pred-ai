from __future__ import annotations

import asyncio
import os
import platform
import re
from typing import Any

from anthropic.types import ToolParam

BLOCKED_PATTERNS = [
    re.compile(r"rm\s+-rf\s+/(?!\S)"),
    re.compile(r"mkfs"),
    re.compile(r"dd\s+if=.*of=/dev"),
    re.compile(r":\(\)\s*\{"),
]


async def _bash(command: str, cwd: str | None = None, timeout_ms: int = 30000) -> str:
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(command):
            return f"Blocked: command matches dangerous pattern {pattern.pattern}"

    working_dir = cwd or os.getcwd()
    is_windows = platform.system() == "Windows"

    if is_windows:
        shell_cmd = ["powershell.exe", "-Command", command]
    else:
        shell_cmd = ["/bin/bash", "-c", command]

    try:
        proc = await asyncio.create_subprocess_exec(
            *shell_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_ms / 1000
        )
        parts = []
        if stdout.strip():
            parts.append(stdout.decode("utf-8", errors="replace").strip())
        if stderr.strip():
            parts.append(f"[stderr]\n{stderr.decode('utf-8', errors='replace').strip()}")
        return "\n".join(parts) if parts else "(no output)"
    except asyncio.TimeoutError:
        return f"Command timed out after {timeout_ms}ms"
    except Exception as e:
        return f"Execution error: {e}"


TOOL_HANDLERS: dict[str, Any] = {
    "bash": _bash,
}

bash_tools: list[ToolParam] = [
    {
        "name": "bash",
        "description": "Execute a shell command (PowerShell on Windows, bash on Unix). Use for running scripts, installing packages, building projects.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Command to execute"},
                "cwd": {"type": "string", "description": "Working directory (optional)"},
                "timeout_ms": {"type": "integer", "description": "Timeout in milliseconds (default: 30000)"},
            },
            "required": ["command"],
        },
    }
]
