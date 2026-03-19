# Local PostgreSQL runbook

## Purpose

Use this runbook when you want to run the repo against a local Postgres instance instead of relying only on sample files.

## Environment file

Copy `.env.example` to `.env` in the repo root and keep it untracked.

```dotenv
NBA_CHARTS_DB_HOST=127.0.0.1
NBA_CHARTS_DB_PORT=5432
NBA_CHARTS_DB_NAME=nba_charts
NBA_CHARTS_DB_ADMIN_NAME=postgres
NBA_CHARTS_DB_USER=postgres
NBA_CHARTS_DB_PASSWORD=123456789
NBA_CHARTS_DB_CONNECT_TIMEOUT_SECONDS=10
NBA_CHARTS_KOBE_DATA_SOURCE=auto
```

You can also use a single DSN instead:

```dotenv
NBA_CHARTS_DB_DSN=dbname=nba_charts user=postgres password=123456789 host=127.0.0.1 port=5432
```

## Database bootstrap

The repo now includes a bootstrap command that creates the target database if needed and applies the DDL for `stats.*` and `analytics.kobe_shots`.

```bash
make db-bootstrap
```

Direct command:

```bash
uv run nba-charts-db bootstrap
```

## Load the Kobe sample into Postgres

```bash
make load-kobe-shots
```

Direct command:

```bash
uv run nba-charts-db load-kobe-shots
```

If you want the one-shot setup for the Kobe dashboard backend, this command now bootstraps the DB, syncs `stats.players` and `stats.teams` from `nba_api`, and loads the Kobe sample into `analytics.kobe_shots`:

```bash
make prepare-kobe-backend
```

Direct command:

```bash
uv run nba-charts-db prepare-kobe-backend
```

## Manual fallback

1. create the database `nba_charts`
2. connect to `nba_charts`
3. create the `stats` and `analytics` schemas
4. run the table DDL for players, teams, and Kobe shots

Example `psql` flow:

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres -c "CREATE DATABASE nba_charts;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -f src/nba_charts/db/sql/ddl/database.sql
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -f src/nba_charts/db/sql/ddl/players.sql
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -f src/nba_charts/db/sql/ddl/teams.sql
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -f src/nba_charts/db/sql/ddl/kobe_shots.sql
```

## Reference-data sync commands

```bash
make sync-players
make sync-teams
make sync-all
```

## Verification

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.players;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.teams;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM analytics.kobe_shots;"
```

## Notes

- the Kobe POC and `/api/reports/kobe-shot-poc` now support the Postgres backend
- `make prepare-kobe-backend` now also populates `stats.players` and `stats.teams`
- in `auto` mode, the app falls back to the sample file if Postgres is unavailable or empty
- `.env` can stay local even though `.env.example` now includes the shared local password value
