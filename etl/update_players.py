import logging

import psycopg2
from nba_api.stats.library.data import players


# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="nba_charts",
        user="postgres",  # replace this with your actual username
        password="postgres",  # use secure password management in production
        host="localhost",
        port="5432",
    )


# Main function
def main():
    conn = get_db_connection()

    # SQL query for batch insert
    query = """
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
    """

    with conn.cursor() as cur:
        try:
            cur.executemany(query=query, vars_list=players)
        except Exception:
            logging.error("Error inserting/updating player data", exc_info=True)
        conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
