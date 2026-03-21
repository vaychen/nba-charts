INSERT INTO analytics.player_season_points (
    season_id,
    season_start_year,
    player_id,
    player_name,
    team_id,
    team_abbreviation,
    gp,
    pts,
    season_points_rank,
    source_endpoint
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (season_id, player_id)
DO UPDATE SET
    season_start_year = EXCLUDED.season_start_year,
    player_name = EXCLUDED.player_name,
    team_id = EXCLUDED.team_id,
    team_abbreviation = EXCLUDED.team_abbreviation,
    gp = EXCLUDED.gp,
    pts = EXCLUDED.pts,
    season_points_rank = EXCLUDED.season_points_rank,
    source_endpoint = EXCLUDED.source_endpoint,
    updated_at = CURRENT_TIMESTAMP;
