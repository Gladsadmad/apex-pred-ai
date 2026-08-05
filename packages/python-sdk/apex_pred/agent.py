from __future__ import annotations

import asyncio
import inspect
import sys
from typing import Any, cast

import anthropic
from anthropic.types import MessageParam
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from .config import ApexConfig
from .personality import APEX_PRED_SYSTEM_PROMPT
from .session import SessionManager
from .tools import ALL_TOOLS
from .tools.bash_tools import TOOL_HANDLERS as BASH_HANDLERS
from .tools.file_tools import TOOL_HANDLERS as FILE_HANDLERS
from .tools.git_tools import TOOL_HANDLERS as GIT_HANDLERS
from .tools.web_tools import TOOL_HANDLERS as WEB_HANDLERS

ALL_HANDLERS: dict[str, Any] = {
    **FILE_HANDLERS,
    **BASH_HANDLERS,
    **GIT_HANDLERS,
    **WEB_HANDLERS,
}

console = Console()


class ApexPredAgent:
    def __init__(self, config: ApexConfig) -> None:
        self.config = config
        api_key = config.effective_api_key()
        if not api_key:
            console.print(
                Panel(
                    "[red]No API key found.[/red]\nSet [yellow]ANTHROPIC_API_KEY[/yellow] env var or run: [cyan]apex-pred config --key YOUR_KEY[/cyan]",
                    title="[red]✗ Auth Error[/red]",
                    border_style="red",
                )
            )
            sys.exit(1)

        # Use only the async client — calling the sync client inside an async
        # function blocks the entire event loop for the duration of the API call
        self.async_client = anthropic.AsyncAnthropic(api_key=api_key)
        self.session = SessionManager(config.session_history_dir, config.effective_model())

    def _api_messages(self) -> list[MessageParam]:
        """Session history in the shape the Messages API expects.

        The session stores plain dicts so it can round-trip through JSON; the
        SDK's TypedDicts are structurally the same thing at runtime.
        """
        return cast("list[MessageParam]", self.session.get_messages())

    async def chat(self, user_message: str) -> None:
        self.session.add_message({"role": "user", "content": user_message})
        await self._run_agent_loop()
        self.session.save()

    async def _run_agent_loop(self) -> None:
        while True:
            with console.status("[red]Apex-Pred thinking...[/red]", spinner="dots"):
                try:
                    response = await self.async_client.messages.create(
                        model=self.config.effective_model(),
                        max_tokens=self.config.effective_max_tokens(),
                        system=APEX_PRED_SYSTEM_PROMPT,
                        messages=self._api_messages(),
                        tools=ALL_TOOLS,
                    )
                except anthropic.AuthenticationError:
                    console.print("[red]✗ Invalid API key.[/red]")
                    break
                except anthropic.RateLimitError:
                    console.print("[yellow]⚠ Rate limit hit. Chill for a sec.[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]✗ API error: {e}[/red]")
                    break

            self.session.update_tokens(response.usage.input_tokens + response.usage.output_tokens)

            # Serialize content blocks to plain dicts before storing — Pydantic
            # model objects (TextBlock, ToolUseBlock, etc.) are not JSON-serializable
            serialized_content = [b.model_dump() for b in response.content]
            self.session.add_message({"role": "assistant", "content": serialized_content})

            text_blocks = [b for b in response.content if b.type == "text"]
            tool_blocks = [b for b in response.content if b.type == "tool_use"]

            if text_blocks:
                full_text = "\n".join(b.text for b in text_blocks)
                console.print()
                console.print(Text("Apex-Pred: ", style="bold red"), end="")
                console.print(Markdown(full_text))

            if response.stop_reason == "end_turn" or not tool_blocks:
                break

            tool_results = await self._execute_tools(tool_blocks)
            self.session.add_message({"role": "user", "content": tool_results})

    async def stream_chat(self, user_message: str) -> None:
        self.session.add_message({"role": "user", "content": user_message})
        await self._run_streaming_loop()
        self.session.save()

    async def _run_streaming_loop(self) -> None:
        while True:
            console.print(Text("Apex-Pred: ", style="bold red"), end="")
            sys.stdout.flush()

            try:
                async with self.async_client.messages.stream(
                    model=self.config.effective_model(),
                    max_tokens=self.config.effective_max_tokens(),
                    system=APEX_PRED_SYSTEM_PROMPT,
                    messages=self._api_messages(),
                    tools=ALL_TOOLS,
                ) as stream:
                    async for text in stream.text_stream:
                        print(text, end="", flush=True)

                    final = await stream.get_final_message()

                print()
                self.session.update_tokens(final.usage.input_tokens + final.usage.output_tokens)

                # Serialize content blocks to plain dicts before storing
                serialized_content = [b.model_dump() for b in final.content]
                self.session.add_message({"role": "assistant", "content": serialized_content})

                tool_blocks = [b for b in final.content if b.type == "tool_use"]
                if final.stop_reason == "end_turn" or not tool_blocks:
                    break

                tool_results = await self._execute_tools(tool_blocks)
                self.session.add_message({"role": "user", "content": tool_results})

            except Exception as e:
                print()
                console.print(f"[red]✗ Stream error: {e}[/red]")
                break

    async def _execute_tools(self, tool_blocks: list[Any]) -> list[dict[str, Any]]:
        results = []
        for block in tool_blocks:
            console.print(f"\n[orange1]⚡ {block.name}[/orange1]")
            handler = ALL_HANDLERS.get(block.name)

            if not handler:
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Unknown tool: {block.name}",
                    "is_error": True,
                })
                continue

            try:
                kwargs = dict(block.input)
                if inspect.iscoroutinefunction(handler):
                    result = await handler(**kwargs)
                else:
                    result = await asyncio.to_thread(handler, **kwargs)

                if self.config.debug:
                    preview = str(result)[:200]
                    console.print(f"  [dim]→ {preview}{'...' if len(str(result)) > 200 else ''}[/dim]")

                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })
            except Exception as e:
                err_msg = f"Tool error: {e}"
                console.print(f"  [red]✗ {err_msg}[/red]")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": err_msg,
                    "is_error": True,
                })

        return results

    def clear_session(self) -> None:
        self.session.clear()

    def get_session_info(self) -> dict[str, Any]:
        return self.session.get_info()

    def list_tools(self) -> list[str]:
        return [t["name"] for t in ALL_TOOLS]
