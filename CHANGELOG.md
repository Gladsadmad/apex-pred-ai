# Changelog

All notable changes to Apex-Pred AI will be documented here.

## [1.0.1] - 2026-08-05

### Fixed
- `read_file` (both SDKs) silently returned lines from the **end** of a file when
  `start_line` was `0` or negative — the out-of-range value became a negative
  slice index. Ranges are now clamped, and a `start_line` past EOF is an error.
- `read_file` (TypeScript) counted a file's trailing newline as an extra line,
  reporting "of 5" for a 4-line file and emitting a phantom blank last line.
- `edit_file` (TypeScript) corrupted files when `new_string` contained `$&`,
  `` $` ``, `$'` or `$1`: `String.replace` expanded them as replacement patterns
  instead of inserting them literally. Editing shell, regex, or template code
  could silently write content the caller never asked for.

### Added
- Test suite for the TypeScript CLI's file tools (15 tests, `node:test`, no new
  dependencies), wired into CI and the release gate. The `$&` bug above existed
  because this package had no tests.

### Changed
- The version is now declared once per package. The Python SDK reads it from its
  installed distribution metadata (`apex_pred._version`), and the CLI reads it
  from `package.json` — no more hardcoded copies in `__init__.py`, the welcome
  banner, or the CLI's fallback, which had already drifted apart.

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
