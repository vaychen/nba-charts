CREATE TABLE IF NOT EXISTS analytics.player_career_points_frames (
    season_id VARCHAR(7) NOT NULL,
    season_start_year INT NOT NULL,
    player_id INT NOT NULL,
    player_name VARCHAR(256) NOT NULL,
    team_abbreviation VARCHAR(16),
    season_points INT NOT NULL,
    career_points INT NOT NULL,
    season_points_rank INT NOT NULL,
    career_points_rank INT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (season_id, player_id)
);

CREATE INDEX IF NOT EXISTS idx_player_career_points_frames_season
    ON analytics.player_career_points_frames (season_start_year);

CREATE INDEX IF NOT EXISTS idx_player_career_points_frames_rank
    ON analytics.player_career_points_frames (season_id, career_points_rank);

CREATE INDEX IF NOT EXISTS idx_player_career_points_frames_player
    ON analytics.player_career_points_frames (player_id);
