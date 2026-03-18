# Refactor plan

## Goals

- remove stale prototype files and generated artifacts
- consolidate the repo into one Python package with clear API, UI, and ETL layers
- keep the local workflow consistent across macOS and Windows
- preserve a Makefile-based developer entry point without relying on Unix-only commands

## Problems in the old layout

- `app/`, `frontend/`, and `work_dir/` split related code across three top-level trees
- tracked `.DS_Store` and `__pycache__` files added noise to git history
- the project declared libraries that were no longer used and missed some libraries that were required by the code
- environment-sensitive values, especially database settings, were hardcoded in scripts
- the old Makefile only handled environment setup and did not cover the actual app lifecycle

## Target structure

```text
src/nba_charts/
  api/
  ui/
  services/
  etl/
  db/sql/
data/sample/
docs/
scripts/
tests/
```

## What changed

- `app/main.py` moved into `src/nba_charts/api/main.py`
- `app/services/nba.py` moved into `src/nba_charts/services/nba.py`
- the Dash MVP became the primary local dynamic report in `src/nba_charts/ui/dash_app.py`
- ETL scripts and SQL assets moved out of `work_dir/` into `src/nba_charts/etl` and `src/nba_charts/db/sql`
- sample report data moved into `data/sample/`
- project settings now come from `.env` through `src/nba_charts/settings.py`

## Cleanup decisions

- delete old generated files: `.DS_Store`, `__pycache__`, `*.pyc`
- delete duplicate UI paths that were not part of the chosen runtime architecture
- remove `work_dir/` as a catch-all scratch space and replace it with named package modules
- keep `doc/design_overview.png` until the image assets are reorganized separately

## Cross-platform decisions

- use `uv` for dependency and script execution on both devices
- keep Makefile commands simple and shell-neutral so they work with GNU Make on macOS and Windows
- avoid `rm`, `cp`, `mkdir -p`, shell pipes, and platform-specific path assumptions inside Make targets
- use `pathlib` everywhere for file paths in Python code
- use `psycopg[binary]` to reduce PostgreSQL setup friction on Windows

## Rollout phases

### Phase 1

- stabilize package layout
- add shared settings and local sample data access
- add Makefile commands for setup, run, lint, test, and ETL

### Phase 2

- replace sample data with precomputed season-level NBA extracts
- add database migration tooling if ETL becomes part of the main flow
- add richer dashboard states, export, and avatar rendering improvements

### Phase 3

- split UI from API if a custom frontend is needed later
- add CI that runs `make check` on both macOS and Windows runners
