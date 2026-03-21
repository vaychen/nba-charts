INSERT INTO analytics.player_career_points_frames (
    season_id,
    season_start_year,
    player_id,
    player_name,
    team_abbreviation,
    season_points,
    career_points,
    season_points_rank,
    career_points_rank
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (season_id, player_id)
DO UPDATE SET
    season_start_year = EXCLUDED.season_start_year,
    player_name = EXCLUDED.player_name,
    team_abbreviation = EXCLUDED.team_abbreviation,
    season_points = EXCLUDED.season_points,
    career_points = EXCLUDED.career_points,
    season_points_rank = EXCLUDED.season_points_rank,
    career_points_rank = EXCLUDED.career_points_rank,
    updated_at = CURRENT_TIMESTAMP;
