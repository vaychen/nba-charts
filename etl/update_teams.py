import logging
from pathlib import Path
import psycopg2
from nba_api.stats.static import teams


# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="nba_charts",
        user="postgres",  # Replace with your username
        password="postgres",  # Replace with your password
        host="localhost",
        port="5432"
    )


# Main function
def main():
    conn = get_db_connection()

    # SQL query for batch insert
    sql_file_path = Path(__file__).parent.parent / "database" / "dml" / "teams.sql"
    with open(sql_file_path, "r") as file:
        query = file.read()

    with conn.cursor() as cur:
        try:
            teams_data = teams.get_teams()
            # Convert list of dictionaries to list of tuples
            values_list = [tuple(team.values()) for team in teams_data]

            cur.executemany(query=query, vars_list=values_list)
        except Exception:
            logging.error("Error inserting/updating team data", exc_info=True)
        conn.commit()

    conn.close()


# Main function
if __name__ == "__main__":
    main()
