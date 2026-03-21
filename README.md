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
- PostgreSQL locally - recommended: `Postgres.app` on macOS, installed PostgreSQL with `psql` on Windows
- `make` if you want the shared Makefile workflow on both devices

For local database work, `psql` is the recommended shared inspection tool across both platforms.

Bootstrap the project:

```bash
uv python install 3.13
make setup
```

For the local env file:

- macOS or Linux: `cp .env.example .env`
- PowerShell: `Copy-Item .env.example .env`

The repo tracks the target interpreter in `.python-version`, and the Makefile stays thin by letting `uv` use that project setting. If `make` is not available yet on Windows, use the direct `uv` commands in `docs/records/runbooks/cross_platform_workflow.md`.

For the Windows PostgreSQL + PowerShell workflow, use `docs/records/runbooks/windows_postgres_psql.md`.

## Common commands

```bash
make run-api
make run-dashboard
make run-kobe-shot-poc
make prepare-kobe-backend
make prepare-career-points-race
make lint
make test
make sync-all
```

The Kobe POC runs on `http://127.0.0.1:8051` by default. With `NBA_CHARTS_KOBE_DATA_SOURCE=auto` or `postgres`, it can read from the local Postgres backend after `make prepare-kobe-backend`, which now also fills `stats.players` and `stats.teams` from `nba_api`.

The ECharts Kobe POC is served by the API at `http://127.0.0.1:8000/echarts/kobe-shot-poc` after `make run-api`.

The career points bar-race report is served by the API at `http://127.0.0.1:8000/echarts/career-points-race` after `make prepare-career-points-race` and `make run-api`.

GitHub Actions now runs lint, type checks, and tests on both macOS and Windows in `.github/workflows/ci.yml`.

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
- `NBA_CHARTS_NBA_API_TIMEOUT_SECONDS`
- `NBA_CHARTS_NBA_API_VERIFY_SSL`
- `NBA_CHARTS_KOBE_DATA_SOURCE`

## Docs

- `docs/README.md`
- `docs/design/system_architecture.md`
- `docs/design/backend_data_architecture.md`
- `docs/design/career_points_bar_race.md`
- `docs/design/dynamic_reports.md`
- `docs/design/kobe_shot_poc.md`
- `docs/records/runbooks/cross_platform_workflow.md`
- `docs/records/runbooks/local_postgres.md`
- `docs/records/runbooks/windows_postgres_psql.md`
- `docs/records/changes/repo_refactor.md`
