CREATE TABLE IF NOT EXISTS stats.teams (
    id BIGINT PRIMARY KEY,
    full_name VARCHAR(256) NOT NULL,
    abbreviation VARCHAR(256),
    nickname VARCHAR(256),
    city VARCHAR(256),
    state VARCHAR(256),
    year_founded INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
