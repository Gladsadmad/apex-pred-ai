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
- GitHub Actions CI matrix (Ubuntu / Windows / macOS, Node 18/20/22, Python 3.10–3.13)
- Automated npm + PyPI publish on version tags, with tag/manifest version checks,
  npm provenance, and both distributions attached to the GitHub release
- Packaging CI job that builds both distributions, installs them, and runs the binaries
- Per-package `README.md` + `LICENSE` so the npm and PyPI project pages render
- Library entry point for the npm package (`dist/lib.js`) separate from the CLI entry
- PEP 561 `py.typed` marker so the Python SDK ships its type hints
- `apex-pred --version` and an explicit `apex-pred chat` command
- Sharp personality — humor, natural language, brutal honesty

### Fixed
- Python CLI crashed with `UnicodeEncodeError` on consoles that can't encode
  ✓/✗ (legacy Windows cp1252, C-locale Unix) — unencodable glyphs now degrade
  to `?` instead of dying
- `apex-pred config` was unreachable — the one-shot message argument on the Typer
  callback swallowed subcommand names, so `config` was parsed as a chat message
- npm package declared no `license` and pointed `main` at the self-executing CLI
- Python wheel shipped an empty long description (declared README did not exist)
- ESLint (32 errors), ruff (14), and mypy strict (3) failures across both packages

### Security
- Windows bash tool uses `-EncodedCommand` Base64 UTF-16LE (prevents shell injection)
- Git tool uses `execFile` / `create_subprocess_exec` — no shell interpolation
- Dangerous command blocklist (regex, word-boundary matched)
- Subprocess killed on timeout (no zombie processes)
