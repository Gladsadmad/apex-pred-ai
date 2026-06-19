# Apex-Pred AI

> The apex predator of AI assistants. A Claude Code-style terminal AI with personality, tools, and absolutely no corporate bullshit.

[![CI](https://github.com/YOUR_USERNAME/apex-pred-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/apex-pred-ai/actions/workflows/ci.yml)
[![npm version](https://badge.fury.io/js/%40apex-pred%2Fcli.svg)](https://badge.fury.io/js/%40apex-pred%2Fcli)
[![PyPI version](https://badge.fury.io/py/apex-pred-ai.svg)](https://badge.fury.io/py/apex-pred-ai)

---

## What is Apex-Pred?

Apex-Pred AI is a terminal-based AI coding assistant powered by Claude. It's built like Claude Code but with a distinct personality: sharp wit, brutal honesty, and zero tolerance for unnecessary complexity. It swears when appropriate, roasts bad code, and gets genuinely excited about elegant solutions.

It helps you:
- Write, debug, and refactor code
- Read, edit, and write files
- Execute shell commands
- Run git operations
- Search the web
- And basically anything else a great developer would help with

Available as both a **TypeScript CLI** and a **Python SDK**.

---

## Quick Start

### TypeScript CLI (Recommended)

```bash
# Install globally
npm install -g @apex-pred/cli

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...
# or
apex config --key sk-ant-...

# Start interactive mode
apex

# One-shot mode
apex "what's wrong with this code?"

# With a file
apex "review my main function" --cwd /path/to/project
```

### Python SDK

```bash
pip install apex-pred-ai

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Interactive
apex-pred

# One-shot
apex-pred "explain this stack trace"

# Use as a library
python -c "
import asyncio
from apex_pred import ApexPredAgent, get_config
agent = ApexPredAgent(get_config())
asyncio.run(agent.stream_chat('hello'))
"
```

---

## Features

### Tools Apex-Pred Can Use

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

### Personality

Apex-Pred is configured with a system prompt that makes it:
- **Funny** — actually funny, not corporate-funny
- **Direct** — no "Certainly!" or "Great question!" preambles
- **Honest** — will tell you when your code sucks (and fix it)
- **Colorful** — swears naturally when appropriate
- **Autonomous** — uses tools aggressively to just get shit done

### Slash Commands (Interactive Mode)

```
/help     — show all commands
/tools    — list available tools
/config   — view current configuration
/clear    — clear conversation history
/session  — show session info (tokens used, message count)
/exit     — quit
```

---

## Configuration

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required
APEX_MODEL=claude-sonnet-4-6    # Optional: model override
APEX_MAX_TOKENS=8096            # Optional: max tokens
APEX_DEBUG=true                 # Optional: debug logging
```

### CLI Config Command

```bash
# TypeScript CLI
apex config --key sk-ant-...
apex config --model claude-opus-4-8
apex config --show

# Python CLI
apex-pred config --key sk-ant-...
apex-pred config --show
```

Config is stored at:
- **TypeScript**: `~/.config/apex-pred-ai/config.json` (platform-specific)
- **Python**: `~/.config/apex-pred-ai/config.json`

---

## Development

### Prerequisites

- Node.js >= 18
- Python >= 3.10
- An Anthropic API key

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/apex-pred-ai.git
cd apex-pred-ai

# TypeScript CLI
npm install
npm run build -w packages/cli
node packages/cli/dist/index.js

# Python SDK
cd packages/python-sdk
pip install -e ".[dev]"
apex-pred
```

### Project Structure

```
apex-pred-ai/
├── packages/
│   ├── cli/                    # TypeScript CLI (primary)
│   │   └── src/
│   │       ├── index.ts        # Entry point + CLI commands
│   │       ├── cli.ts          # Interactive REPL
│   │       ├── agent.ts        # Agent loop with streaming
│   │       ├── personality.ts  # System prompt
│   │       ├── config.ts       # Configuration management
│   │       ├── session.ts      # Conversation history
│   │       ├── tools/          # Tool implementations
│   │       └── ui/             # Terminal rendering
│   └── python-sdk/             # Python SDK + CLI
│       └── apex_pred/
│           ├── agent.py        # Agent with streaming
│           ├── cli.py          # Typer CLI
│           ├── personality.py  # System prompt
│           ├── config.py       # Config management
│           ├── session.py      # Session management
│           └── tools/          # Tool implementations
├── .github/workflows/          # CI + Release automation
└── README.md
```

### Running Tests

```bash
# Python
cd packages/python-sdk
pytest tests/ -v

# TypeScript
cd packages/cli
npm run typecheck
```

---

## Models

Apex-Pred works with any Anthropic Claude model. Defaults to `claude-sonnet-4-6`.

| Model | Speed | Intelligence | Best For |
|-------|-------|-------------|----------|
| `claude-haiku-4-5-20251001` | Fastest | Good | Quick tasks |
| `claude-sonnet-4-6` | Fast | Great | Default — best balance |
| `claude-opus-4-8` | Slower | Best | Complex reasoning |

```bash
apex --model claude-opus-4-8 "architect a distributed system for me"
```

---

## License

MIT — do whatever you want with it.

---

*Built with Claude by Anthropic. Apex-Pred is not affiliated with Anthropic.*
