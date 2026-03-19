# Dynamic report tools

## What kind of tool you need

Time-based reports usually need four things:

- a timeline or season index
- a playback control such as play, pause, or scrub
- smooth state changes between frames
- a data model that is already shaped into ordered snapshots

## Tool options

### Dash + Plotly

- best fit for a Python-first repo
- fast to prototype and easy to keep close to ETL code
- good for sliders, callbacks, filters, and locally hosted demos
- recommended for the current MVP because the repo is already Python-centric

### ECharts

- strong animation support and very good timeline interactions
- better than most BI tools when you want custom motion and layout freedom
- a strong next step if the project later needs a custom frontend

### D3.js

- highest control over animation and storytelling
- best for premium custom visual narratives
- most expensive option in implementation time and maintenance

### Power BI and Tableau

- best for governance, business-user sharing, and scheduled refresh workflows
- good for dashboards, weaker for custom motion-heavy layouts with avatars and bespoke transitions
- useful if the final audience mainly consumes reports inside a BI platform

## Recommended stack for this repo

### Short term

- FastAPI for reusable data endpoints
- Dash for the local dynamic report demo
- Dash + Plotly now also powers a Kobe shot-archive POC backed by `data/sample/kobe_career_shoot_made.csv`
- precomputed datasets under `data/processed/` later, sample data for now

### Long term

- keep FastAPI as the data service layer
- move to ECharts if the team wants more polished animation and custom web UI control
- only move to Power BI or Tableau if distribution and governance become more important than custom motion behavior

## Data requirements for animated reports

- one row per player per season or time step
- a stable ordering key for the timeline
- precomputed values to avoid slow live calculations during playback
- image URLs or asset keys if avatars should appear in the report

## Implementation notes in the refactor

- the local Dash app now includes play and pause controls
- the active season updates both a history chart and a season leaderboard
- the API exposes a sample `fg3m` report endpoint so a future frontend can consume the same data model
