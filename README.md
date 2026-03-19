# nba-charts

Cross-platform NBA analytics tooling for APIs, ETL jobs, and dynamic chart demos.

## What is in the repo

- `src/nba_charts/api` - FastAPI service for local report data and shot chart endpoints.
- `src/nba_charts/ui` - Dash-based dynamic report demo for season playback.
- `src/nba_charts/etl` - reference-data sync scripts for players and teams.
- `data/sample` - sample data used for local development and tests.
- `data/sample/kobe_career_shoot_made.csv` - Kobe career shot sample used by the first tool-option POC.
- `docs` - architecture notes, runbooks, and change records.


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

The repo tracks the target interpreter in `.python-version`, and the Makefile stays thin by letting `uv` use that project setting. If `make` is not available yet on Windows, use the direct `uv` commands in `docs/records/runbooks/cross_platform_workflow.md`.

## Common commands

```bash
make run-api
make run-dashboard
make run-kobe-shot-poc
make prepare-kobe-backend
make lint
make test
make sync-all
```

The Kobe POC runs on `http://127.0.0.1:8051` by default. With `NBA_CHARTS_KOBE_DATA_SOURCE=auto` or `postgres`, it can read from the local Postgres backend after `make prepare-kobe-backend`, which now also fills `stats.players` and `stats.teams` from `nba_api`.

## Environment configuration

Copy `.env.example` to `.env` and adjust values when you need database-backed ETL runs or Postgres-backed Kobe reports.

Important variables:

- `NBA_CHARTS_API_HOST`
- `NBA_CHARTS_API_PORT`
- `NBA_CHARTS_DASH_HOST`
- `NBA_CHARTS_DASH_PORT`
- `NBA_CHARTS_DASH_INTERVAL_MS`
- `NBA_CHARTS_DB_DSN`
- `NBA_CHARTS_DB_HOST`
- `NBA_CHARTS_DB_PORT`
- `NBA_CHARTS_DB_NAME`
- `NBA_CHARTS_DB_ADMIN_NAME`
- `NBA_CHARTS_DB_USER`
- `NBA_CHARTS_DB_PASSWORD`
- `NBA_CHARTS_DB_CONNECT_TIMEOUT_SECONDS`
- `NBA_CHARTS_KOBE_DATA_SOURCE`

## Docs

- `docs/README.md`
- `docs/design/system_architecture.md`
- `docs/design/backend_data_architecture.md`
- `docs/design/dynamic_reports.md`
- `docs/design/kobe_shot_poc.md`
- `docs/records/runbooks/cross_platform_workflow.md`
- `docs/records/runbooks/local_postgres.md`
- `docs/records/changes/repo_refactor.md`
