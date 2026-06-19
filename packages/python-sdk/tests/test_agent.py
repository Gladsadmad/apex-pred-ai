"""Tests for Apex-Pred AI agent and tools."""
from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from apex_pred.config import ApexConfig
from apex_pred.session import SessionManager
from apex_pred.tools.file_tools import _read_file, _write_file, _edit_file, _list_files
from apex_pred.tools.bash_tools import _bash
from apex_pred.tools.web_tools import _web_fetch


class TestSessionManager:
    def test_init(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionManager(tmpdir, "claude-sonnet-4-6")
            assert session.session_id.startswith("session_")
            assert session.messages == []
            assert session.total_tokens == 0

    def test_add_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionManager(tmpdir, "test-model")
            session.add_message({"role": "user", "content": "hello"})
            assert len(session.get_messages()) == 1

    def test_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionManager(tmpdir, "test-model")
            session.add_message({"role": "user", "content": "hello"})
            session.update_tokens(100)
            session.clear()
            assert session.messages == []
            assert session.total_tokens == 0

    def test_save_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session = SessionManager(tmpdir, "test-model")
            session.add_message({"role": "user", "content": "test"})
            session.save()
            sessions = SessionManager.list_sessions(tmpdir)
            assert session.session_id in sessions


class TestFileTools:
    @pytest.mark.asyncio
    async def test_write_and_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            result = await _write_file(path, "line1\nline2\nline3")
            assert "Written" in result

            result = await _read_file(path)
            assert "line1" in result
            assert "line2" in result

    @pytest.mark.asyncio
    async def test_read_with_line_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            await _write_file(path, "\n".join(f"line{i}" for i in range(1, 11)))
            result = await _read_file(path, start_line=3, end_line=5)
            assert "line3" in result
            assert "line5" in result
            assert "line1" not in result

    @pytest.mark.asyncio
    async def test_edit_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            await _write_file(path, "hello world")
            result = await _edit_file(path, "hello", "goodbye")
            assert "Replaced" in result
            read_result = await _read_file(path)
            assert "goodbye world" in read_result

    @pytest.mark.asyncio
    async def test_edit_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.txt")
            await _write_file(path, "hello world")
            result = await _edit_file(path, "nonexistent", "replacement")
            assert "Error" in result

    @pytest.mark.asyncio
    async def test_list_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file1.txt").write_text("a")
            (Path(tmpdir) / "file2.txt").write_text("b")
            result = await _list_files(tmpdir)
            assert "file1.txt" in result
            assert "file2.txt" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent(self) -> None:
        result = await _read_file("/nonexistent/path/file.txt")
        assert "Error" in result


class TestBashTools:
    @pytest.mark.asyncio
    async def test_echo(self) -> None:
        import platform
        if platform.system() == "Windows":
            result = await _bash("echo hello")
        else:
            result = await _bash("echo hello")
        assert "hello" in result.lower()

    @pytest.mark.asyncio
    async def test_timeout(self) -> None:
        import platform
        if platform.system() == "Windows":
            result = await _bash("Start-Sleep -Seconds 10", timeout_ms=500)
        else:
            result = await _bash("sleep 10", timeout_ms=500)
        assert "timed out" in result.lower()

    @pytest.mark.asyncio
    async def test_blocked_command(self) -> None:
        result = await _bash("rm -rf /")
        assert "Blocked" in result


class TestApexConfig:
    def test_defaults(self) -> None:
        config = ApexConfig()
        assert config.model == "claude-sonnet-4-6"
        assert config.max_tokens == 8096
        assert config.streaming_enabled is True
        assert config.debug is False

    def test_effective_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
        config = ApexConfig()
        assert config.effective_api_key() == "test-key-123"

    def test_effective_model_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APEX_MODEL", "claude-opus-4-8")
        config = ApexConfig()
        assert config.effective_model() == "claude-opus-4-8"
