from __future__ import annotations

import asyncio
import contextlib
import sys
from importlib import metadata
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from typer.core import TyperGroup

from .agent import ApexPredAgent
from .config import ApexConfig, get_config, get_config_path, set_config
from .personality import APEX_PRED_BANNER, WELCOME_MESSAGE


def _tolerate_narrow_encodings() -> None:
    """Never crash on glyphs the active console encoding can't represent.

    Legacy Windows consoles report cp1252 stdout, and C-locale Unix reports
    ASCII; rich then dies with UnicodeEncodeError writing ✓/✗/⚡. Substituting
    "?" for the odd glyph beats a crash — UTF-8 terminals are unaffected
    because every glyph encodes and "replace" never fires.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            # Closed or exotic streams can refuse — leave those be
            with contextlib.suppress(ValueError, OSError):
                reconfigure(errors="replace")


_tolerate_narrow_encodings()


class ImplicitChatGroup(TyperGroup):
    """Routes anything that isn't a known command to `chat`.

    A variadic argument on the group callback would swallow subcommand names
    ("apex-pred config" parsed as the message "config"), so the one-shot
    message lives on its own command and unrecognized tokens are sent there.

    Typed loosely on purpose: Typer vendors its own copy of click in newer
    releases, so the concrete Context/Command classes here vary by version.
    """

    def resolve_command(
        self, ctx: Any, args: list[str]
    ) -> tuple[str | None, Any, list[str]]:
        # Leave options and real command names alone; everything else is a message
        if args and not args[0].startswith("-") and args[0] not in self.commands:
            chat_cmd = self.get_command(ctx, "chat")
            if chat_cmd is not None:
                # Hand the tokens over untouched — `chat` parses them as the message
                return "chat", chat_cmd, args
        return super().resolve_command(ctx, args)


app = typer.Typer(
    name="apex-pred",
    help="Apex-Pred AI — the apex predator of AI assistants",
    add_completion=False,
    rich_markup_mode="rich",
    cls=ImplicitChatGroup,
)

console = Console()

SLASH_COMMANDS = {
    "/help": "Show available commands",
    "/tools": "List available tools",
    "/config": "Show current config",
    "/clear": "Clear conversation history",
    "/session": "Show session info",
    "/exit": "Exit",
}


def print_banner() -> None:
    console.print(Text(APEX_PRED_BANNER, style="bold red"))
    console.print(Panel(WELCOME_MESSAGE, border_style="red", padding=(0, 2)))


def _package_version() -> str:
    try:
        return metadata.version("apex-pred-ai")
    except metadata.PackageNotFoundError:
        # Running straight from a source checkout
        from . import __version__

        return __version__


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"Apex-Pred AI v{_package_version()}")
        raise typer.Exit()


def _resolve_config(
    key: str | None,
    model: str | None,
    max_tokens: int | None,
    no_stream: bool,
    debug: bool,
    base: ApexConfig | None = None,
) -> ApexConfig:
    """Apply command-line overrides on top of the stored config."""
    cfg = base if base is not None else get_config()
    if key:
        cfg.api_key = key
    if model:
        cfg.model = model
    if max_tokens:
        cfg.max_tokens = max_tokens
    if no_stream:
        cfg.streaming_enabled = False
    if debug:
        cfg.debug = True
    return cfg


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    key: str | None = typer.Option(None, "--key", "-k", help="Anthropic API key"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model to use"),
    max_tokens: int | None = typer.Option(None, "--max-tokens", "-t", help="Max tokens"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Disable streaming"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Start Apex-Pred AI.

    Run bare for an interactive session, or pass a message for one-shot mode.
    """
    cfg = _resolve_config(key, model, max_tokens, no_stream, debug)
    # Hand the resolved config to whichever subcommand runs next
    ctx.obj = cfg

    if ctx.invoked_subcommand is not None:
        return

    asyncio.run(_interactive(cfg))


@app.command()
def chat(
    ctx: typer.Context,
    message: list[str] = typer.Argument(..., help="Message to send"),
    key: str | None = typer.Option(None, "--key", "-k", help="Anthropic API key"),
    model: str | None = typer.Option(None, "--model", "-m", help="Model to use"),
    max_tokens: int | None = typer.Option(None, "--max-tokens", "-t", help="Max tokens"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Disable streaming"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """Send one message and print the reply. Implied when you pass a bare message."""
    base = ctx.obj if isinstance(ctx.obj, ApexConfig) else None
    cfg = _resolve_config(key, model, max_tokens, no_stream, debug, base=base)
    asyncio.run(_one_shot(" ".join(message), cfg))


async def _one_shot(message: str, config: ApexConfig) -> None:
    agent = ApexPredAgent(config)
    if config.streaming_enabled:
        await agent.stream_chat(message)
    else:
        await agent.chat(message)


async def _interactive(config: ApexConfig) -> None:
    print_banner()
    agent = ApexPredAgent(config)

    while True:
        try:
            user_input = Prompt.ask(
                Text("\nYou → ", style="bold yellow"),
                console=console,
            ).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Apex-Pred out. Stay sharp.[/dim]")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            cmd = user_input.split()[0].lower()

            if cmd == "/help":
                console.print("\n[bold orange1]Slash Commands:[/bold orange1]")
                for c, desc in SLASH_COMMANDS.items():
                    console.print(f"  [red]{c:<12}[/red] [dim]{desc}[/dim]")
                console.print()

            elif cmd == "/tools":
                console.print("\n[bold orange1]Available Tools:[/bold orange1]")
                for tool in agent.list_tools():
                    console.print(f"  [red]⚡[/red] {tool}")
                console.print()

            elif cmd == "/config":
                console.print("\n[bold orange1]Current Config:[/bold orange1]")
                console.print(f"  Model:      [yellow]{config.effective_model()}[/yellow]")
                console.print(f"  Max Tokens: [yellow]{config.effective_max_tokens()}[/yellow]")
                console.print(f"  Streaming:  [yellow]{config.streaming_enabled}[/yellow]")
                console.print(f"  Debug:      [yellow]{config.debug}[/yellow]")
                api_status = "[green]✓ set[/green]" if config.effective_api_key() else "[red]✗ missing[/red]"
                console.print(f"  API Key:    {api_status}")
                console.print()

            elif cmd == "/clear":
                agent.clear_session()
                console.clear()
                print_banner()
                console.print("[green]Conversation cleared. Fresh start.[/green]\n")

            elif cmd == "/session":
                info = agent.get_session_info()
                console.print("\n[bold orange1]Session Info:[/bold orange1]")
                for k, v in info.items():
                    console.print(f"  {k}: [yellow]{v}[/yellow]")
                console.print()

            elif cmd in ("/exit", "/quit"):
                console.print("[dim]Apex-Pred out. Stay sharp.[/dim]")
                break

            else:
                console.print(f"[red]Unknown command: {cmd}[/red] — try /help")

            continue

        try:
            if config.streaming_enabled:
                await agent.stream_chat(user_input)
            else:
                await agent.chat(user_input)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def config(
    key: str | None = typer.Option(None, "--key", "-k", help="Set API key"),
    model: str | None = typer.Option(None, "--model", "-m", help="Set default model"),
    max_tokens: int | None = typer.Option(None, "--max-tokens", "-t", help="Set max tokens"),
    show: bool = typer.Option(False, "--show", help="Show current config"),
) -> None:
    """View or update Apex-Pred AI configuration."""
    cfg = get_config()

    if show or not any([key, model, max_tokens]):
        console.print("\n[bold red]Apex-Pred AI Configuration[/bold red]")
        console.print(f"[dim]Config file: {get_config_path()}[/dim]\n")
        api_status = "[green]✓ set[/green]" if cfg.effective_api_key() else "[red]✗ not set[/red]"
        console.print(f"  API Key:    {api_status}")
        console.print(f"  Model:      [yellow]{cfg.effective_model()}[/yellow]")
        console.print(f"  Max Tokens: [yellow]{cfg.effective_max_tokens()}[/yellow]")
        console.print(f"  Streaming:  [yellow]{cfg.streaming_enabled}[/yellow]")
        console.print(f"  Debug:      [yellow]{cfg.debug}[/yellow]")
        console.print()
        return

    updates: dict[str, object] = {}
    if key:
        updates["api_key"] = key
    if model:
        updates["model"] = model
    if max_tokens:
        updates["max_tokens"] = max_tokens

    set_config(updates)
    console.print("[green]✓ Configuration updated.[/green]")


if __name__ == "__main__":
    app()
