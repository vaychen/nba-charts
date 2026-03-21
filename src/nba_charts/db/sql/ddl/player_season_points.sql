CREATE TABLE IF NOT EXISTS analytics.player_season_points (
    season_id VARCHAR(7) NOT NULL,
    season_start_year INT NOT NULL,
    player_id INT NOT NULL,
    player_name VARCHAR(256) NOT NULL,
    team_id BIGINT,
    team_abbreviation VARCHAR(16),
    gp INT NOT NULL,
    pts INT NOT NULL,
    season_points_rank INT NOT NULL,
    source_endpoint VARCHAR(128) NOT NULL DEFAULT 'LeagueLeaders',
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (season_id, player_id)
);

CREATE INDEX IF NOT EXISTS idx_player_season_points_start_year
    ON analytics.player_season_points (season_start_year);

CREATE INDEX IF NOT EXISTS idx_player_season_points_player
    ON analytics.player_season_points (player_id);

CREATE INDEX IF NOT EXISTS idx_player_season_points_rank
    ON analytics.player_season_points (season_id, season_points_rank);
