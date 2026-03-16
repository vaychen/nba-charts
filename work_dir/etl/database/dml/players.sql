INSERT INTO stats.players (player_index_id, player_index_last_name, player_index_first_name, player_index_full_name, player_index_is_active)
VALUES
   (%s, %s, %s, %s, %s)
ON CONFLICT (player_index_id)
DO UPDATE SET
    player_index_last_name = EXCLUDED.player_index_last_name,
    player_index_first_name = EXCLUDED.player_index_first_name,
    player_index_full_name = EXCLUDED.player_index_full_name,
    player_index_is_active = EXCLUDED.player_index_is_active,
    updated_at = CURRENT_TIMESTAMP
;