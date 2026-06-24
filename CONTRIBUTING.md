# Contributing to Apex-Pred AI

Thanks for wanting to contribute. Here's how to not waste either of our time.

## Setup

```bash
git clone https://github.com/Gladsadmad/apex-pred-ai.git
cd apex-pred-ai

# TypeScript CLI
npm install
npm run build -w packages/cli

# Python SDK
cd packages/python-sdk
pip install -e ".[dev]"
```

## Before You Submit

**TypeScript:**
```bash
cd packages/cli
npm run typecheck   # must pass — zero TS errors
npm run lint        # fix any ESLint warnings
npm run build       # confirm it compiles
```

**Python:**
```bash
cd packages/python-sdk
pytest tests/ -v    # all tests must pass
ruff check apex_pred/
```

## Pull Requests

- One feature or fix per PR
- Include tests for new tools or behaviors
- Don't break the personality — Apex-Pred should stay direct and sharp
- Security changes (tools, subprocess, config) get extra scrutiny

## Adding a Tool

1. TypeScript: add to `packages/cli/src/tools/` and register in `packages/cli/src/tools/index.ts`
2. Python: add to `packages/python-sdk/apex_pred/tools/` and add spec to `packages/python-sdk/apex_pred/tools/__init__.py`
3. Match signatures in both implementations
4. Add tests

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include your OS, Node/Python version, and a minimal reproduction.
