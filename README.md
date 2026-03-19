# nba-charts

Cross-platform NBA analytics tooling for APIs, ETL jobs, and dynamic chart demos.

## What is in the repo

- `src/nba_charts/api` - FastAPI service for local report data and shot chart endpoints.
- `src/nba_charts/ui` - Dash-based dynamic report demo for season playback.
- `src/nba_charts/etl` - reference-data sync scripts for players and teams.
- `data/sample` - sample data used for local development and tests.
- `docs` - refactor plan, dynamic report architecture, and device workflow notes.


## Local setup

Requirements:

- Python version pinned in `.python-version` (`3.13`)
- `uv` - install guide: https://docs.astral.sh/uv/
- `make` if you want the shared Makefile workflow on both devices

Bootstrap the project:

```bash
uv python install 3.13
make setup
```

The repo tracks the target interpreter in `.python-version`, and the Makefile stays thin by letting `uv` use that project setting. If `make` is not available yet on Windows, use the direct `uv` commands in `docs/cross_platform_workflow.md`.

## Common commands

```bash
make run-api
make run-dashboard
make lint
make test
make sync-all
```

## Environment configuration

Copy `.env.example` to `.env` and adjust values when you need database-backed ETL runs.

Important variables:

- `NBA_CHARTS_API_HOST`
- `NBA_CHARTS_API_PORT`
- `NBA_CHARTS_DASH_HOST`
- `NBA_CHARTS_DASH_PORT`
- `NBA_CHARTS_DB_DSN`

## Docs

- `docs/refactor_plan.md`
- `docs/dynamic_reports.md`
- `docs/cross_platform_workflow.md`
