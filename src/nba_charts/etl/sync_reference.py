import argparse
import logging
from collections.abc import Sequence
from typing import Any

from nba_api.stats.library.data import players as player_rows
from nba_api.stats.static import teams

from nba_charts.etl.db import get_connection, load_sql_query

LOGGER = logging.getLogger(__name__)


def sync_players() -> None:
    sql = load_sql_query("dml/players.sql")
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(sql, player_rows)
        connection.commit()
    LOGGER.info("Synced %s players", len(player_rows))


def sync_teams() -> None:
    sql = load_sql_query("dml/teams.sql")
    team_rows = [
        (
            team["id"],
            team["full_name"],
            team["abbreviation"],
            team["nickname"],
            team["city"],
            team["state"],
            team["year_founded"],
        )
        for team in teams.get_teams()
    ]
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.executemany(sql, team_rows)
        connection.commit()
    LOGGER.info("Synced %s teams", len(team_rows))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sync NBA reference data into PostgreSQL.")
    parser.add_argument("resource", choices=["players", "teams", "all"])
    return parser


def sync_all() -> None:
    sync_players()
    sync_teams()


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = build_parser().parse_args(argv)

    actions: dict[str, Any] = {
        "players": sync_players,
        "teams": sync_teams,
        "all": sync_all,
    }
    actions[args.resource]()


if __name__ == "__main__":
    main()
