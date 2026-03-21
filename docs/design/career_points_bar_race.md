# Career points bar race

## Goal

Build a dynamic report that ranks NBA players by accumulated regular-season career points at the end of each season, then animates those standings in an ECharts bar-race view.

## Source and coverage

- source: official `nba_api` stats endpoints
- primary endpoint: `LeagueLeaders` with `stat_category_abbreviation=PTS`, `per_mode48=Totals`, and `season_type_all_star=Regular Season`
- first season with stable league-wide coverage from this endpoint: `1958-59`

The product goal says "start from the first date of NBA," but the official league-wide `nba_api` feed does not return complete leaderboard rows for the earliest BAA and NBA seasons. This implementation therefore starts from the first season the official league feed returns consistently.

## Data flow

```mermaid
flowchart LR
    nba[nba_api LeagueLeaders per season] --> etl[ETL loader]
    etl --> season[analytics.player_season_points]
    season --> transform[career accumulation transform]
    transform --> frames[analytics.player_career_points_frames]
    frames --> api[/api/reports/career-points-race/]
    api --> echarts[/echarts/career-points-race/]
```

## Storage plan

### `analytics.player_season_points`

One row per player per season from the NBA API season-total feed.

Core fields:

- `season_id`
- `season_start_year`
- `player_id`
- `player_name`
- `team_id`
- `team_abbreviation`
- `gp`
- `pts`
- `season_points_rank`
- source metadata and timestamps

### `analytics.player_career_points_frames`

One row per player per season after cumulative career scoring is calculated.

Core fields:

- `season_id`
- `season_start_year`
- `player_id`
- `player_name`
- `team_abbreviation`
- `season_points`
- `career_points`
- `season_points_rank`
- `career_points_rank`
- timestamps

This table is already shaped for animated report playback.

## API shape

`/api/reports/career-points-race`

Response fields:

- `seasons`
- `frames` with one frame per season
- `top_n`
- `backend_source`
- optional `highlight_player_id`

Each frame should include:

- `season`
- `leaders`
  - `player_id`
  - `player_name`
  - `team_abbreviation`
  - `season_points`
  - `career_points`
  - `career_points_rank`

## Frontend plan

- serve a dedicated ECharts page from FastAPI
- use a bar-race pattern similar to the referenced ECharts country-ranking example
- animate one season at a time using precomputed frames from PostgreSQL
- allow at least:
  - play and pause
  - season scrub
  - top-N limit
  - optional player highlight

## ETL plan

1. bootstrap DB schemas if needed
2. sync `stats.players` and `stats.teams`
3. fetch one season at a time from `nba_api`
4. upsert into `analytics.player_season_points`
5. rebuild `analytics.player_career_points_frames`

## Notes and tradeoffs

- using the season leaderboard endpoint keeps API calls manageable because it is one request per season, not one request per player
- cumulative values are stored in Postgres so the report can animate quickly without recalculating during every API call
- if later coverage of pre-1958 seasons becomes mandatory, the project will need a different historical source or a much heavier player-by-player backfill process
