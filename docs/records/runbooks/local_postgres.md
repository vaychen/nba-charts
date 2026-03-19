# Local PostgreSQL runbook

## Purpose

Use this runbook when you want to run the repo against a local Postgres instance instead of relying only on sample files.

## Environment file

Create a local `.env` in the repo root and keep it untracked.

```dotenv
NBA_CHARTS_DB_HOST=localhost
NBA_CHARTS_DB_PORT=5432
NBA_CHARTS_DB_NAME=nba_charts
NBA_CHARTS_DB_USER=postgres
NBA_CHARTS_DB_PASSWORD=your-local-password
```

You can also use a single DSN instead:

```dotenv
NBA_CHARTS_DB_DSN=dbname=nba_charts user=postgres password=your-local-password host=localhost port=5432
```

## Database bootstrap

1. create the database `nba_charts`
2. connect to `nba_charts`
3. create the `stats` schema
4. run the table DDL for players and teams

Example `psql` flow:

```bash
psql -h localhost -p 5432 -U postgres -d postgres -c "CREATE DATABASE nba_charts;"
psql -h localhost -p 5432 -U postgres -d nba_charts -c "CREATE SCHEMA IF NOT EXISTS stats;"
psql -h localhost -p 5432 -U postgres -d nba_charts -f src/nba_charts/db/sql/ddl/players.sql
psql -h localhost -p 5432 -U postgres -d nba_charts -f src/nba_charts/db/sql/ddl/teams.sql
```

## Reference-data sync commands

```bash
make sync-players
make sync-teams
make sync-all
```

## Verification

```bash
psql -h localhost -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.players;"
psql -h localhost -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.teams;"
```

## Notes

- the current Kobe POC still reads from `data/sample/kobe_career_shoot_made.csv`
- the database layer is the planned home for future multi-API ingest and reusable report datasets
- keep secrets local; do not commit `.env`
