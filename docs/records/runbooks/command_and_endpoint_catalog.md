# Command and endpoint catalog

## Make targets

| Target | Description |
| --- | --- |
| `make help` | Print the available Make targets. |
| `make setup` | Install the pinned Python version with `uv` and sync all dependency groups. |
| `make lock` | Refresh `uv.lock` from the current dependency definitions. |
| `make format` | Run Ruff format across `src`, `tests`, and `scripts`. |
| `make lint` | Run Ruff plus mypy checks. |
| `make test` | Run the pytest suite. |
| `make check` | Run Ruff and pytest together for a quick quality gate. |
| `make run-api` | Start the FastAPI server. |
| `make run-dashboard` | Start the original Dash dynamic dashboard. |
| `make run-kobe-shot-poc` | Start the Dash Kobe shot POC. |
| `make db-bootstrap` | Create the target database if needed and apply DDL. |
| `make load-kobe-shots` | Load the Kobe sample CSV into `analytics.kobe_shots`. |
| `make prepare-kobe-backend` | Bootstrap the DB, sync players and teams, and load the Kobe backend. |
| `make load-career-points-race` | Fetch season scoring leaders from `nba_api` and load the career-points race tables. |
| `make prepare-career-points-race` | Bootstrap the DB, sync players and teams, and build the career-points race backend. |
| `make sync-players` | Sync `stats.players` from official NBA static reference data. |
| `make sync-teams` | Sync `stats.teams` from official NBA static reference data. |
| `make sync-all` | Sync both players and teams. |
| `make clean` | Remove common local generated artifacts. |

## API routes

### Service and UI routes

| Route | Description |
| --- | --- |
| `GET /` | Basic API banner response. |
| `GET /health` | Health-check endpoint for local validation. |
| `GET /echarts/kobe-shot-poc` | Serve the Kobe shot ECharts page. |
| `GET /echarts/career-points-race` | Serve the career-points bar-race ECharts page. |

### Report data routes

| Route | Description |
| --- | --- |
| `GET /api/reports/fg3m` | Return the sample three-point makes report with season filtering and leaderboard output. |
| `GET /api/reports/kobe-shot-poc` | Return Kobe shot-map data, summaries, and filters for Dash or ECharts clients. |
| `GET /api/reports/career-points-race` | Return precomputed season frames for the ECharts career-points bar race. |

### Shot-chart routes

| Route | Description |
| --- | --- |
| `GET /api/shot-chart` | Fetch live shot-chart records for a player and season from `nba_api`. |
| `GET /api/shot-chart/image` | Render a static shot-chart PNG for a player and season. |

## Notes

- the ECharts pages are browser routes served by FastAPI, while the data comes from `/api/reports/...`
- database-backed report routes depend on local Postgres setup and ETL preparation commands
- the command list in this doc should stay in sync with `Makefile` and `src/nba_charts/api/main.py`
