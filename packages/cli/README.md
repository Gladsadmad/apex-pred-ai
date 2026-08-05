# @apex-pred/cli

> The apex predator of AI assistants. A Claude Code-style terminal AI with personality, tools, and absolutely no corporate bullshit.

[![npm version](https://img.shields.io/npm/v/@apex-pred/cli.svg)](https://www.npmjs.com/package/@apex-pred/cli)
[![CI](https://github.com/Gladsadmad/apex-pred-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Gladsadmad/apex-pred-ai/actions/workflows/ci.yml)

Apex-Pred AI is a terminal-based coding assistant powered by Claude. It reads and edits your files, runs shell commands and git operations, searches the web, and tells you the truth about your code.

This is the TypeScript CLI. A [Python SDK](https://pypi.org/project/apex-pred-ai/) with the same tools is also available.

---

## Install

```bash
npm install -g @apex-pred/cli
```

Requires Node.js >= 18.

## Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or persist it
apex config --key sk-ant-...
```

Grab a key at [console.anthropic.com](https://console.anthropic.com).

## Use it

```bash
# Interactive REPL
apex

# One-shot
apex "what's wrong with this regex?"

# Pick a model
apex --model claude-opus-4-8 "architect a job queue for me"

# Skip streaming
apex --no-stream "summarize this repo"
```

The binary is installed as both `apex` and `apex-pred`.

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
apex [message...]              Start interactive mode, or send a one-shot message

  -k, --key <key>              Anthropic API key (overrides env/config)
  -m, --model <model>          Model to use (default: claude-sonnet-4-6)
  -t, --max-tokens <tokens>    Max tokens per response
      --no-stream              Disable streaming output
      --debug                  Enable debug logging
  -v, --version                Show version

apex config                    View or update configuration

  -k, --key <key>              Set Anthropic API key
  -m, --model <model>          Set default model
  -t, --max-tokens <tokens>    Set max tokens per response
      --enable-stream          Enable streaming by default
      --disable-stream         Disable streaming by default
      --enable-debug           Enable debug mode
      --disable-debug          Disable debug mode
      --show                   Show current config and exit
```

## Configuration

### Environment variables

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required
APEX_MODEL=claude-sonnet-4-6    # Optional: model override
APEX_MAX_TOKENS=8096            # Optional: max tokens
APEX_DEBUG=true                 # Optional: debug logging
```

Config is persisted to a platform-specific path — run `apex config --show` to see where.

---

## Use as a library

```ts
import { ApexPredAgent, getConfig } from '@apex-pred/cli';

const agent = new ApexPredAgent(getConfig());
await agent.chat('explain this stack trace');
```

---

## Links

- [Repository](https://github.com/Gladsadmad/apex-pred-ai)
- [Issues](https://github.com/Gladsadmad/apex-pred-ai/issues)
- [Changelog](https://github.com/Gladsadmad/apex-pred-ai/blob/master/CHANGELOG.md)

## License

MIT — do whatever you want with it.

*Built with Claude by Anthropic. Apex-Pred is not affiliated with Anthropic.*
