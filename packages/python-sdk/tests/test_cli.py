"""Tests for Apex-Pred AI command dispatch.

The one-shot message argument used to live on the group callback, where it
swallowed subcommand names — `apex-pred config` was parsed as the message
"config" and the config command was unreachable. These pin the routing.
"""
from __future__ import annotations

import os
import site
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from apex_pred.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep every test off the real user config file."""
    config_dir = tmp_path / "config"
    monkeypatch.setattr("apex_pred.config.CONFIG_DIR", config_dir)
    monkeypatch.setattr("apex_pred.config.CONFIG_FILE", config_dir / "config.json")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("APEX_API_KEY", raising=False)


class TestCommandDispatch:
    def test_config_show_reaches_config_command(self) -> None:
        result = runner.invoke(app, ["config", "--show"])
        assert result.exit_code == 0
        assert "Apex-Pred AI Configuration" in result.stdout

    def test_bare_config_reaches_config_command(self) -> None:
        # No flags: `config` alone must still hit the command, not become a message
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Apex-Pred AI Configuration" in result.stdout

    def test_config_key_persists(self) -> None:
        result = runner.invoke(app, ["config", "--key", "sk-ant-test"])
        assert result.exit_code == 0
        assert "Configuration updated" in result.stdout

        show = runner.invoke(app, ["config", "--show"])
        assert "✓ set" in show.stdout

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "Apex-Pred AI v" in result.stdout

    def test_bare_message_routes_to_chat(self) -> None:
        with patch("apex_pred.cli._one_shot") as one_shot:
            result = runner.invoke(app, ["explain", "this", "stack", "trace"])
        assert result.exit_code == 0, result.stdout
        one_shot.assert_called_once()
        assert one_shot.call_args.args[0] == "explain this stack trace"

    def test_explicit_chat_command_routes_to_chat(self) -> None:
        with patch("apex_pred.cli._one_shot") as one_shot:
            result = runner.invoke(app, ["chat", "hello there"])
        assert result.exit_code == 0, result.stdout
        one_shot.assert_called_once()
        assert one_shot.call_args.args[0] == "hello there"

    def test_bare_invocation_starts_interactive(self) -> None:
        with patch("apex_pred.cli._interactive") as interactive:
            result = runner.invoke(app, [])
        assert result.exit_code == 0, result.stdout
        interactive.assert_called_once()

    def test_unknown_option_still_errors(self) -> None:
        result = runner.invoke(app, ["--definitely-not-a-flag"])
        assert result.exit_code != 0


class TestNarrowEncodings:
    def test_config_show_survives_cp1252_stdout(self, tmp_path: Path) -> None:
        """Legacy Windows consoles report cp1252; ✓/✗ used to raise UnicodeEncodeError.

        Forcing the encoding via PYTHONIOENCODING reproduces the Windows CI
        failure on every platform.
        """
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        # Keep the subprocess off the real user config dir on every OS
        env["HOME"] = str(tmp_path)
        env["XDG_CONFIG_HOME"] = str(tmp_path)
        env["APPDATA"] = str(tmp_path)
        env["LOCALAPPDATA"] = str(tmp_path)
        # Redirecting HOME hides pip's user-site (~/.local); keep deps importable
        user_site = site.getusersitepackages()
        if user_site:
            prev = env.get("PYTHONPATH")
            env["PYTHONPATH"] = user_site + (os.pathsep + prev if prev else "")

        result = subprocess.run(
            [sys.executable, "-m", "apex_pred.cli", "config", "--show"],
            capture_output=True,
            env=env,
            timeout=60,
        )
        stdout = result.stdout.decode("cp1252", errors="replace")
        assert result.returncode == 0, result.stderr.decode("cp1252", errors="replace")
        assert "Apex-Pred AI Configuration" in stdout


class TestOptionOverrides:
    def test_model_override_reaches_chat(self) -> None:
        with patch("apex_pred.cli._one_shot") as one_shot:
            result = runner.invoke(app, ["--model", "claude-opus-4-8", "hey"])
        assert result.exit_code == 0, result.stdout
        config = one_shot.call_args.args[1]
        assert config.model == "claude-opus-4-8"

    def test_trailing_options_reach_chat(self) -> None:
        # Options after the message are parsed by `chat` itself
        with patch("apex_pred.cli._one_shot") as one_shot:
            result = runner.invoke(app, ["hey", "--no-stream", "--debug"])
        assert result.exit_code == 0, result.stdout
        config = one_shot.call_args.args[1]
        assert config.streaming_enabled is False
        assert config.debug is True
