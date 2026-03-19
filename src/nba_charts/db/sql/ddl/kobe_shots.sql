CREATE TABLE IF NOT EXISTS analytics.kobe_shots (
    shot_id INT PRIMARY KEY,
    action_type TEXT NOT NULL,
    combined_shot_type TEXT NOT NULL,
    game_event_id INT NOT NULL,
    game_id BIGINT NOT NULL,
    lat DOUBLE PRECISION,
    loc_x INT,
    loc_y INT,
    lon DOUBLE PRECISION,
    minutes_remaining SMALLINT,
    period SMALLINT,
    playoffs SMALLINT NOT NULL,
    season VARCHAR(7) NOT NULL,
    seconds_remaining SMALLINT,
    shot_distance SMALLINT,
    shot_made_flag SMALLINT,
    shot_type TEXT NOT NULL,
    shot_zone_area TEXT,
    shot_zone_basic TEXT,
    shot_zone_range TEXT,
    team_id BIGINT NOT NULL,
    team_name TEXT NOT NULL,
    game_date DATE,
    matchup TEXT,
    opponent TEXT,
    source_name TEXT NOT NULL DEFAULT 'kobe_career_shoot_made.csv',
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kobe_shots_season ON analytics.kobe_shots (season);
CREATE INDEX IF NOT EXISTS idx_kobe_shots_game_date ON analytics.kobe_shots (game_date);
CREATE INDEX IF NOT EXISTS idx_kobe_shots_playoffs ON analytics.kobe_shots (playoffs);
CREATE INDEX IF NOT EXISTS idx_kobe_shots_flag ON analytics.kobe_shots (shot_made_flag);
