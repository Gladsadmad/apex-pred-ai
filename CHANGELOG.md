# Changelog

All notable changes to Apex-Pred AI will be documented here.

## [1.0.0] - 2026-06-24

### Added
- TypeScript CLI (`@apex-pred/cli`) — interactive REPL + one-shot mode
- Python SDK (`apex-pred-ai`) — full async agent + Typer CLI
- 9 built-in tools: `read_file`, `write_file`, `edit_file`, `list_files`, `delete_file`, `bash`, `git`, `web_fetch`, `web_search`
- Streaming responses via Anthropic SDK
- Persistent config (`~/.config/apex-pred-ai/config.json`)
- Session history with JSON save/load
- Slash commands: `/help`, `/tools`, `/config`, `/clear`, `/session`, `/exit`
- GitHub Actions CI matrix (Ubuntu / Windows / macOS, Node 18+20, Python 3.10–3.12)
- Automated npm + PyPI publish on version tags
- Sharp personality — humor, natural language, brutal honesty

### Security
- Windows bash tool uses `-EncodedCommand` Base64 UTF-16LE (prevents shell injection)
- Git tool uses `execFile` / `create_subprocess_exec` — no shell interpolation
- Dangerous command blocklist (regex, word-boundary matched)
- Subprocess killed on timeout (no zombie processes)
