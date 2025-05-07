import logging

import psycopg2
from pathlib import Path
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
    sql_file_path = Path(__file__).parent.parent / "database" / "dml" / "players.sql"
    with open(sql_file_path, "r") as file:
        query = file.read()

    with conn.cursor() as cur:
        try:
            cur.executemany(query=query, vars_list=players)
        except Exception:
            logging.error("Error inserting/updating player data", exc_info=True)
        conn.commit()

    conn.close()


if __name__ == "__main__":
    main()
