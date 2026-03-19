# Cross-platform workflow

## Supported local environments

- macOS with Homebrew or direct Python installation
- Windows with PowerShell, Command Prompt, or Git Bash

The recommended workflow uses `uv` on both devices and optionally uses GNU Make as a shared command layer.

The repo pins Python in `.python-version`, so local `uv sync` and `uv run` commands resolve against the project target version after it is installed.

## First-time setup

```bash
uv python install 3.13
make setup
```

If `make` is not available yet, use the direct command:

```bash
uv python install 3.13
uv sync --all-groups
```

## Daily commands

| Task | Makefile | Direct command |
| --- | --- | --- |
| Install deps | `make setup` | `uv python install 3.13` then `uv sync --all-groups` |
| Run API | `make run-api` | `uv run nba-charts-api` |
| Run dashboard | `make run-dashboard` | `uv run nba-charts-dashboard` |
| Run Kobe shot POC | `make run-kobe-shot-poc` | `uv run nba-charts-kobe-shot-poc` |
| Check | `make check` | `uv run ruff check src tests scripts` then `uv run pytest` |
| Lint | `make lint` | `uv run ruff check src tests scripts` then `uv run mypy src` |
| Test | `make test` | `uv run pytest` |
| Sync players | `make sync-players` | `uv run nba-charts-sync players` |
| Sync teams | `make sync-teams` | `uv run nba-charts-sync teams` |
| Sync all | `make sync-all` | `uv run nba-charts-sync all` |
| Clean artifacts | `make clean` | `uv run python scripts/clean.py` |

## Why the Makefile stays simple

- it only calls `uv` or `python`
- it does not depend on shell pipes or Unix utilities
- it avoids path separators that differ between macOS and Windows

## Device sync advice

- keep `.env` local and untracked on both devices
- commit `pyproject.toml` and `uv.lock` together after dependency changes
- use Python `3.13` on both machines to reduce lockfile churn
- prefer sample or precomputed datasets in git instead of machine-local raw extracts
