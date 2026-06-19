from __future__ import annotations

import asyncio
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from .agent import ApexPredAgent
from .config import get_config, set_config, get_config_path, ApexConfig
from .personality import APEX_PRED_BANNER, WELCOME_MESSAGE

app = typer.Typer(
    name="apex-pred",
    help="Apex-Pred AI — the apex predator of AI assistants",
    add_completion=False,
    rich_markup_mode="rich",
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


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    message: Optional[list[str]] = typer.Argument(None, help="One-shot message to send"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Anthropic API key"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", "-t", help="Max tokens"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Disable streaming"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
) -> None:
    """Start Apex-Pred AI. Provide a message for one-shot mode, or run interactively."""
    if ctx.invoked_subcommand is not None:
        return

    cfg = get_config()
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

    if message:
        asyncio.run(_one_shot(" ".join(message), cfg))
    else:
        asyncio.run(_interactive(cfg))


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
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Set API key"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Set default model"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", "-t", help="Set max tokens"),
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
