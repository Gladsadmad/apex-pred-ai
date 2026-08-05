# apex-pred-ai

> The apex predator of AI assistants. A Claude Code-style terminal AI with personality, tools, and absolutely no corporate bullshit.

[![PyPI version](https://img.shields.io/pypi/v/apex-pred-ai.svg)](https://pypi.org/project/apex-pred-ai/)
[![Python versions](https://img.shields.io/pypi/pyversions/apex-pred-ai.svg)](https://pypi.org/project/apex-pred-ai/)
[![CI](https://github.com/Gladsadmad/apex-pred-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Gladsadmad/apex-pred-ai/actions/workflows/ci.yml)

Apex-Pred AI is a terminal-based coding assistant powered by Claude. It reads and edits your files, runs shell commands and git operations, searches the web, and tells you the truth about your code.

This is the Python SDK and CLI. A [TypeScript CLI](https://www.npmjs.com/package/@apex-pred/cli) with the same tools is also available.

---

## Install

```bash
pip install apex-pred-ai
```

Requires Python >= 3.10.

## Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or persist it
apex-pred config --key sk-ant-...
```

Grab a key at [console.anthropic.com](https://console.anthropic.com).

## Use it

```bash
# Interactive REPL
apex-pred

# One-shot
apex-pred "explain this stack trace"

# Pick a model
apex-pred --model claude-opus-4-8 "architect a job queue for me"

# Skip streaming
apex-pred --no-stream "summarize this repo"
```

---

## Use as a library

```python
import asyncio

from apex_pred import ApexPredAgent, get_config

agent = ApexPredAgent(get_config())
asyncio.run(agent.stream_chat("what's wrong with this regex?"))
```

The public API is `ApexPredAgent`, `ApexConfig`, `get_config`, `set_config`, and
`APEX_PRED_SYSTEM_PROMPT`. The agent is fully async and streams by default.

```python
from apex_pred import ApexConfig, ApexPredAgent

config = ApexConfig(model="claude-opus-4-8", max_tokens=16384, streaming_enabled=False)
agent = ApexPredAgent(config)

await agent.chat("refactor this module")
print(agent.get_session_info())   # {'id': ..., 'message_count': ..., 'tokens_used': ...}
agent.clear_session()
```

---

## Tools

| Tool | Description |
|------|-------------|
| `read_file` | Read file contents with optional line ranges |
| `write_file` | Create or overwrite files |
| `edit_file` | Surgical string replacement in files |
| `list_files` | List directory contents or glob patterns |
| `delete_file` | Delete files or empty directories |
| `bash` | Execute shell commands (PowerShell on Windows) |
| `git` | Run git operations |
| `web_fetch` | Fetch and parse URL content |
| `web_search` | Search DuckDuckGo |

## Slash commands

```
/help     — show all commands
/tools    — list available tools
/config   — view current configuration
/clear    — clear conversation history
/session  — show session info (tokens used, message count)
/exit     — quit
```

## CLI reference

```
apex-pred [MESSAGE...]         Start interactive mode, or send a one-shot message

  -k, --key TEXT               Anthropic API key
  -m, --model TEXT             Model to use (default: claude-sonnet-4-6)
  -t, --max-tokens INTEGER     Max tokens per response
      --no-stream              Disable streaming
      --debug                  Enable debug logging

apex-pred config               View or update configuration

  -k, --key TEXT               Set API key
  -m, --model TEXT             Set default model
  -t, --max-tokens INTEGER     Set max tokens
      --show                   Show current config
```

## Configuration

### Environment variables

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required
APEX_MODEL=claude-sonnet-4-6    # Optional: model override
APEX_MAX_TOKENS=8096            # Optional: max tokens
APEX_DEBUG=false                # Optional: debug logging
```

A `.env` file in the working directory is loaded automatically. Persistent config
lives in a platform-specific directory — run `apex-pred config --show` to see where.

---

## Development

```bash
git clone https://github.com/Gladsadmad/apex-pred-ai.git
cd apex-pred-ai/packages/python-sdk

pip install -e ".[dev]"

ruff check apex_pred/ tests/
mypy apex_pred/
pytest tests/ -v
```

---

## Links

- [Repository](https://github.com/Gladsadmad/apex-pred-ai)
- [Issues](https://github.com/Gladsadmad/apex-pred-ai/issues)
- [Changelog](https://github.com/Gladsadmad/apex-pred-ai/blob/master/CHANGELOG.md)

## License

MIT — do whatever you want with it.

*Built with Claude by Anthropic. Apex-Pred is not affiliated with Anthropic.*
