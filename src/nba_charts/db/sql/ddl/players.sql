CREATE TABLE IF NOT EXISTS stats.players (
    player_index_id INT PRIMARY KEY,
    player_index_last_name VARCHAR(256) NOT NULL,
    player_index_first_name VARCHAR(256),
    player_index_full_name VARCHAR(256),
    player_index_is_active BOOLEAN,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
