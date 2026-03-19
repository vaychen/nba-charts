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

## Launch PostgreSQL on Windows

PostgreSQL on Windows usually runs as a Windows service after installation.

Check the installed PostgreSQL service:

```powershell
Get-Service | Where-Object {$_.Name -like "postgresql*"}
```

If you want to search by display name instead:

```powershell
Get-Service | Where-Object {$_.DisplayName -like "*PostgreSQL*"}
```

Start the service with the exact service name returned above. A common example is:

```powershell
Start-Service postgresql-x64-18
```

Check the service status:

```powershell
Get-Service postgresql-x64-18
```

Useful service commands:

```powershell
Start-Service postgresql-x64-18
Stop-Service postgresql-x64-18
Restart-Service postgresql-x64-18
```

Once the service is running, verify the server connection with `psql`:

```powershell
psql -h 127.0.0.1 -p 5432 -U postgres -d postgres
```

## Verify psql in PowerShell

Open a new PowerShell window and run:

```powershell
psql --version
```

If `psql` is not on `PATH`, run it directly:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" --version
```

If `psql` is not on `PATH`, you can also use the full executable path for connections:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h 127.0.0.1 -p 5432 -U postgres -d postgres
```

## Repo setup

```powershell
Copy-Item .env.example .env
uv python install 3.13
uv sync --all-groups
uv run nba-charts-db prepare-kobe-backend
uv run nba-charts-kobe-shot-poc
```

After PostgreSQL is running, you can prepare the repo database at any time with:

```powershell
uv run nba-charts-db prepare-kobe-backend
```

## Verification

```powershell
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.players;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM stats.teams;"
psql -h 127.0.0.1 -p 5432 -U postgres -d nba_charts -c "SELECT COUNT(*) FROM analytics.kobe_shots;"
```
