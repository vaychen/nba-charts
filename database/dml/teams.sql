INSERT INTO stats.teams (id, full_name, abbreviation, nickname, city, state, year_founded)
VALUES
    (%s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id)
DO UPDATE SET
    full_name = EXCLUDED.full_name,
    abbreviation = EXCLUDED.abbreviation,
    nickname = EXCLUDED.nickname,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    year_founded = EXCLUDED.year_founded,
    updated_at = CURRENT_TIMESTAMP;
