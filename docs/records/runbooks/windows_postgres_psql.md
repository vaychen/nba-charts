# Windows PostgreSQL with psql

## Goal

Use installed PostgreSQL plus `psql` from PowerShell as the Windows local database workflow for this repo.

## Install PostgreSQL

- download PostgreSQL for Windows from `https://www.enterprisedb.com/downloads/postgres-postgresql-downloads`
- keep the PostgreSQL server and command line tools selected during install
- you do not need `pgAdmin` for this repo

Suggested installer choices:

- port: `5432`
- username: `postgres`
- password: your local password

## Verify psql in PowerShell

Open a new PowerShell window and run:

```powershell
psql --version
```

If `psql` is not on `PATH`, run it directly:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" --version
```

## Repo setup

```powershell
Copy-Item .env.example .env
uv python install 3.13
uv sync --all-groups
uv run nba-charts-db prepare-kobe-backend
uv run nba-charts-kobe-shot-poc
```

## Verification

```powershell
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.players;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.teams;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM analytics.kobe_shots;"
```
