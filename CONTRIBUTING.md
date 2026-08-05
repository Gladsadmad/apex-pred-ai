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
npm test            # all tests must pass
npm run build       # confirm it compiles
```

**Python:**
```bash
cd packages/python-sdk
pytest tests/ -v              # all tests must pass
ruff check apex_pred/ tests/  # zero errors
mypy apex_pred/               # strict mode, zero errors
```

CI runs exactly these on Node 18/20/22 and Python 3.10–3.13 across Linux, Windows,
and macOS, plus a packaging job that builds both distributions, installs them, and
runs the binaries.

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

## Releasing

Releases are driven entirely by tags. Pushing `vX.Y.Z` publishes `@apex-pred/cli`
to npm, `apex-pred-ai` to PyPI, and creates a GitHub release with both
distributions attached.

1. Bump the version in **both** manifests — they must match the tag or the
   release workflow fails fast:
   - `packages/cli/package.json`
   - `packages/python-sdk/pyproject.toml`
2. Update `CHANGELOG.md`.
3. Tag and push:
   ```bash
   git tag v1.0.1
   git push origin v1.0.1
   ```

### One-time publishing setup

| What | Where | Notes |
|------|-------|-------|
| `NPM_TOKEN` | Settings → Secrets and variables → Actions | An npm **automation** token with publish rights to the `@apex-pred` scope. Required. |
| PyPI auth | PyPI project settings, or `PYPI_API_TOKEN` secret | Prefer a [trusted publisher](https://docs.pypi.org/trusted-publishers/) for `Gladsadmad/apex-pred-ai` with workflow `release.yml`. If the `PYPI_API_TOKEN` secret exists, the workflow uses it instead. |

npm publishes with `--provenance`, which needs the repository to stay public.

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include your OS, Node/Python version, and a minimal reproduction.
