from __future__ import annotations

from pathlib import Path
from typing import Any

from anthropic.types import ToolParam


async def _read_file(path: str, start_line: int = 1, end_line: int | None = None) -> str:
    try:
        p = Path(path).resolve()
        content = p.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        total = len(lines)
        end = end_line or total
        selected = lines[start_line - 1:end]
        numbered = "\n".join(
            f"{start_line + i:4d}\t{line}" for i, line in enumerate(selected)
        )
        return f"File: {p} (lines {start_line}-{end} of {total})\n\n{numbered}"
    except Exception as e:
        return f"Error reading file: {e}"


async def _write_file(path: str, content: str) -> str:
    try:
        if ".." in path:
            raise Exception("Invalid file path")
        p = Path(path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        lines = content.count("\n") + 1
        return f"Written {lines} lines to {p}"
    except Exception as e:
        return f"Error writing file: {e}"


async def _edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    try:
        if ".." in path:
            raise Exception("Invalid file path")
        p = Path(path).resolve()
        content = p.read_text(encoding="utf-8")
        count = content.count(old_string)
        if count == 0:
            return f"Error: string not found in {p}"
        if not replace_all and count > 1:
            return f"Error: {count} occurrences found. Use replace_all=true or add more context."
        new_content = content.replace(old_string, new_string) if replace_all else content.replace(old_string, new_string, 1)
        p.write_text(new_content, encoding="utf-8")
        return f"Replaced {count if replace_all else 1} occurrence(s) in {p}"
    except Exception as e:
        return f"Error editing file: {e}"


async def _list_files(path: str, include_hidden: bool = False) -> str:
    try:
        import glob as glob_module
        if "*" in path or "?" in path:
            matches = sorted(glob_module.glob(path, recursive=True))
            return "\n".join(matches) if matches else "No files matched"
        p = Path(path).resolve()
        if p.is_file():
            return str(p)
        entries = sorted(p.iterdir(), key=lambda e: (not e.is_dir(), e.name))
        if not include_hidden:
            entries = [e for e in entries if not e.name.startswith(".")]
        lines = [f"{'📁' if e.is_dir() else '📄'} {e.name}{'/' if e.is_dir() else ''}" for e in entries]
        return f"{p}/\n" + "\n".join(lines)
    except Exception as e:
        return f"Error listing files: {e}"


async def _delete_file(path: str) -> str:
    try:
        p = Path(path).resolve()
        if p.is_dir():
            p.rmdir()
        else:
            p.unlink()
        return f"Deleted: {p}"
    except Exception as e:
        return f"Error deleting: {e}"


TOOL_HANDLERS: dict[str, Any] = {
    "read_file": _read_file,
    "write_file": _write_file,
    "edit_file": _edit_file,
    "list_files": _list_files,
    "delete_file": _delete_file,
}

file_tools: list[ToolParam] = [
    {
        "name": "read_file",
        "description": "Read the contents of a file. Optionally specify line ranges.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "start_line": {"type": "integer", "description": "Start line (1-indexed, optional)"},
                "end_line": {"type": "integer", "description": "End line (1-indexed, optional)"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file, creating or overwriting it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to write to"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Perform targeted string replacement in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "old_string": {"type": "string", "description": "Exact string to replace"},
                "new_string": {"type": "string", "description": "Replacement string"},
                "replace_all": {"type": "boolean", "description": "Replace all occurrences"},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    {
        "name": "list_files",
        "description": "List files in a directory or matching a glob pattern.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path or glob pattern"},
                "include_hidden": {"type": "boolean", "description": "Include hidden files"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "delete_file",
        "description": "Delete a file or empty directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to delete"},
            },
            "required": ["path"],
        },
    },
]
